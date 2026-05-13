from django.test import RequestFactory, TestCase

from .forms import RepairRequestCreateForm
from .models import RepairRequest, Status
from .views import filter_manager_requests


class RepairRequestSearchAndPhoneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.review = Status.objects.get(slug="review")

    def test_phone_is_formatted_before_save(self):
        form = RepairRequestCreateForm(
            data={
                "customer_name": "Иван Иванов",
                "phone": "89935443001",
                "device": "Телевизор",
                "problem_description": "Нет изображения",
                "captcha_answer": "7",
                "personal_data_consent": "on",
            },
            captcha_question="3 + 4 = ?",
            captcha_answer=7,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["phone"], "+7 (993) 544-30-01")

    def test_manager_search_matches_cyrillic_case_insensitively(self):
        RepairRequest.objects.create(
            customer_name="Иван Иванов",
            phone="+7 (993) 544-30-01",
            device="Телевизор",
            problem_description="Нет изображения",
            status=self.review,
        )
        request = RequestFactory().get("/manager/requests/", {"q": "иван"})

        results = filter_manager_requests(request)

        self.assertEqual(results.count(), 1)
