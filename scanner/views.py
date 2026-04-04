"""
Improved Views for TRINETRA Scanner
Includes error handling, validation, logging, and proper form usage
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction

from .models import ScanResult, UserScanStatistics
from .forms import TrintraUserCreationForm, TrintraLoginForm, TrinetraScanForm
from .utils import NmapScanner, InputValidator, RiskAnalyzer

logger = logging.getLogger('scanner')


# ✅ SIGNUP VIEW
@require_http_methods(['GET', 'POST'])
def signup_view(request):
    """
    ✅ User signup with proper form validation
    - Prevents duplicate usernames
    - Password confirmation
    - Email validation
    """
    if request.user.is_authenticated:
        return redirect('scan')
    
    if request.method == 'POST':
        form = TrintraUserCreationForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                
                # Create user statistics
                UserScanStatistics.objects.create(user=user)
                
                logger.info(f'New user registered: {user.username}')
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('login')
            
            except Exception as e:
                logger.error(f'Error creating user: {str(e)}')
                messages.error(request, 'An error occurred during signup. Please try again.')
        
        else:
            # Form has errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    else:
        form = TrintraUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})


# ✅ LOGIN VIEW
@require_http_methods(['GET', 'POST'])
def login_view(request):
    """
    ✅ User login with proper authentication
    - Error messages for failed attempts
    - Redirect to next page
    """
    if request.user.is_authenticated:
        return redirect('scan')
    
    if request.method == 'POST':
        form = TrintraLoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                logger.info(f'User logged in: {username}')
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect to next page or scan
                next_page = request.GET.get('next', 'scan')
                return redirect(next_page)
            
            else:
                logger.warning(f'Failed login attempt for username: {username}')
                messages.error(request, 'Invalid username or password.')
    
    else:
        form = TrintraLoginForm()
    
    return render(request, 'login.html', {'form': form})


# ✅ LOGOUT VIEW
@login_required(login_url='login')
@require_http_methods(['POST'])
def logout_view(request):
    """
    ✅ User logout
    - Log the action
    - Redirect to login
    """
    username = request.user.username
    logout(request)
    logger.info(f'User logged out: {username}')
    messages.success(request, 'You have been logged out.')
    return redirect('/login/')


# ✅ SCAN VIEW (Main scanning functionality)
@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def scan_view(request):
    """
    ✅ Network scanning with:
    - Form validation
    - Error handling
    - Nmap integration
    - Result parsing
    - Risk analysis
    """
    if request.method == 'POST':
        form = TrinetraScanForm(request.POST)
        
        if form.is_valid():
            try:
                target = form.cleaned_data.get('target')
                port_range = form.cleaned_data.get('port_range')
                
                # ✅ Validate target
                is_valid, error_msg = InputValidator.validate_target(target)
                if not is_valid:
                    messages.error(request, f'Invalid target: {error_msg}')
                    return render(request, 'scan.html', {'form': form})
                
                logger.info(f'Scan initiated by {request.user.username} for target: {target}')
                
                # Create scan record with pending status
                scan_result = ScanResult.objects.create(
                    user=request.user,
                    target=target,
                    port_range=port_range,
                    status='scanning'
                )
                
                # ✅ Run Nmap scan
                scanner = NmapScanner()
                scan_data = scanner.scan(target, port_range)
                
                if not scan_data['success']:
                    # Scan failed
                    scan_result.status = 'failed'
                    scan_result.error_message = scan_data['error']
                    scan_result.result = f'Scan Error: {scan_data["error"]}'
                    scan_result.save()
                    
                    logger.error(f'Scan failed for {target}: {scan_data["error"]}')
                    messages.error(request, f'Scan failed: {scan_data["error"]}')
                    return render(request, 'scan.html', {'form': form})
                
                # Parse results
                parsed = scan_data['parsed_result']
                formatted_output = scanner.get_formatted_output(parsed)
                
                # ✅ Update scan record with results
                scan_result.status = 'completed'
                scan_result.result = formatted_output
                scan_result.parsed_results = parsed
                
                # Update port counts
                summary = parsed.get('summary', {})
                scan_result.open_ports_count = summary.get('total_open', 0)
                scan_result.closed_ports_count = summary.get('total_closed', 0)
                scan_result.filtered_ports_count = summary.get('total_filtered', 0)
                
                scan_result.save()
                
                # ✅ Analyze risks
                risks = RiskAnalyzer.analyze(parsed)
                
                logger.info(
                    f'Scan completed for {target}: '
                    f'{scan_result.open_ports_count} open ports'
                )
                
                # Update user statistics
                try:
                    stats = request.user.scan_statistics
                    stats.update_stats()
                except UserScanStatistics.DoesNotExist:
                    UserScanStatistics.objects.create(user=request.user)
                
                messages.success(
                    request,
                    f'Scan completed! Found {scan_result.open_ports_count} open ports.'
                )
                
                return render(request, 'result.html', {
                    'scan': scan_result,
                    'risks': risks,
                    'result': formatted_output
                })
            
            except Exception as e:
                logger.error(f'Unexpected error during scan: {str(e)}', exc_info=True)
                messages.error(request, 'An unexpected error occurred. Please try again.')
                return render(request, 'scan.html', {'form': form})
        
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    
    else:
        form = TrinetraScanForm()
    
    return render(request, 'scan.html', {'form': form})


# ✅ SCAN HISTORY VIEW (With pagination)
@login_required(login_url='login')
def history_view(request):
    """
    ✅ Display user's scan history with:
    - Pagination
    - Filtering
    - Sorting
    """
    try:
        # Get all scans for current user
        scans = ScanResult.objects.filter(user=request.user).order_by('-created_at')
        
        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter:
            scans = scans.filter(status=status_filter)
        
        target_filter = request.GET.get('target')
        if target_filter:
            scans = scans.filter(target__icontains=target_filter)
        
        # Pagination
        paginator = Paginator(scans, 10)  # 10 scans per page
        page = request.GET.get('page', 1)
        
        try:
            scans = paginator.page(page)
        except PageNotAnInteger:
            scans = paginator.page(1)
        except EmptyPage:
            scans = paginator.page(paginator.num_pages)
        
        logger.info(f'User {request.user.username} viewed scan history (page {page})')
        
        return render(request, 'history.html', {
            'scans': scans,
            'status_choices': ScanResult.SCAN_STATUS_CHOICES,
            'total_scans': paginator.count
        })
    
    except Exception as e:
        logger.error(f'Error loading history: {str(e)}')
        messages.error(request, 'An error occurred while loading history.')
        return redirect('scan')


# ✅ SCAN DETAIL VIEW (View specific scan results)
@login_required(login_url='login')
def scan_detail_view(request, scan_id):
    """
    ✅ Display detailed scan results
    - Ensure user can only view their own scans
    - Display formatted results
    - Show risk analysis
    """
    try:
        scan = get_object_or_404(ScanResult, id=scan_id, user=request.user)
        
        risks = {}
        if scan.parsed_results:
            risks = RiskAnalyzer.analyze(scan.parsed_results)
        
        logger.info(f'User {request.user.username} viewed scan {scan_id}')
        
        return render(request, 'scan_detail.html', {
            'scan': scan,
            'risks': risks
        })
    
    except Exception as e:
        logger.error(f'Error loading scan detail: {str(e)}')
        messages.error(request, 'An error occurred while loading scan details.')
        return redirect('history')


# ✅ DELETE SCAN VIEW
@login_required(login_url='login')
@require_http_methods(['POST'])
def delete_scan_view(request, scan_id):
    """
    ✅ Delete a scan (only user's own scans)
    """
    try:
        scan = get_object_or_404(ScanResult, id=scan_id, user=request.user)
        target = scan.target
        
        scan.delete()
        
        logger.info(f'User {request.user.username} deleted scan for {target}')
        messages.success(request, f'Scan for {target} deleted successfully.')
        
        return redirect('history')
    
    except Exception as e:
        logger.error(f'Error deleting scan: {str(e)}')
        messages.error(request, 'An error occurred while deleting the scan.')
        return redirect('history')


# ✅ USER PROFILE VIEW
@login_required(login_url='login')
def profile_view(request):
    """
    ✅ Display user profile and statistics
    """
    try:
        stats = request.user.scan_statistics
    except UserScanStatistics.DoesNotExist:
        stats = UserScanStatistics.objects.create(user=request.user)
    
    recent_scans = ScanResult.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-completed_at')[:5]
    
    return render(request, 'profile.html', {
        'stats': stats,
        'recent_scans': recent_scans
    })


# ✅ ERROR HANDLERS
def page_not_found_view(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def server_error_view(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)

