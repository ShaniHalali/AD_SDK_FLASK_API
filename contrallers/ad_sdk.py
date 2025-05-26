from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionManager
import datetime
import uuid

ad_sdk_blueprint = Blueprint('ad_sdk', __name__)

# 1. Create a new ad
@ad_sdk_blueprint.route('/ad_sdk', methods=['POST'])
def create_ad():
    """
    Create a new ad 
    ---
    parameters:
      - name: ad
        in: body
        required: true
        description: Ad object that needs to be created
        schema:
          id: Ad
          required:
            - package_name
            - name
            - dicription
            - ad_type
            - beginning_date
            - expiration_date
            - ad_location
            - ad_link
          properties:
            package_name:
              type: string
              description: The name of the package
            name:
              type: string
              description: The name of the ad
            dicription:
              type: string
              description: The description of the ad
            ad_type:
              type: string
              description: The type of the ad
            beginning_date:
              type: string
              description: The start date of the ad
            expiration_date:
              type: string
              description: The end date of the ad
            ad_location:
              type: string
              description: The location of the ad
            ad_link:
              type: string
              description: The link of the ad 
    responses:
      201:
        description: Ad created successfully
      400:
        description: Invalid input
      500:
        description: An error occurred while creating the ad
    """
    data = request.get_json()
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    required_fields = [
        'package_name', 'name', 'dicription', 'ad_type',
        'beginning_date', 'expiration_date', 'ad_location', 'ad_link'
    ]
    if not all(key in data for key in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        beginning_date = datetime.datetime.strptime(data['beginning_date'], '%Y-%m-%d %H:%M:%S')
        expiration_date = datetime.datetime.strptime(data['expiration_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    if beginning_date > expiration_date:
        return jsonify({"error": "Beginning date must be before expiration date"}), 400

    ad_item = {
        "_id": str(uuid.uuid4()),
        "name": data['name'],
        "dicription": data['dicription'],
        "ad_type": data['ad_type'],
        "beginning_date": beginning_date,
        "expiration_date": expiration_date,
        "ad_location": data['ad_location'],
        "ad_link": data['ad_link'],
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now()
    }

    package_collection = db[data['package_name']]
    package_collection.insert_one(ad_item)

    return jsonify({"message": "Ad created successfully", "_id": ad_item["_id"]}), 201


# 2. Get all ads for package name
@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_ads(package_name):
    """
    Get all ads for a specific package name
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
        description: Name of the package
    responses:
      200:
        description: List of ads
      404:
        description: No ads found
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    package_collection = db[package_name]
    ads = list(package_collection.find())
    if not ads:
        return jsonify({"error": "No ads found"}), 404

    for ad in ads:
        ad['_id'] = str(ad['_id'])

    return jsonify(ads), 200
