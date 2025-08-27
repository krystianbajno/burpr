#!/usr/bin/env python3
"""Test Latin-1 encoding and fuzzing-friendly features."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from burpr import burpr
from burpr.models.BurpRequest import BurpRequest

def test_latin1_characters():
    """Test that all Latin-1 characters (0x00-0xFF) are preserved."""
    print("Testing Latin-1 character preservation...")
    
    # Create a request with all Latin-1 characters in body
    all_chars = ''.join(chr(i) for i in range(256))
    
    request = f"""POST /fuzz HTTP/1.1
Host: example.com
Content-Type: application/octet-stream

{all_chars}"""
    
    req = burpr.parse_string(request)
    assert req.body == all_chars, "Body should preserve all Latin-1 characters"
    
    # Test in headers (skip control chars that might break header parsing)
    # Only test printable Latin-1 characters in headers
    header_chars = ''.join(chr(i) for i in range(33, 127)) + ''.join(chr(i) for i in range(160, 256))
    request_with_bad_header = """GET /test HTTP/1.1
Host: example.com
X-Fuzz: """ + header_chars + """

"""
    req = burpr.parse_string(request_with_bad_header)
    assert req.headers["X-Fuzz"] == header_chars
    
    print("✓ All Latin-1 characters preserved")


def test_null_bytes():
    """Test null byte handling."""
    print("Testing null byte handling...")
    
    request = b"""POST /null-test HTTP/1.1
Host: example.com
Content-Type: application/octet-stream

Hello\x00World\x00Test""".decode('latin-1')
    
    req = burpr.parse_string(request)
    assert req.body == "Hello\x00World\x00Test"
    assert '\x00' in req.body
    
    print("✓ Null bytes preserved")


def test_control_characters():
    """Test control character handling."""
    print("Testing control characters...")
    
    # Create body with various control characters
    control_chars = '\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0e\x0f'
    request = f"""POST /control HTTP/1.1
Host: example.com

{control_chars}data{control_chars}"""
    
    req = burpr.parse_string(request)
    assert req.body == f"{control_chars}data{control_chars}"
    
    print("✓ Control characters preserved")


def test_content_length_calculation():
    """Test Content-Length calculation with Latin-1 encoding."""
    print("Testing Content-Length calculation...")
    
    # Create request with multi-byte UTF-8 characters that fit in Latin-1
    req = BurpRequest(
        host="example.com",
        path="/test",
        protocol="HTTP/1.1",
        method="POST",
        headers={},
        body="café\xFF\xFE"  # Latin-1 extended characters
    )
    
    burpr.prepare(req)
    
    # Content-Length should be byte length in Latin-1
    expected_length = len(req.body.encode('latin-1'))
    assert req.headers["Content-Length"] == str(expected_length)
    assert req.headers["Content-Length"] == "6"  # c=1, a=1, f=1, é=1, FF=1, FE=1
    
    print(f"✓ Content-Length correctly calculated as {expected_length}")


def test_to_burp_format():
    """Test converting back to Burp format preserves special characters."""
    print("Testing to_burp_format...")
    
    req = BurpRequest(
        host="example.com",
        path="/test",
        protocol="HTTP/1.1", 
        method="POST",
        headers={"X-Binary": "test\xFF\xFE"},
        body="Binary\x00Data\xFF"
    )
    
    output = burpr.to_burp_format(req)
    assert "Binary\x00Data\xFF" in output
    assert "test\xFF\xFE" in output
    
    print("✓ to_burp_format preserves special characters")


def test_file_parsing():
    """Test parsing from file with Latin-1 encoding."""
    print("Testing file parsing with Latin-1...")
    
    # Create a test file with Latin-1 characters
    test_file = "test_latin1_request.txt"
    content = b"POST /test HTTP/1.1\r\nHost: example.com\r\n\r\nLatin1:\xFF\xFE\x00\x01"
    
    with open(test_file, "wb") as f:
        f.write(content)
    
    try:
        req = burpr.parse_file(test_file)
        assert req.body == "Latin1:\xFF\xFE\x00\x01"
        print("✓ File parsing preserves Latin-1 encoding")
    finally:
        os.remove(test_file)


def test_fuzzing_placeholders():
    """Test that fuzzing placeholders work with special characters."""
    print("Testing fuzzing placeholder replacement...")
    
    req = BurpRequest(
        host="example.com",
        path="/api?param=$FUZZ$",
        protocol="HTTP/1.1",
        method="POST", 
        headers={"X-Token": "$TOKEN$"},
        body='{"data": "$PAYLOAD$"}'
    )
    
    # Replace with Latin-1 characters
    req.bind("$FUZZ$", "\xFF\xFE")
    req.bind("$TOKEN$", "Bearer\x00\x01")
    req.bind("$PAYLOAD$", "test\x00\xFF")
    
    assert req.path == "/api?param=\xFF\xFE"
    assert req.headers["X-Token"] == "Bearer\x00\x01"
    assert req.body == '{"data": "test\x00\xFF"}'
    
    print("✓ Placeholders work with special characters")


if __name__ == "__main__":
    test_latin1_characters()
    test_null_bytes()
    test_control_characters()
    test_content_length_calculation()
    test_to_burp_format()
    test_file_parsing()
    test_fuzzing_placeholders()
    
    print("\n✅ All Latin-1 and fuzzing tests passed!")