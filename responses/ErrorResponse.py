class ErrorResponse:
  def __init__(self, message, status):
    self.message = message
    self.status = status
    
  def to_dict(self):
    return {
      "message": self.message,
      "status": self.status
    }