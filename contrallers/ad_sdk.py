from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionManager
import datetime
import uuid

ad_sdk_blueprint = Blueprint('ad_sdk', __name__)

# 1. Create a new ad
@ad_sdk_blueprint.route('/ad_sdk', methods=['POST'])
def create_ad():
    """Create a new ad
    ---
    parameters:
      - name: ad
        in: body
        required: true
        schema:
          id: Ad
          required: [package_name, name, dicription, ad_type, beginning_date, expiration_date, ad_location, ad_link]
          properties:
            package_name: {type: string}
            name: {type: string}
            dicription: {type: string}
            ad_type: {type: string}
            beginning_date: {type: string}
            expiration_date: {type: string}
            ad_location: {type: string}
            ad_link: {type: string}
    responses:
      201: {description: Ad created successfully}
    """
    data = request.get_json()
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    required = ['package_name', 'name', 'dicription', 'ad_type', 'beginning_date', 'expiration_date', 'ad_location', 'ad_link']
    if not all(k in data for k in required):
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


# 2. Get all ads for package name
@ad_sdk_blueprint.route('/ad_sdk/<package_name>/all', methods=['GET'])
def get_ads(package_name):
    """
    Get all ads for a package
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        type: string
    responses:
      200: {description: List of ads}
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    ads = list(db[package_name].find())
    for ad in ads:
        ad['_id'] = str(ad['_id'])
    return jsonify(ads), 200


# 3. Get ad by ID
@ad_sdk_blueprint.route('/ad_sdk/<package_name>/<ad_id>', methods=['GET'])
def get_ad_by_id(package_name, ad_id):
    """
    Get ad by ID
    ---
    parameters:
      - name: package_name
        in: path
        required: true
      - name: ad_id
        in: path
        required: true
    responses:
      200: {description: Ad found}
      404: {description: Not found}
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    ad = db[package_name].find_one({"_id": ad_id})
    if ad:
        ad['_id'] = str(ad['_id'])
        return jsonify(ad), 200
    return jsonify({"error": "Ad not found"}), 404


# 4. Update ad by ID
@ad_sdk_blueprint.route('/ad_sdk/<package_name>/<ad_id>', methods=['PUT'])
def update_ad(package_name, ad_id):
    """
    Update ad details by ID
    ---
    parameters:
      - name: package_name
        in: path
        required: true
      - name: ad_id
        in: path
        required: true
      - name: ad
        in: body
        required: true
        schema:
          id: Ad
          properties:
            name: {type: string}
            dicription: {type: string}
            ad_type: {type: string}
            beginning_date: {type: string}
            expiration_date: {type: string}
            ad_location: {type: string}
            ad_link: {type: string}
    responses:
      200: {description: Ad updated}
      404: {description: Ad not found}
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    data = request.get_json()
    update_fields = {}

    for field in ['name', 'dicription', 'ad_type', 'ad_location', 'ad_link']:
        if field in data:
            update_fields[field] = data[field]

    try:
        if 'beginning_date' in data:
            update_fields['beginning_date'] = datetime.datetime.strptime(data['beginning_date'], '%Y-%m-%d %H:%M:%S')
        if 'expiration_date' in data:
            update_fields['expiration_date'] = datetime.datetime.strptime(data['expiration_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    if 'beginning_date' in update_fields and 'expiration_date' in update_fields:
        if update_fields['beginning_date'] > update_fields['expiration_date']:
            return jsonify({"error": "Beginning date must be before expiration date"}), 400

    update_fields['updated_at'] = datetime.datetime.now()
    result = db[package_name].update_one({"_id": ad_id}, {"$set": update_fields})

    if result.matched_count == 0:
        return jsonify({"error": "Ad not found"}), 404

    return jsonify({"message": "Ad updated successfully", "_id": ad_id}), 200


# 5. Get active ads by date (using ?date=YYYY-MM-DD)
@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_ads_by_date_or_location(package_name):
    """
    Get active ads by date or location
    ---
    parameters:
      - name: package_name
        in: path
        required: true
      - name: date
        in: query
        required: false
        type: string
      - name: location
        in: query
        required: false
        type: string
    responses:
      200: {description: List of filtered ads}
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    query = {}
    now = datetime.datetime.now()
    filter_date = now

    if 'date' in request.args:
        try:
            filter_date = datetime.datetime.strptime(request.args.get('date'), '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    query["beginning_date"] = {"$lte": filter_date}
    query["expiration_date"] = {"$gte": filter_date}

    if 'location' in request.args:
        query["ad_location"] = request.args.get('location')

    ads = list(db[package_name].find(query))
    for ad in ads:
        ad['_id'] = str(ad['_id'])
    return jsonify(ads), 200


# 6. Delete all ads
@ad_sdk_blueprint.route('/ad_sdk', methods=['DELETE'])
def delete_all_ads():
    """
    Delete all ads from all packages
    ---
    responses:
      200: {description: All ads deleted}
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    for name in db.list_collection_names():
        db[name].delete_many({})
    return jsonify({"message": "All ads deleted successfully"}), 200
