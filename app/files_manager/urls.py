from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('files/', views.files_page, name='files'),
]
