#!/usr/bin/env python3
"""Test bytes input support."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from burpr import burpr
from burpr.models.BurpRequest import BurpRequest

def test_parse_bytes():
    """Test parsing bytes input."""
    print("Testing bytes input...")
    
    # Test 1: Basic request as bytes
    request_bytes = b"GET /test HTTP/1.1\r\nHost: example.com\r\n\r\n"
    req = burpr.parse_string(request_bytes)
    assert req.method == "GET"
    assert req.path == "/test"
    assert req.host == "example.com"
    print("✓ Basic bytes parsing works")
    
    # Test 2: Bytes with null bytes and special chars
    request_bytes = b"POST /binary HTTP/1.1\r\nHost: example.com\r\nX-Binary: \xff\xfe\x00\r\n\r\nBinary\x00Data\xff"
    req = burpr.parse_string(request_bytes)
    assert req.body == "Binary\x00Data\xff"
    assert req.headers["X-Binary"] == "\xff\xfe\x00"
    print("✓ Binary data preserved from bytes input")
    
    # Test 3: Mixed string and bytes
    req = BurpRequest()
    req.set_host("example.com")
    req.set_body(b"Raw\x00Bytes\xff")  # Pass bytes
    assert req.body == "Raw\x00Bytes\xff"
    
    req.set_header("X-Test", b"\xff\xfe")  # Pass bytes  
    assert req.headers["X-Test"] == "\xff\xfe"
    print("✓ set_body and set_header accept bytes")


def test_string_still_works():
    """Test that string input still works."""
    print("\nTesting string compatibility...")
    
    # Regular string
    req = burpr.parse_string("GET / HTTP/1.1\nHost: example.com\n\n")
    assert req.method == "GET"
    
    # String with special chars
    req = burpr.parse_string("POST / HTTP/1.1\nHost: example.com\n\nData\x00\xff")
    assert req.body == "Data\x00\xff"
    
    print("✓ String input still works")


if __name__ == "__main__":
    test_parse_bytes()
    test_string_still_works()
    print("\n✅ All bytes support tests passed!")