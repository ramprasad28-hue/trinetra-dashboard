from django.urls import path
from .views import history_view, scan_view

urlpatterns = [
    path('', scan_view, name='scan'),
    path('history/', history_view, name='history'),
]