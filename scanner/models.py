"""
Enhanced Models for TRINETRA Scanner
Includes scan status tracking, timing, and open ports count
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class ScanResult(models.Model):
    """
    ✅ Enhanced scan result model with:
    - Status tracking (pending, completed, failed)
    - Scan timing information
    - Open ports count
    - Service information
    - Error logging
    """
    
    # Status choices
    SCAN_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scanning', 'Scanning'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    # Core fields
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scan_results',
        help_text='User who initiated the scan'
    )
    
    target = models.CharField(
        max_length=100,
        db_index=True,  # ✅ Index for fast queries
        help_text='Target IP, domain, or IP range'
    )
    
    # ✅ Status tracking
    status = models.CharField(
        max_length=20,
        choices=SCAN_STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Current scan status'
    )
    
    # ✅ Raw results from Nmap
    result = models.TextField(
        help_text='Raw Nmap output'
    )
    
    # ✅ Parsed results in JSON format for easier access
    parsed_results = models.JSONField(
        default=dict,
        blank=True,
        help_text='Structured scan results: {hosts: [{ip, ports: [{port, state, service}]}]}'
    )
    
    # ✅ Statistics
    open_ports_count = models.IntegerField(
        default=0,
        help_text='Number of open ports found'
    )
    
    closed_ports_count = models.IntegerField(
        default=0,
        help_text='Number of closed ports found'
    )
    
    filtered_ports_count = models.IntegerField(
        default=0,
        help_text='Number of filtered ports found'
    )
    
    # ✅ Timing information
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When the scan was initiated'
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the scan actually started'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the scan completed'
    )
    
    # ✅ Scan configuration
    port_range = models.CharField(
        max_length=50,
        default='1-1024',
        help_text='Port range that was scanned'
    )
    
    # ✅ Error handling
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text='Error message if scan failed'
    )
    
    # ✅ Additional info
    notes = models.TextField(
        blank=True,
        help_text='User notes about this scan'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['target']),
        ]
        verbose_name = 'Scan Result'
        verbose_name_plural = 'Scan Results'
    
    def __str__(self):
        return f'{self.target} - {self.get_status_display()} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'
    
    @property
    def scan_duration(self):
        """Calculate scan duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def total_ports_scanned(self):
        """Total number of ports scanned"""
        return self.open_ports_count + self.closed_ports_count + self.filtered_ports_count
    
    @property
    def risk_level(self):
        """
        ✅ Calculate risk level based on open ports
        Low: 0-3 open ports
        Medium: 4-10 open ports
        High: 11+ open ports
        """
        if self.open_ports_count >= 11:
            return 'HIGH'
        elif self.open_ports_count >= 4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def save(self, *args, **kwargs):
        """Override save to set started_at when status changes to 'scanning'"""
        if self.status == 'scanning' and not self.started_at:
            self.started_at = timezone.now()
        
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)


class ScanHistory(models.Model):
    """
    ✅ Additional model to track scan history metadata
    Useful for analytics and trending
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scan_history'
    )
    
    total_scans = models.IntegerField(default=0)
    total_open_ports = models.IntegerField(default=0)
    last_scan = models.ForeignKey(
        ScanResult,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Scan History'
    
    def __str__(self):
        return f'{self.user.username} - {self.total_scans} scans'


class PortService(models.Model):
    """
    ✅ Store common port-to-service mappings
    Helps identify services running on open ports
    """
    
    port = models.IntegerField(unique=True, db_index=True)
    service_name = models.CharField(max_length=100)
    protocol = models.CharField(max_length=10, default='tcp')
    description = models.TextField(blank=True)
    common_vulnerability = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['port']
        verbose_name = 'Port Service'
        verbose_name_plural = 'Port Services'
    
    def __str__(self):
        return f'Port {self.port} - {self.service_name}'


class UserScanStatistics(models.Model):
    """
    ✅ Track user scan statistics for insights
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='scan_statistics'
    )
    
    total_scans = models.IntegerField(default=0)
    total_open_ports = models.IntegerField(default=0)
    average_scan_time = models.FloatField(default=0)
    last_scan_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Scan Statistics'
        verbose_name_plural = 'User Scan Statistics'
    
    def __str__(self):
        return f'{self.user.username} statistics'
    
    def update_stats(self):
        """Update statistics based on recent scans"""
        scans = self.user.scan_results.filter(status='completed')
        
        self.total_scans = scans.count()
        self.total_open_ports = sum(s.open_ports_count for s in scans)
        
        completed_scans = scans.exclude(started_at__isnull=True).exclude(completed_at__isnull=True)
        if completed_scans.exists():
            durations = [s.scan_duration for s in completed_scans if s.scan_duration]
            if durations:
                self.average_scan_time = sum(durations) / len(durations)
        
        self.last_scan_date = scans.latest('completed_at').completed_at if scans.exists() else None
        self.save()
