from django.shortcuts import render
from .models import ScanResult
import nmap

def scan_view(request):
    if request.method == "POST":
        target = request.POST.get("target")

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

        ScanResult.objects.create(target=target, result=result)

        return render(request, "result.html", {"result": result})

    return render(request, "scan.html")

def history_view(request):
    scans = ScanResult.objects.all().order_by('-created_at')
    return render(request, "history.html", {"scans": scans})