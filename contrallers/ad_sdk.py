from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionManager
import datetime
import uuid

ad_sdk_blueprint = Blueprint('ad_sdk', __name__)

@ad_sdk_blueprint.route('/ad_sdk', methods=['POST'])
def create_ad():
    """
    Create a new ad
    ---
    parameters:
      - name: ad
        in: body
        required: true
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
            name:
              type: string
            dicription:
              type: string
            ad_type:
              type: string
            beginning_date:
              type: string
            expiration_date:
              type: string
            ad_location:
              type: string
            ad_link:
              type: string
    responses:
      201:
        description: Ad created
    """
    data = request.get_json()
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    required_fields = ['package_name', 'name', 'dicription', 'ad_type', 'beginning_date', 'expiration_date', 'ad_location', 'ad_link']
    if not all(k in data for k in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        begin = datetime.datetime.strptime(data['beginning_date'], '%Y-%m-%d %H:%M:%S')
        expire = datetime.datetime.strptime(data['expiration_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    if begin > expire:
        return jsonify({"error": "Beginning date must be before expiration date"}), 400

    ad_item = {
        "_id": str(uuid.uuid4()),
        "name": data['name'],
        "dicription": data['dicription'],
        "ad_type": data['ad_type'],
        "beginning_date": begin,
        "expiration_date": expire,
        "ad_location": data['ad_location'],
        "ad_link": data['ad_link'],
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now()
    }

    db[data['package_name']].insert_one(ad_item)
    return jsonify({"message": "Ad created successfully", "_id": ad_item["_id"]}), 201


@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_ads(package_name):
    """
    Get all ads for a specific package
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
    responses:
      200:
        description: Ads retrieved
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    ads = list(db[package_name].find())
    for ad in ads:
        ad['_id'] = str(ad['_id'])
    return jsonify(ads), 200


@ad_sdk_blueprint.route('/ad_sdk/<package_name>/by-id/<ad_id>', methods=['GET'])
def get_ad_by_id(package_name, ad_id):
    """
    Get ad by ID
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
      - name: ad_id
        in: path
        required: true
        type: string
    responses:
      200:
        description: Ad found
      404:
        description: Ad not found
    """
    db = MongoConnectionManager.get_db()
    ad = db[package_name].find_one({"_id": ad_id})
    if ad:
        ad['_id'] = str(ad['_id'])
        return jsonify(ad), 200
    return jsonify({"error": "Ad not found"}), 404


@ad_sdk_blueprint.route('/ad_sdk/<package_name>/by-id/<ad_id>', methods=['PUT'])
def update_ad(package_name, ad_id):
    """
    Update ad by ID
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
      - name: ad_id
        in: path
        required: true
        type: string
      - name: ad
        in: body
        required: true
        schema:
          id: Ad
          properties:
            beginning_date:
              type: string
            expiration_date:
              type: string
    responses:
      200:
        description: Ad updated
    """
    data = request.get_json()
    db = MongoConnectionManager.get_db()
    ad = db[package_name].find_one({"_id": ad_id})
    if not ad:
        return jsonify({"error": "Ad not found"}), 404

    try:
        if 'beginning_date' in data:
            ad['beginning_date'] = datetime.datetime.strptime(data['beginning_date'], '%Y-%m-%d %H:%M:%S')
        if 'expiration_date' in data:
            ad['expiration_date'] = datetime.datetime.strptime(data['expiration_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    db[package_name].update_one({"_id": ad_id}, {"$set": ad})
    return jsonify({"message": "Ad updated"}), 200


@ad_sdk_blueprint.route('/ad_sdk/<package_name>/by-date', methods=['GET'])
def get_ads_by_date(package_name):
    """
    Get ads active on a specific date
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
      - name: date
        in: query
        required: true
        type: string
    responses:
      200:
        description: Active ads by date
    """
    date_str = request.args.get('date')
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid date format"}), 400

    db = MongoConnectionManager.get_db()
    ads = list(db[package_name].find({
        "expiration_date": {"$gte": date},
        "beginning_date": {"$lte": date}
    }))
    for ad in ads:
        ad['_id'] = str(ad['_id'])
    return jsonify(ads), 200


@ad_sdk_blueprint.route('/ad_sdk/<package_name>/by-location', methods=['GET'])
def get_ads_by_location(package_name):
    """
    Get active ads by location
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
      - name: location
        in: query
        required: true
        type: string
    responses:
      200:
        description: Active ads by location
    """
    location = request.args.get("location")
    now = datetime.datetime.now()
    db = MongoConnectionManager.get_db()
    ads = list(db[package_name].find({
        "expiration_date": {"$gte": now},
        "beginning_date": {"$lte": now},
        "ad_location": location
    }))
    for ad in ads:
        ad['_id'] = str(ad['_id'])
    return jsonify(ads), 200


@ad_sdk_blueprint.route('/ad_sdk/all', methods=['DELETE'])
def delete_all_ads():
    """
    Delete all ads
    ---
    responses:
      200:
        description: All ads deleted
    """
    db = MongoConnectionManager.get_db()
    for collection in db.list_collection_names():
        db[collection].delete_many({})
    return jsonify({"message": "All ads deleted successfully"}), 200
