from flask import Flask
from flasgger import Swagger
from mongodb_connection_manager import MongoConnectionManager
from routes import initial_routes

import os

app = Flask(__name__)
Swagger(app)
MongoConnectionManager.initialize_db()
initial_routes(app)

@app.route('/')
def index():
    return "Welcome to Ad SDK Flask API!"

# ⛔️ חשוב! לא צריך app.run() כשמריצים על Vercel
# זה כן רץ מקומית, אבל לא בשירותים serverless
