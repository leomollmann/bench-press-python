from datetime import datetime
from functools import wraps
from flask import Flask, abort, json, request
from flask_cors import CORS
from gpt import chat_gpt_repository

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

def handle_internal_error(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except Exception as error:
      abort(500, "Internal Server Error")

  return decorator

@app.route('/api/create_user', methods=['POST'])
def createUser():
  user = request.get_json()

  chat_gpt_repository.create_user({
    'name': user['name'],
    'checkin': user['checkin'],
    'checkout': user['checkout'],
    'bill': user['bill']
  })

  return app.response_class(
    status=200,
    mimetype='application/json'
  )

@app.route('/api/get_history', methods=['GET'])
def getHistory(): 
  user = request.args.get("user")
  history = chat_gpt_repository.get_hisotry(user)
  
  return app.response_class(
    response=json.dumps(history),
    status=200,
    mimetype='application/json'
  )

@app.route('/api/chat', methods=['POST'])
def addMessage():
  user = request.args.get("user")
  data = request.get_json()
  response = chat_gpt_repository.chat(user, data['chat'])

  return app.response_class(
    response=json.dumps(response),
    status=200,
    mimetype='application/json'
  )