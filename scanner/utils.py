"""
Utility functions for TRINETRA Scanner
Includes Nmap operations, input validation, and result parsing
"""

import logging
import nmap
import json
import re
from ipaddress import ip_address, IPv4Network, AddressValueError
from django.utils import timezone

logger = logging.getLogger('scanner')


class NmapScanner:
    """
    ✅ Wrapper class for Nmap operations
    - Cross-platform compatibility
    - Error handling
    - Result parsing
    - Logging
    """
    
    def __init__(self):
        """Initialize Nmap scanner"""
        try:
            self.nm = nmap.PortScanner()
            logger.info('Nmap scanner initialized successfully')
        except nmap.PortScannerError as e:
            logger.error(f'Failed to initialize Nmap: {str(e)}')
            raise Exception('Nmap is not installed. Please install: sudo apt-get install nmap')
    
    def scan(self, target, port_range='1-1024'):
        """
        ✅ Perform network scan with error handling
        
        Args:
            target (str): IP address, domain, or CIDR range
            port_range (str): Port range to scan (e.g., '1-1024')
        
        Returns:
            dict: Scan results with parsed data
        """
        try:
            logger.info(f'Starting scan for target: {target}, ports: {port_range}')
            
            # Perform scan
            self.nm.scan(target, port_range, '-sV')  # -sV for service detection
            
            logger.info(f'Scan completed for {target}')
            
            return {
                'success': True,
                'raw_result': self.nm.csv(),
                'parsed_result': self.parse_results(),
                'error': None
            }
        
        except nmap.PortScannerError as e:
            error_msg = f'Nmap scanning error: {str(e)}'
            logger.error(error_msg)
            return {
                'success': False,
                'raw_result': '',
                'parsed_result': {},
                'error': error_msg
            }
        
        except Exception as e:
            error_msg = f'Unexpected error during scan: {str(e)}'
            logger.error(error_msg)
            return {
                'success': False,
                'raw_result': '',
                'parsed_result': {},
                'error': error_msg
            }
    
    def parse_results(self):
        """
        ✅ Parse Nmap results into structured JSON format
        
        Returns:
            dict: Parsed results with host and port information
        """
        parsed = {
            'hosts': [],
            'summary': {
                'total_open': 0,
                'total_closed': 0,
                'total_filtered': 0
            }
        }
        
        try:
            for host in self.nm.all_hosts():
                host_info = {
                    'ip': host,
                    'hostname': self.nm[host].hostname(),
                    'status': self.nm[host].state(),
                    'protocols': {}
                }
                
                # Iterate through protocols (tcp, udp, etc.)
                for proto in self.nm[host].all_protocols():
                    host_info['protocols'][proto] = []
                    
                    # Iterate through ports
                    ports = self.nm[host][proto].keys()
                    for port in ports:
                        port_info = self.nm[host][proto][port]
                        state = port_info['state']
                        
                        port_data = {
                            'port': port,
                            'state': state,
                            'service': port_info.get('name', 'unknown'),
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', '')
                        }
                        
                        host_info['protocols'][proto].append(port_data)
                        
                        # Update counters
                        if state == 'open':
                            parsed['summary']['total_open'] += 1
                        elif state == 'closed':
                            parsed['summary']['total_closed'] += 1
                        elif state == 'filtered':
                            parsed['summary']['total_filtered'] += 1
                
                parsed['hosts'].append(host_info)
            
            logger.info(f'Parsed results: {parsed["summary"]["total_open"]} open ports found')
            return parsed
        
        except Exception as e:
            logger.error(f'Error parsing Nmap results: {str(e)}')
            return parsed
    
    def get_formatted_output(self, parsed_result):
        """
        ✅ Create human-readable formatted output
        
        Args:
            parsed_result (dict): Parsed scan results
        
        Returns:
            str: Formatted text output
        """
        output = []
        output.append('=' * 80)
        output.append('NETWORK SCAN RESULTS')
        output.append('=' * 80)
        output.append('')
        
        for host in parsed_result.get('hosts', []):
            output.append(f"Host: {host['ip']}")
            if host['hostname']:
                output.append(f"Hostname: {host['hostname']}")
            output.append(f"Status: {host['status']}")
            output.append('-' * 80)
            
            for proto, ports in host['protocols'].items():
                output.append(f"\n{proto.upper()} Ports:")
                output.append(f"{'Port':<10} {'State':<12} {'Service':<20} {'Product/Version':<30}")
                output.append('-' * 80)
                
                for port in ports:
                    product_info = port['product']
                    if port['version']:
                        product_info += f" {port['version']}"
                    
                    output.append(
                        f"{port['port']:<10} {port['state']:<12} "
                        f"{port['service']:<20} {product_info:<30}"
                    )
                
                output.append('')
            
            output.append('=' * 80)
            output.append('')
        
        # Summary
        summary = parsed_result.get('summary', {})
        output.append('SUMMARY')
        output.append('-' * 80)
        output.append(f"Open Ports: {summary.get('total_open', 0)}")
        output.append(f"Closed Ports: {summary.get('total_closed', 0)}")
        output.append(f"Filtered Ports: {summary.get('total_filtered', 0)}")
        output.append('=' * 80)
        
        return '\n'.join(output)


