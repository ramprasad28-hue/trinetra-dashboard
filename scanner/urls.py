from django.urls import include, path

from scanner import admin
from .views import scan_view, history_view, signup_view, login_view, logout_view

urlpatterns = [
    path('', scan_view, name='scan'),
    path('history/', history_view, name='history'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]