from datetime import datetime

class SuccessResponse:
  def __init__(self, response, imageUrl = None):
    self.message = "Successful"
    self.data = {
      "isBot": True,
      "response": response,
      "isContainImage": bool(imageUrl),
      "imageUrl": imageUrl,
      "createdAt": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-1]
    }
    
  def to_dict(self):
    return {
      "message": self.message,
      "data": self.data
    }