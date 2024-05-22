from flask import Flask, request, jsonify
import requests
from responses.SuccessResponse import SuccessResponse
from responses.ErrorResponse import ErrorResponse

app = Flask(__name__)
RASA_API_URL = 'http://127.0.0.1:5005/webhooks/rest/webhook'

@app.route('/')
def home():
  strWelcome = 'Hello! Welcome to my chatbot api'
  return strWelcome

@app.route('/chatbot', methods = ['POST'])
def create_chat():
  print('into create chatbot')
  try:
    # Get the data request
    user_message = request.json['message']
    print('User Message: ', user_message)
    
    rasa_response = requests.post(RASA_API_URL, json = {'message': user_message})
    print(f"RASA Response Status Code: {rasa_response.status_code}")
    print(f"RASA Response Headers: {rasa_response.headers}")
    # rasa_response.raise_for_status()
    
    rasa_response_json = rasa_response.json()
    print('Rasa Response: ', rasa_response_json)
    
    if not rasa_response_json:
      raise ValueError("Empty response from chatbot")
    
    bot_response_message = 'Sorry, I did not understand that'
    if rasa_response_json:
      bot_response_message = rasa_response_json[0]['text']
    
    image_url = next((item.get('image') for item in rasa_response_json if 'image' in item), None)

    response = SuccessResponse(bot_response_message, image_url)
    return jsonify(response.to_dict()), 200
    
  except requests.exceptions.RequestException as e:
    error_response = ErrorResponse("Failed to connect to chatbot server", 500)
    return jsonify(error_response.to_dict()), 500
  
  except Exception as e:
    error_response = ErrorResponse(str(e), 400)
    return jsonify(error_response.to_dict()), 400
  
if __name__ == "__main__":
  app.run(debug = True)