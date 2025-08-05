import os
import logging
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def home(request):
    """Homepage view"""
    context = {
        'pod_name': os.environ.get('POD_NAME', 'unknown'),
        'node_name': os.environ.get('NODE_NAME', 'unknown'),
        'storage_path': settings.FILES_STORAGE_PATH,
    }
    return render(request, 'home.html', context)


def files_page(request):
    """Files management page"""
    context = {
        'pod_name': os.environ.get('POD_NAME', 'unknown'),
        'node_name': os.environ.get('NODE_NAME', 'unknown'),
        'storage_path': settings.FILES_STORAGE_PATH,
    }
    return render(request, 'files.html', context)
