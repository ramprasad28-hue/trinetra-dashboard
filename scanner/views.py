from django.shortcuts import render, redirect
from .models import ScanResult
import nmap

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


# 🔐 SIGNUP
def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, "signup.html")


# 🔑 LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('scan')

    return render(request, "login.html")


# 🚪 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')


# 🔍 SCAN (Protected)
def scan_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == "POST":
        target = request.POST.get('target')
        nm = nmap.PortScanner(
            nmap_search_path=(
                "C:\\Program Files (x86)\\Nmap\\nmap.exe",
                "C:\\Program Files\\Nmap\\nmap.exe",
            )
        )

        nm.scan(target, '1-1024')

        result = ""

        for host in nm.all_hosts():
            result += f"Host: {host}\n"
            for proto in nm[host].all_protocols():
                ports = nm[host][proto].keys()
                for port in ports:
                    state = nm[host][proto][port]['state']
                    result += f"Port {port}: {state}\n"

        ScanResult.objects.create(
            user=request.user,
            target=target,
            result=result
        )

        return render(request, "result.html", {"result": result})

    return render(request, "scan.html")


# 📜 HISTORY (User-specific)
def history_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    scans = ScanResult.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "history.html", {"scans": scans})