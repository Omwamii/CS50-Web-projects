from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("emails", csrf_exempt(views.compose), name="compose"),
    path("emails/<int:email_id>", views.email, name="email"),
    path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
    path("user", views.user, name="user"),
]
