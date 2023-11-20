from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:name>", views.get_wiki, name="get_wiki"),
    path("search/", views.search, name="search"),
    path("new/", views.create_page, name="create_page"),
    path("edit/<str:page_title>/", views.edit_page, name="edit_page"),
    path("random/", views.random_page, name="random_page")
]
