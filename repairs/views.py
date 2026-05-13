import csv
from random import randint

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import ClientLoginForm, ClientRegistrationForm, RepairRequestCreateForm, RepairRequestManagerForm, TrackingForm
from .models import RepairRequest, Status
from .services import log_status_change, notify_managers_about_new_request


CAPTCHA_ANSWER_SESSION_KEY = "repair_request_captcha_answer"
CAPTCHA_QUESTION_SESSION_KEY = "repair_request_captcha_question"


def home(request):
    return render(request, "repairs/home.html")


def privacy_policy(request):
    return render(
        request,
        "repairs/privacy_policy.html",
        {
            "company_legal_name": settings.COMPANY_LEGAL_NAME,
            "contact_email": settings.CONTACT_EMAIL,
        },
    )


def refresh_request_captcha(request):
    left = randint(2, 9)
    right = randint(2, 9)
    request.session[CAPTCHA_QUESTION_SESSION_KEY] = f"{left} + {right} = ?"
    request.session[CAPTCHA_ANSWER_SESSION_KEY] = left + right


def get_request_captcha(request):
    if (
        CAPTCHA_QUESTION_SESSION_KEY not in request.session
        or CAPTCHA_ANSWER_SESSION_KEY not in request.session
    ):
        refresh_request_captcha(request)

    return (
        request.session[CAPTCHA_QUESTION_SESSION_KEY],
        request.session[CAPTCHA_ANSWER_SESSION_KEY],
    )


def create_request(request):
    initial_status = Status.objects.get(slug="review")
    captcha_question, captcha_answer = get_request_captcha(request)

    if request.method == "POST":
        form = RepairRequestCreateForm(
            request.POST,
            captcha_question=captcha_question,
            captcha_answer=captcha_answer,
        )
        if form.is_valid():
            repair_request = form.save(commit=False)
            if request.user.is_authenticated:
                repair_request.customer = request.user
            repair_request.status = initial_status
            repair_request.save()
            log_status_change(repair_request, comment="Заявка создана")
            notify_managers_about_new_request(repair_request, request)
            refresh_request_captcha(request)
            return render(
                request,
                "repairs/request_success.html",
                {"repair_request": repair_request},
            )
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["customer_name"] = request.user.get_full_name() or request.user.username
        form = RepairRequestCreateForm(
            initial=initial,
            captcha_question=captcha_question,
            captcha_answer=captcha_answer,
        )

    return render(request, "repairs/request_form.html", {"form": form})


def track_request(request):
    form = TrackingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"]
        return redirect("request_status", code=code)
    return render(request, "repairs/track_form.html", {"form": form})


def request_status(request, code):
    repair_request = get_object_or_404(RepairRequest.objects.select_related("status"), code=code.upper())
    status_history = repair_request.status_history.select_related("old_status", "new_status", "changed_by").order_by(
        "created_at",
        "id",
    )
    return render(
        request,
        "repairs/request_status.html",
        {"repair_request": repair_request, "status_history": status_history},
    )


def staff_required(user):
    return user.is_authenticated and user.is_staff


def register(request):
    if request.user.is_authenticated:
        return redirect("client_requests")

    if request.method == "POST":
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Аккаунт создан. Теперь заявки будут сохраняться в личном кабинете.")
            return redirect("client_requests")
    else:
        form = ClientRegistrationForm()

    return render(request, "repairs/register.html", {"form": form})


class ClientLoginView(LoginView):
    template_name = "repairs/login.html"
    authentication_form = ClientLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        if self.request.user.is_staff:
            return reverse_lazy("manager_requests")
        return reverse_lazy("client_requests")


class ClientLogoutView(LogoutView):
    next_page = reverse_lazy("home")


@login_required(login_url="login")
def client_requests(request):
    requests_qs = RepairRequest.objects.select_related("status").filter(customer=request.user)
    return render(request, "repairs/client_requests.html", {"requests_list": requests_qs})


@user_passes_test(staff_required, login_url="login")
def manager_requests(request):
    requests_qs = filter_manager_requests(request)
    statuses = Status.objects.all()
    return render(
        request,
        "repairs/manager_requests.html",
        {
            "requests_list": requests_qs,
            "statuses": statuses,
            "query": request.GET.get("q", "").strip(),
            "selected_status": request.GET.get("status", "").strip(),
            "export_querystring": request.GET.urlencode(),
        },
    )


def filter_manager_requests(request):
    requests_qs = RepairRequest.objects.select_related("status")
    query = request.GET.get("q", "").strip()
    status_slug = request.GET.get("status", "").strip()

    if status_slug:
        requests_qs = requests_qs.filter(status__slug=status_slug)

    if query:
        matched_ids = [
            item.pk
            for item in requests_qs
            if manager_request_matches_query(item, query)
        ]
        requests_qs = requests_qs.filter(pk__in=matched_ids)

    return requests_qs


def manager_request_matches_query(repair_request, query):
    normalized_query = query.casefold()
    query_digits = "".join(char for char in query if char.isdigit())
    fields = [
        repair_request.code,
        repair_request.customer_name,
        repair_request.phone,
        repair_request.device,
    ]

    if any(normalized_query in str(value).casefold() for value in fields):
        return True

    if query_digits:
        phone_digits = "".join(char for char in repair_request.phone if char.isdigit())
        return query_digits in phone_digits

    return False


@user_passes_test(staff_required, login_url="login")
def manager_requests_export(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="repair-requests.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow(
        [
            "Код",
            "Клиент",
            "Телефон",
            "Устройство",
            "Описание проблемы",
            "Статус",
            "Создана",
            "Обновлена",
        ]
    )
    for item in filter_manager_requests(request):
        writer.writerow(
            [
                item.code,
                item.customer_name,
                item.phone,
                item.device,
                item.problem_description,
                item.status.title,
                item.created_at.strftime("%d.%m.%Y %H:%M"),
                item.updated_at.strftime("%d.%m.%Y %H:%M"),
            ]
        )

    return response


@user_passes_test(staff_required, login_url="login")
def manager_request_edit(request, pk):
    repair_request = get_object_or_404(
        RepairRequest.objects.select_related("status").prefetch_related("status_history"),
        pk=pk,
    )
    if request.method == "POST":
        old_status = RepairRequest.objects.select_related("status").get(pk=repair_request.pk).status
        form = RepairRequestManagerForm(request.POST, instance=repair_request)
        if form.is_valid():
            updated_request = form.save()
            if old_status.pk != updated_request.status_id:
                log_status_change(
                    updated_request,
                    old_status=old_status,
                    changed_by=request.user,
                    comment="Статус изменен менеджером",
                )
            messages.success(request, "Заявка обновлена.")
            return redirect("manager_requests")
    else:
        form = RepairRequestManagerForm(instance=repair_request)

    status_history = repair_request.status_history.select_related("old_status", "new_status", "changed_by").order_by(
        "created_at",
        "id",
    )
    return render(
        request,
        "repairs/manager_request_edit.html",
        {"form": form, "repair_request": repair_request, "status_history": status_history},
    )


@user_passes_test(staff_required, login_url="login")
def manager_request_delete(request, pk):
    repair_request = get_object_or_404(RepairRequest, pk=pk)
    if request.method == "POST":
        code = repair_request.code
        repair_request.delete()
        messages.success(request, f"Заявка {code} удалена.")
        return redirect("manager_requests")
    return render(
        request,
        "repairs/manager_request_delete.html",
        {"repair_request": repair_request},
    )
