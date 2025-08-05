from django.urls import path
from . import api_views

urlpatterns = [
    path('files/', api_views.FileListCreateAPIView.as_view(), name='api_files'),
    path('files/<str:filename>/', api_views.FileDetailAPIView.as_view(), name='api_file_detail'),
    path('health/', api_views.health_check, name='health'),
]
