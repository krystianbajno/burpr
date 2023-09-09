from burpr.enums.ProtocolEnum import ProtocolEnum

class BurpRequest:
  def __init__(
    self,
    host="",
    path="",
    protocol="",
    method="",
    headers={},
    body={},
    transport=""
  ):
    self.host = host
    self.path = path
    self.protocol = protocol
    self.method = method
    self.headers = headers
    self.body = body
    self.transport = transport

  @property
  def url(self):
    return f'{self.transport}://{self.host}{self.path}'

  @property
  def is_http2(self): 
    return self.protocol == ProtocolEnum.HTTP2

  def set_host(self, host):
    self.host = host

  def set_path(self, path):
    self.path = path

  def set_method(self, method):
    self.method = method

  def set_headers(self, headers):
    self.headers = headers

  def remove_header(self, header_key):
    del self.headers[header_key]

  def set_header(self, header_key, header_value):
    self.headers[header_key] = str(header_value)

  def set_body(self, body):
    self.body = body

  def remove_parameter(self, param_key):
    del self.body[param_key]

  def set_parameter(self, param_key, param_value):
    self.body[param_key] = str(param_value)
  
  def set_protocol(self, protocol):
    self.protocol = protocol

  def set_transport(self, transport):
    self.transport = transport