class InputValidator:
    """
    ✅ Validate user input for scanning
    """
    
    @staticmethod
    def validate_target(target):
        """
        ✅ Validate target (IP, domain, or CIDR range)
        
        Returns:
            tuple: (is_valid, error_message)
        """
        target = target.strip()
        
        if not target:
            return False, 'Target cannot be empty'
        
        if len(target) > 100:
            return False, 'Target is too long'
        
        # Check if it's an IPv4 address
        if InputValidator._is_valid_ipv4(target):
            return True, None
        
        # Check if it's an IPv4 CIDR range
        if InputValidator._is_valid_cidr(target):
            return True, None
        
        # Check if it's a valid domain
        if InputValidator._is_valid_domain(target):
            return True, None
        
        return False, 'Invalid target. Use IPv4, domain, or CIDR range (e.g., 192.168.1.0/24)'
    
    @staticmethod
    def _is_valid_ipv4(ip):
        """Check if string is a valid IPv4 address"""
        try:
            ip_obj = ip_address(ip)
            return ip_obj.version == 4
        except AddressValueError:
            return False
    
    @staticmethod
    def _is_valid_cidr(cidr):
        """Check if string is a valid CIDR notation"""
        if '/' not in cidr:
            return False
        
        try:
            IPv4Network(cidr)
            return True
        except (ValueError, AddressValueError):
            return False
    
    @staticmethod
    def _is_valid_domain(domain):
        """Check if string is a valid domain name"""
        domain_regex = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        
        if re.match(domain_regex, domain) and '.' in domain:
            return True
        
        return False


class RiskAnalyzer:
    """
    ✅ Analyze scan results for security risks
    """
    
    # Common dangerous ports
    DANGEROUS_PORTS = {
        21: 'FTP - File Transfer (Unencrypted)',
        23: 'TELNET - Remote Access (Unencrypted)',
        25: 'SMTP - Email (Can be abused)',
        135: 'RPC - Remote Procedure Call (Vulnerability risk)',
        139: 'NETBIOS - File Sharing',
        445: 'SMB - Windows File Sharing (Common target)',
        3389: 'RDP - Remote Desktop (Brute force risk)',
        3306: 'MySQL - Database (Should not be exposed)',
        5432: 'PostgreSQL - Database (Should not be exposed)',
        5984: 'CouchDB - Database (Should not be exposed)',
        6379: 'Redis - Cache (Should not be exposed)',
        27017: 'MongoDB - Database (Should not be exposed)',
    }
    
    @classmethod
    def analyze(cls, parsed_result):
        """
        ✅ Analyze parsed results and return risk assessment
        
        Returns:
            dict: Risk analysis with recommendations
        """
        risks = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for host in parsed_result.get('hosts', []):
            for proto, ports in host['protocols'].items():
                for port in ports:
                    if port['state'] == 'open':
                        port_num = port['port']
                        
                        if port_num in cls.DANGEROUS_PORTS:
                            risk = {
                                'port': port_num,
                                'service': port['service'],
                                'description': cls.DANGEROUS_PORTS[port_num],
                                'recommendation': f'Close this port or restrict access if not needed'
                            }
                            
                            if port_num in [3306, 5432, 5984, 6379, 27017]:
                                risks['critical'].append(risk)
                            elif port_num in [445, 3389]:
                                risks['high'].append(risk)
                            else:
                                risks['medium'].append(risk)
        
        return risks
    
    @classmethod
    def get_risk_level(cls, open_ports_count):
        """
        ✅ Calculate overall risk level
        
        Returns:
            str: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if open_ports_count >= 20:
            return 'CRITICAL'
        elif open_ports_count >= 10:
            return 'HIGH'
        elif open_ports_count >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
