from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auctions.urls'))
]

handler404 = 'auctions.views.custom_404'
