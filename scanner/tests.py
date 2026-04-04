"""
Tests for TRINETRA Scanner app
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ScanResult


class AuthenticationTests(TestCase):
    """Test user authentication"""
    
    def setUp(self):
        self.client = Client()
    
    def test_signup_page_loads(self):
        """Test signup page is accessible"""
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_loads(self):
        """Test login page is accessible"""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_user(self):
        """Test user creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.assertEqual(user.username, 'testuser')


class ScanTests(TestCase):
    """Test scanning functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.client = Client()
        self.client.login(username='testuser', password='TestPass123!')
    
    def test_scan_page_requires_login(self):
        """Test that scan page requires authentication"""
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
