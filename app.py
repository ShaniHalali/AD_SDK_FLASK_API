from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from mongodb_connection_manager import MongoConnectionManager
from routes import initial_routes

import os

app = Flask(__name__)
CORS(app)
Swagger(app)
MongoConnectionManager.initialize_db()
initial_routes(app)

@app.route('/')
def index():
    return "Welcome to Ad SDK Flask API!"



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8088))
    app.run(debug=True , port=port, host = "0.0.0.0")

