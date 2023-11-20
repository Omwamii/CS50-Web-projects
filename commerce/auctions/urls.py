from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.show_categories, name="categories"),
    path("watchlist", views.show_watchlist, name="watchlist"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:listing_id>/", views.goto_listing, name="listing"),
    path("category/<str:name>/", views.goto_category, name="category")
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
