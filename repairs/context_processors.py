from django.conf import settings


def company_contacts(request):
    return {
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "SITE_DOMAIN": settings.SITE_DOMAIN,
        "COMPANY_LEGAL_NAME": settings.COMPANY_LEGAL_NAME,
    }
