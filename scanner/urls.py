"""
URL routing for TRINETRA Scanner app
"""
from django.urls import path
from .views import (
    scan_view, 
    history_view, 
    signup_view, 
    login_view, 
    logout_view,
    scan_detail_view,
    delete_scan_view,
    profile_view
)

urlpatterns = [
    # Authentication
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Scanning
    path('', scan_view, name='scan'),
    path('scan/<int:scan_id>/', scan_detail_view, name='scan_detail'),
    path('scan/<int:scan_id>/delete/', delete_scan_view, name='delete_scan'),
    
    # History & Profile
    path('history/', history_view, name='history'),
    path('profile/', profile_view, name='profile'),
]
