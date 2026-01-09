"""
DNS Fix for Python IPv6 Resolution Issues
This script forces Python to prefer IPv4 addresses when resolving hostnames.
"""
import socket

# Store the original getaddrinfo function
_original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4_only(*args, **kwargs):
    """
    Wrapper for socket.getaddrinfo that filters out IPv6 addresses.
    Forces IPv4-only resolution to avoid DNS issues on some networks.
    """
    responses = _original_getaddrinfo(*args, **kwargs)
    # Filter to keep only IPv4 (AF_INET) responses
    return [response for response in responses if response[0] == socket.AF_INET]

# Replace the system's getaddrinfo with our IPv4-only version
socket.getaddrinfo = getaddrinfo_ipv4_only

print("DNS fix applied: Python will now use IPv4 addresses only.")
