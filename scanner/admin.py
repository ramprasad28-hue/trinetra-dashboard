"""
Django Admin Configuration for TRINETRA
Register and configure models for admin interface
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import ScanResult, ScanHistory, PortService, UserScanStatistics


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    """
    ✅ Custom admin interface for ScanResult
    - List display with formatted columns
    - Search and filtering
    - Read-only fields
    - Custom actions
    """
    
    list_display = (
        'id',
        'target',
        'user',
        'status_badge',
        'open_ports_count',
        'risk_level_badge',
        'created_at',
        'scan_duration_display'
    )
    
    list_filter = (
        'status',
        'created_at',
        'user',
        ('open_ports_count', admin.RelatedFieldListFilter),
    )
    
    search_fields = (
        'target',
        'user__username',
        'error_message',
    )
    
    readonly_fields = (
        'user',
        'created_at',
        'started_at',
        'completed_at',
        'result',
        'parsed_results',
        'open_ports_count',
        'closed_ports_count',
        'filtered_ports_count',
        'scan_duration',
        'risk_level'
    )
    
    fieldsets = (
        ('Scan Information', {
            'fields': ('user', 'target', 'status', 'port_range')
        }),
        ('Timing', {
            'fields': ('created_at', 'started_at', 'completed_at', 'scan_duration')
        }),
        ('Results', {
            'fields': (
                'result',
                'parsed_results',
                'open_ports_count',
                'closed_ports_count',
                'filtered_ports_count',
                'risk_level'
            ),
            'classes': ('collapse',)
        }),
        ('Error Handling', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'delete_scan']
    
    ordering = ('-created_at',)
    
    def status_badge(self, obj):
        """✅ Display status with color badge"""
        colors = {
            'pending': '#FFA500',
            'scanning': '#3498DB',
            'completed': '#27AE60',
            'failed': '#E74C3C'
        }
        color = colors.get(obj.status, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def risk_level_badge(self, obj):
        """✅ Display risk level with color badge"""
        colors = {
            'LOW': '#27AE60',
            'MEDIUM': '#F39C12',
            'HIGH': '#E74C3C',
            'CRITICAL': '#8B0000'
        }
        color = colors.get(obj.risk_level, '#95A5A6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.risk_level
        )
    risk_level_badge.short_description = 'Risk Level'
    
    def scan_duration_display(self, obj):
        """✅ Display scan duration in human-readable format"""
        if obj.scan_duration:
            return f'{obj.scan_duration:.2f}s'
        return '-'
    scan_duration_display.short_description = 'Duration'
    
    def mark_as_completed(self, request, queryset):
        """✅ Action to mark scans as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} scans marked as completed.')
    mark_as_completed.short_description = 'Mark selected scans as completed'
    
    def mark_as_failed(self, request, queryset):
        """✅ Action to mark scans as failed"""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} scans marked as failed.')
    mark_as_failed.short_description = 'Mark selected scans as failed'
    
    def delete_scan(self, request, queryset):
        """✅ Action to delete scans"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} scans deleted.')
    delete_scan.short_description = 'Delete selected scans'


@admin.register(ScanHistory)
class ScanHistoryAdmin(admin.ModelAdmin):
    """
    ✅ Admin interface for ScanHistory
    """
    
    list_display = (
        'user',
        'total_scans',
        'total_open_ports',
        'last_scan',
        'updated_at'
    )
    
    list_filter = ('updated_at', 'user')
    
    search_fields = ('user__username',)
    
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Statistics', {
            'fields': (
                'total_scans',
                'total_open_ports',
                'last_scan',
                'updated_at'
            )
        })
    )


@admin.register(PortService)
class PortServiceAdmin(admin.ModelAdmin):
    """
    ✅ Admin interface for PortService
    - Manage common port-to-service mappings
    """
    
    list_display = (
        'port',
        'service_name',
        'protocol',
        'common_vulnerability'
    )
    
    list_filter = (
        'protocol',
        ('port', admin.RelatedFieldListFilter),
    )
    
    search_fields = (
        'port',
        'service_name',
        'description',
        'common_vulnerability'
    )
    
    fieldsets = (
        ('Port Information', {
            'fields': ('port', 'protocol', 'service_name')
        }),
        ('Details', {
            'fields': ('description', 'common_vulnerability')
        })
    )
    
    ordering = ('port',)


@admin.register(UserScanStatistics)
class UserScanStatisticsAdmin(admin.ModelAdmin):
    """
    ✅ Admin interface for UserScanStatistics
    - View user scanning statistics
    """
    
    list_display = (
        'user',
        'total_scans',
        'total_open_ports',
        'average_scan_time_display',
        'last_scan_date'
    )
    
    list_filter = (
        'created_at',
        'updated_at',
    )
    
    search_fields = ('user__username',)
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'total_scans',
        'total_open_ports',
        'average_scan_time',
        'last_scan_date'
    )
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Statistics', {
            'fields': (
                'total_scans',
                'total_open_ports',
                'average_scan_time',
                'last_scan_date'
            ),
            'classes': ('readonly',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def average_scan_time_display(self, obj):
        """Display average scan time in seconds"""
        return f'{obj.average_scan_time:.2f}s'
    average_scan_time_display.short_description = 'Avg Scan Time'


# ✅ Customize Django Admin Site
admin.site.site_header = 'TRINETRA Admin Panel'
admin.site.site_title = 'TRINETRA Scanner'
admin.site.index_title = 'Welcome to TRINETRA Administration'
