from django.urls import path

from .views import UserRegistrationView, LogoutView, UserLoginView, profile_purpose, edit_profile_purpose, change_password, account_verify


app_name = 'accounts'

urlpatterns = [
    path(
        "login/", UserLoginView.as_view(),
        name="user_login"
    ),
    path(
        "logout/", LogoutView.as_view(),
        name="user_logout"
    ),
    path(
        "register/", UserRegistrationView.as_view(),
        name="user_registration"
    ),
    path(
        "profile/", profile_purpose,
        name="user_profile"
    ),
    path(
        "editprofile/", edit_profile_purpose,
        name="edit_profile"
    ),
    path(
        "changepass/", change_password,
        name="change_password"
    ),
    path(
        "verify/<slug:token>", account_verify,
        name="account_verify"
    ),


]
