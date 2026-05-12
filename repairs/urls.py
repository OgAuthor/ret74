from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("privacy/", views.privacy_policy, name="privacy_policy"),
    path("zayavka/", views.create_request, name="create_request"),
    path("otsledit/", views.track_request, name="track_request"),
    path("otsledit/<str:code>/", views.request_status, name="request_status"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.ClientLoginView.as_view(), name="login"),
    path("accounts/logout/", views.ClientLogoutView.as_view(), name="logout"),
    path("accounts/requests/", views.client_requests, name="client_requests"),
    path("manager/login/", views.ClientLoginView.as_view(), name="manager_login"),
    path("manager/logout/", views.ClientLogoutView.as_view(), name="manager_logout"),
    path("manager/requests/", views.manager_requests, name="manager_requests"),
    path("manager/requests/export.csv", views.manager_requests_export, name="manager_requests_export"),
    path("manager/requests/<int:pk>/edit/", views.manager_request_edit, name="manager_request_edit"),
    path("manager/requests/<int:pk>/delete/", views.manager_request_delete, name="manager_request_delete"),
]
