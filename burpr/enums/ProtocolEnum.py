from enum import Enum

class ProtocolEnum(str, Enum):
  HTTP2 = "HTTP/2"
  HTTP1_1 = "HTTP/1.1"
  HTTP1_0 = "HTTP/1.0"

  def __str__(self) -> str:
    return self.value