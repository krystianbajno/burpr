import urllib3
from burpr.models.BurpRequest import BurpRequest
from burpr.enums.TransportEnum import TransportEnum

def parse_string(string) -> BurpRequest:
  data = string.splitlines()
  method = data[0].split(" ")[0]
  path = data[0].split(" ")[1]
  protocol = data[0].split(" ")[2]
  headers = {}
  body = {}

  # headers
  for line in data[1:]:
    if line == "":
      break
    headers[line.split(": ")[0]] = line.split(": ")[1]
    
  # param
  for param in data[-1].split("&"):
    body[param.split("=")[0]] = param.split("=")[1]
  
  return BurpRequest(
    headers["Host"],
    path,
    protocol,
    method,
    headers,
    body,
    TransportEnum.HTTPS
  )
  
def parse_file(file):
  with open(file, "r") as f:
    return parse_string(f.read())
  
def clone(req: BurpRequest) -> BurpRequest:
  return BurpRequest(req.host, req.path, req.protocol, req.method, req.headers, req.body, req.transport)

def prepare(req: BurpRequest):
  req.set_header("Content-Length", len(urllib3.parse.urlencode(req.body)))