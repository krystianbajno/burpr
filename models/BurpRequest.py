import urllib 

class BurpRequest:
  def __init__(self, host="", path="", protocol="", method="", headers={}, body={}):
    self.host = host
    self.path = path
    self.protocol = protocol
    self.method = method
    self.headers = headers
    self.body = body

  @property
  def url(self, protocol="https"):
    return f'{protocol}://{self.host}{self.path}'

  def set_host(self, host):
    self.host = host

  def set_path(self, path):
    self.path = path

  def set_method(self, method):
    self.method = method

  def set_headers(self, headers):
    self.headers = headers

  def set_header(self, headerKey, headerValue):
    self.headers[headerKey, headerValue]

  def set_body(self, body):
    self.body = body
  
  def set_protocol(self, protocol):
    self.protocol = protocol

  def prepare(self):
    self.set_header("Content-Length", urllib.parse.urlencode(self.body))