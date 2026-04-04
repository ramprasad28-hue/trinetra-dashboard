"""
Django Forms for TRINETRA Scanner
Handles validation for user authentication and scanning
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from ipaddress import ip_address, AddressValueError


class TrintraUserCreationForm(UserCreationForm):
    """
    ✅ Enhanced user signup form with validation
    - Prevents duplicate usernames
    - Ensures password confirmation
    - Validates email format
    - Enforces strong passwords
    """
    
    email = forms.EmailField(
        required=True,
        help_text='A valid email address is required.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_username(self):
        """✅ Prevent duplicate usernames"""
        username = self.cleaned_data.get('username')
        
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists. Choose a different one.')
        
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.')
        
        # Allow only alphanumeric and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
        
        return username
    
    def clean_email(self):
        """✅ Prevent duplicate emails"""
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already registered. Use login or password reset.')
        
        return email
    
    def clean_password2(self):
        """✅ Ensure passwords match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        
        return password2


class TrintraLoginForm(forms.Form):
    """
    ✅ Custom login form with validation
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )
    
    def clean(self):
        """✅ Validate that username and password are provided"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if not username or not password:
            raise ValidationError('Username and password are required.')
        
        return cleaned_data


class TrinetraScanForm(forms.Form):
    """
    ✅ Scanner form with comprehensive target validation
    - Supports IPv4, IPv6, domains, and ranges
    - Prevents invalid input
    - Sanitizes user input
    """
    
    TARGET_CHOICES = (
        ('single', 'Single Target (IP or Domain)'),
        ('range', 'IP Range (192.168.1.0/24)'),
    )
    
    target = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 192.168.1.1 or example.com or 192.168.1.0/24',
            'required': True
        }),
        help_text='Enter a single IP, domain, or IP range'
    )
    
    scan_type = forms.ChoiceField(
        choices=TARGET_CHOICES,
        initial='single',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    port_range = forms.CharField(
        max_length=50,
        initial='1-1024',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1-1024 (or 1-65535 for all ports)',
            'required': True
        }),
        help_text='Specify port range (e.g., 1-1024 or 80,443,8080)'
    )
    
    def clean_target(self):
        """✅ Validate target (IP, domain, or range)"""
        target = self.cleaned_data.get('target').strip()
        
        if not target:
            raise ValidationError('Target cannot be empty.')
        
        if len(target) > 100:
            raise ValidationError('Target is too long (max 100 characters).')
        
        # Check if it's an IPv4 address
        if self._is_valid_ipv4(target):
            return target
        
        # Check if it's an IPv4 CIDR range
        if self._is_valid_cidr(target):
            return target
        
        # Check if it's a valid domain
        if self._is_valid_domain(target):
            return target
        
        raise ValidationError(
            'Invalid target. Enter a valid IPv4 address, domain, or CIDR range.'
        )
    
    def clean_port_range(self):
        """✅ Validate port range"""
        port_range = self.cleaned_data.get('port_range').strip()
        
        try:
            # Check format: "1-1024" or "80,443,8080"
            if '-' in port_range:
                parts = port_range.split('-')
                if len(parts) != 2:
                    raise ValidationError('Invalid port range format.')
                
                start, end = int(parts[0]), int(parts[1])
                
                if start < 1 or end > 65535:
                    raise ValidationError('Ports must be between 1 and 65535.')
                
                if start > end:
                    raise ValidationError('Start port must be less than end port.')
            
            elif ',' in port_range:
                ports = [int(p.strip()) for p in port_range.split(',')]
                for port in ports:
                    if port < 1 or port > 65535:
                        raise ValidationError('Ports must be between 1 and 65535.')
            
            else:
                port = int(port_range)
                if port < 1 or port > 65535:
                    raise ValidationError('Port must be between 1 and 65535.')
        
        except ValueError:
            raise ValidationError('Invalid port format. Use "1-1024" or "80,443,8080".')
        
        return port_range
    
    @staticmethod
    def _is_valid_ipv4(ip):
        """Check if string is a valid IPv4 address"""
        try:
            ip_address(ip)
            return True
        except AddressValueError:
            return False
    
    @staticmethod
    def _is_valid_cidr(cidr):
        """Check if string is a valid CIDR notation"""
        if '/' not in cidr:
            return False
        
        try:
            parts = cidr.split('/')
            if len(parts) != 2:
                return False
            
            ip_part = parts[0]
            prefix = int(parts[1])
            
            ip_address(ip_part)
            
            if prefix < 0 or prefix > 32:
                return False
            
            return True
        except (ValueError, AddressValueError):
            return False
    
    @staticmethod
    def _is_valid_domain(domain):
        """
        Check if string is a valid domain name
        Allows: example.com, sub.example.com, example.co.uk
        """
        # Regex for domain validation
        domain_regex = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        
        if re.match(domain_regex, domain):
            # Must have at least one dot
            if '.' in domain:
                return True
        
        return False
