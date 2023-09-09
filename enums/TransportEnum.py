from enum import Enum

class TransportEnum(str, Enum):
  HTTP = "http"
  HTTPS = "https"

  def __str__(self) -> str:
    return self.value
  
