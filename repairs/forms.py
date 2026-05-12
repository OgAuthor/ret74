import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import RepairRequest, Status

User = get_user_model()


class ClientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Иван"}),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "mail@example.ru"}),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "password1", "password2"]
        labels = {
            "username": "Логин",
        }
        help_texts = {
            "username": "",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "ivan74"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Повторите пароль"
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""


class ClientLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class RepairRequestCreateForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    captcha_answer = forms.IntegerField(
        label="Антиспам",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ответ",
                "inputmode": "numeric",
            }
        ),
    )
    personal_data_consent = forms.BooleanField(
        label="Согласие на обработку персональных данных",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = RepairRequest
        fields = ["customer_name", "phone", "device", "problem_description"]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Иванов Иван Иванович"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+7 900 000-00-00"}),
            "device": forms.TextInput(attrs={"class": "form-control", "placeholder": "Телевизор, ноутбук, приставка..."}),
            "problem_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Опишите неисправность как можно подробнее",
                }
            ),
        }

    def __init__(self, *args, captcha_question="", captcha_answer=None, **kwargs):
        self.expected_captcha_answer = captcha_answer
        super().__init__(*args, **kwargs)
        if captcha_question:
            self.fields["captcha_answer"].label = f"Антиспам: {captcha_question}"

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        normalized = re.sub(r"[^\d+]", "", phone)
        if not re.fullmatch(r"\+?\d{10,15}", normalized):
            raise forms.ValidationError("Введите корректный номер телефона.")
        return phone

    def clean_website(self):
        website = self.cleaned_data.get("website", "")
        if website:
            raise forms.ValidationError("Заявку не удалось отправить.")
        return website

    def clean_captcha_answer(self):
        answer = self.cleaned_data["captcha_answer"]
        if self.expected_captcha_answer is None or answer != int(self.expected_captcha_answer):
            raise forms.ValidationError("Решите пример, чтобы отправить заявку.")
        return answer


class TrackingForm(forms.Form):
    code = forms.CharField(
        label="Код заявки",
        max_length=16,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "TM74-ABC123",
                "autocomplete": "off",
            }
        ),
    )

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()


class RepairRequestManagerForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ["customer_name", "phone", "device", "problem_description", "status"]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "device": forms.TextInput(attrs={"class": "form-control"}),
            "problem_description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
