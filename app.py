from datetime import datetime
from functools import wraps
from flask import Flask, abort, json, request
from flask_cors import CORS

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

@app.route('/api/healthcheck', methods=['GET'])
def healthcheck():  
  return app.response_class(
    response=json.dumps(datetime.now()),
    status=200,
    mimetype='application/json'
  )