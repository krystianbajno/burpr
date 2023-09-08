import models.BurpRequest as BurpRequest

def parse_string(string):
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
  
  return BurpRequest.BurpRequest(
    headers["Host"],
    path,
    protocol,
    method,
    headers,
    body
  )
  
def parse_file(file):
  with open(file, "r") as f:
    return parse_string(f.read())
  