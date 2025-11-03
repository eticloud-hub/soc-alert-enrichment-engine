import requests
import json
import time

# Free tier API endpoints
ABUSEIPDB_API = "https://api.abuseipdb.com/api/v2/check"
IPINFO_API = "https://ipinfo.io"

# Mock enrichment data (to avoid API rate limits in testing)
MOCK_ENRICHMENT = {
    "192.168.1.105": {
        "reputation": 65,
        "is_vpn": False,
        "threat_types": ["brute_force"]
    },
    "198.51.100.89": {
        "reputation": 92,
        "is_vpn": True,
        "threat_types": ["phishing"]
    },
    "203.0.113.78": {
        "reputation": 85,
        "is_vpn": False,
        "threat_types": ["port_scanning"]
    },
    "192.0.2.15": {
        "reputation": 78,
        "is_vpn": False,
        "threat_types": ["malware"]
    },
    "198.51.100.200": {
        "reputation": 88,
        "is_vpn": True,
        "threat_types": ["c2_communication"]
    },
    "203.0.113.99": {
        "reputation": 45,
        "is_vpn": False,
        "threat_types": ["brute_force"]
    }
}

def get_ip_reputation(ip_address):
    """
    Get IP reputation score (0-100, higher = more suspicious)
    Using mock data to avoid API rate limits
    """
    if ip_address in MOCK_ENRICHMENT:
        return MOCK_ENRICHMENT[ip_address]

    # Fallback for unknown IPs
    return {
        "reputation": 0,
        "is_vpn": False,
        "threat_types": []
    }

def get_geolocation(ip_address):
    """
    Get geolocation and ASN info for IP
    Returns mock data for testing
    """
    mock_geos = {
        "192.168.1.105": {"country": "IN", "city": "Mumbai", "asn": "AS9829"},
        "198.51.100.89": {"country": "US", "city": "New York", "asn": "AS8452"},
        "203.0.113.78": {"country": "CN", "city": "Beijing", "asn": "AS4134"},
        "192.0.2.15": {"country": "RU", "city": "Moscow", "asn": "AS3216"},
        "198.51.100.200": {"country": "KP", "city": "Pyongyang", "asn": "AS131"},
        "203.0.113.99": {"country": "IN", "city": "Bangalore", "asn": "AS9829"}
    }

    return mock_geos.get(ip_address, {"country": "Unknown", "city": "Unknown", "asn": "Unknown"})

def check_urlhaus(url):
    """
    Check if URL is in URLhaus malicious database
    Returns True if malicious, False otherwise
    """
    # For this demo, check against a small list
    malicious_domains = [
        "phishing-example.com",
        "malware-distribution.net",
        "command-control.xyz"
    ]

    return any(domain in url.lower() for domain in malicious_domains)

def enrich_alert(source_ip, destination_ip, alert_type, message):
    """
    Enrich alert with threat intelligence data
    Returns enrichment dictionary
    """
    enrichment = {
        "source_reputation": get_ip_reputation(source_ip),
        "source_geo": get_geolocation(source_ip),
        "destination_geo": get_geolocation(destination_ip),
        "alert_type_severity": get_alert_type_severity(alert_type)
    }

    return enrichment

def get_alert_type_severity(alert_type):
    """
    Map alert types to base severity scores
    """
    severity_map = {
        "failed_login": 30,
        "malicious_url": 70,
        "port_scan": 60,
        "data_exfiltration": 90,
        "command_execution": 85,
        "privilege_escalation": 95,
        "lateral_movement": 75,
        "malware_detected": 80
    }

    return severity_map.get(alert_type, 50)