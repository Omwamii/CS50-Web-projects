
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create-post', views.create_post, name='create-post'),
    path('load-posts/<str:type_of_posts>', views.load_posts, name='load-posts'),
    path('get_user', views.get_user, name='get_user'),
    path('like-post/<int:postId>', views.like_post, name='like-post'),
    path('edit-post/<int:post_id>', views.edit_post, name='edit-post'),
    path('user-stats/<int:user_id>', views.get_user_stats, name='get_user_stats'),
    path('get-poster/<int:post_id>', views.get_poster, name='get_poster'),
    path('follow/<int:user_id>', views.follow, name='follow')
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)