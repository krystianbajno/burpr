from burpr.enums.ProtocolEnum import ProtocolEnum

class BurpRequest:
  def __init__(
    self,
    host="",
    path="",
    protocol="",
    method="",
    headers=None,
    body="",
    transport=""
  ):
    self.host = host
    self.path = path
    self.protocol = protocol
    self.method = method
    self.headers = headers if headers is not None else {}
    self.body = body
    self.transport = transport

  @property
  def url(self):
    return f'{self.transport}://{self.host}{self.path}'

  @property
  def is_http2(self): 
    return self.protocol == ProtocolEnum.HTTP2


  def set_header(self, header_key, header_value):
    # Convert bytes to string using latin-1 if needed
    if isinstance(header_value, bytes):
      header_value = header_value.decode('latin-1')
    self.headers[header_key] = str(header_value)

  
  def set_body(self, body):
    # Convert bytes to string using latin-1 if needed
    if isinstance(body, bytes):
      body = body.decode('latin-1')
    self.body = body
  
  
  def __str__(self):
    return f"{self.method} {self.url} {self.protocol}"
  
  def __repr__(self):
    return (f"BurpRequest(host='{self.host}', path='{self.path}', "
            f"protocol='{self.protocol}', method='{self.method}', "
            f"headers={len(self.headers)} items, body={len(self.body)} items, "
            f"transport='{self.transport}')")
  
  def bind(self, placeholder: str, value: str):
    """Replace placeholder in all request components (path, headers, body).
    
    Args:
        placeholder: The placeholder string to replace (e.g., "%TOKEN%")
        value: The value to replace the placeholder with
        
    Returns:
        Self for method chaining
    """
    # Replace in path
    self.path = self.path.replace(placeholder, str(value))
    
    # Replace in host
    self.host = self.host.replace(placeholder, str(value))
    
    # Replace in headers
    for key, header_value in self.headers.items():
        self.headers[key] = header_value.replace(placeholder, str(value))
    
    # Replace in body
    self.body = self.body.replace(placeholder, str(value))
    
    return self
  
  def to_request(self, session=None, auto_prepare=True):
    """Convert to a requests.Request or requests.PreparedRequest object.
    
    Args:
        session: Optional requests.Session to prepare the request with
        auto_prepare: Whether to automatically calculate Content-Length (default: True)
        
    Returns:
        requests.PreparedRequest if session provided, else requests.Request
    """
    import requests
    from burpr import burpr
    
    # Auto-prepare if requested
    if auto_prepare:
        burpr.prepare(self)
    
    # Build the full URL
    url = self.url
    
    # Prepare the request
    req = requests.Request(
        method=self.method,
        url=url,
        headers=self.headers.copy(),
        data=self.body.encode('latin-1') if self.body else None
    )
    
    if session:
        return session.prepare_request(req)
    else:
        return req.prepare()
  
  def make_request(self, session=None, auto_prepare=True, **kwargs):
    """Execute the HTTP request using requests library.
    
    Args:
        session: Optional requests.Session to use
        auto_prepare: Whether to automatically calculate Content-Length (default: True)
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        requests.Response object
    """
    import requests
    
    if session is None:
        session = requests.Session()
    
    # Determine if we should use HTTP/2
    if self.is_http2 and 'http2' not in kwargs:
        # Note: requests doesn't support HTTP/2 natively
        # Users should use httpx or other libraries for HTTP/2
        import warnings
        warnings.warn("requests library doesn't support HTTP/2. Consider using httpx instead.")
    
    prepared = self.to_request(session, auto_prepare=auto_prepare)
    return session.send(prepared, **kwargs)
  
  def make_httpx_request(self, client=None, auto_prepare=True, **kwargs):
    """Execute the HTTP request using httpx library (supports HTTP/2).
    
    Args:
        client: Optional httpx.Client to use
        auto_prepare: Whether to automatically calculate Content-Length (default: True)
        **kwargs: Additional arguments to pass to httpx
        
    Returns:
        httpx.Response object
    """
    try:
        import httpx
    except ImportError:
        raise ImportError("httpx is required for HTTP/2 support. Install with: pip install httpx")
    
    if client is None:
        client = httpx.Client(http2=self.is_http2)
    
    # Auto-prepare if requested
    if auto_prepare:
        from burpr import burpr
        burpr.prepare(self)
    
    return client.request(
        method=self.method,
        url=self.url,
        headers=self.headers,
        content=self.body.encode('latin-1') if self.body else None,
        **kwargs
    )