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
        schema:
          type: object
          required:
            - package_name
            - name
            - description
            - ad_type
            - beginning_date
            - expiration_date
            - ad_location
            - ad_link
            - category
            - ad_image_link
          
          properties:
            package_name:
              type: string
              description: "App package name the ad is associated with"
            name:
              type: string
              description: "Name of the ad"
            description:
              type: string
              description: "Description of the ad"
            ad_type:
              type: string
              description: "Type of the ad (e.g., image, video)"
            beginning_date:
              type: string
              description: "Start date of the ad (format: YYYY-MM-DD HH:MM:SS)"
            expiration_date:
              type: string
              description: "End date of the ad (format: YYYY-MM-DD HH:MM:SS)"
            ad_location:
              type: string
              description: "Location to target the ad"
            ad_link:
              type: string
              description: "Link to the ad content"
            category:
              type: string
              enum: ["Hotel", "Restaurant", "Attraction", "Shop", "Product"]
              description: "Hotel / Restaurant  / Attraction / Shop / Product"
            ad_image_link:
              type: string
              description: "Link to the ad url"
    responses:
      201:
        description: Ad created successfully
      400:
        description: Bad request, missing fields or invalid date format
      500:
        description: Internal server error
    """
    data = request.get_json()

    # Start by checking DB connection
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    # Required fields check
    required_fields = [
        'package_name', 'name', 'description', 'ad_type',
        'beginning_date', 'expiration_date', 'ad_location', 'ad_link','category', 'ad_image_link'
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Date parsing
    try:
        begin = datetime.datetime.strptime(data['beginning_date'], '%Y-%m-%d %H:%M:%S')
        expire = datetime.datetime.strptime(data['expiration_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"}), 400

    if begin > expire:
        return jsonify({"error": "Beginning date must be before expiration date"}), 400
    
    valid_categories = ['Hotel', 'Restaurant', 'Attraction', 'Shop' , 'Product']
    if data['category'] not in valid_categories:
        return jsonify({"error": "Invalid category. Must be one of: Hotel, Restaurant, Attraction, Shop, Product"}), 400


    # Create the ad item
    ad_item = {
        "_id": str(uuid.uuid4()),
        "package_name": data['package_name'],
        "category": data['category'],
        "name": data['name'],
        "description": data['description'],
        "ad_type": data['ad_type'],
        "beginning_date": begin,
        "expiration_date": expire,
        "ad_location": data['ad_location'],
        "ad_link": data['ad_link'],
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "ad_image_link": data['ad_image_link']
    }

    # Insert into MongoDB in the correct collection
    try:
        db[data['package_name']].insert_one(ad_item)
        return jsonify({"message": "Ad created successfully", "_id": ad_item["_id"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    Update ad details by ID and package name
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
            description: {type: string}
            ad_type: {type: string}
            beginning_date: {type: string}
            expiration_date: {type: string}
            ad_location: {type: string}
            ad_link: {type: string}
            category: {type: string}
            ad_image_link: {type: string}
    responses:
      200: {description: Ad updated}
      404: {description: Ad not found}
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    data = request.get_json()
    update_fields = {}

    for field in ['name', 'description', 'ad_type', 'ad_location', 'ad_link', 'category', 'ad_image_link']:
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
        
    if 'ad_image_link' in update_fields and not update_fields['ad_image_link'].startswith('http'):
        return jsonify({"error": "Invalid ad_image_link URL"}), 400
    
    valid_categories = ['Hotel', 'Restaurant', 'Attraction', 'Shop', 'Product']
    if 'category' in data and data['category'] not in valid_categories:
        return jsonify({
        "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}" }), 400
    
    update_fields['updated_at'] = datetime.datetime.now()
    result = db[package_name].update_one({"_id": ad_id}, {"$set": update_fields})


    if result.matched_count == 0:
        return jsonify({"error": "Ad not found"}), 404
    
  
    return jsonify({"message": "Ad updated successfully", "_id": ad_id}), 200


@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_ads_by_date_or_location_or_category(package_name):
    """
    Get active ads by date, location, or category
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
      - name: category
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
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    query["beginning_date"] = {"$lte": filter_date}
    query["expiration_date"] = {"$gte": filter_date}

    if 'location' in request.args:
        query["ad_location"] = request.args.get('location')

    if 'category' in request.args:
        query["category"] = request.args.get('category')

    ads = list(db[package_name].find(query))
    for ad in ads:
        ad['_id'] = str(ad['_id'])
    return jsonify(ads), 200



# 6. Delete all ads
@ad_sdk_blueprint.route('/ad_sdk', methods=['DELETE'])
def delete_all_ads():
    """
    Delete all ads from package - Ads
    ---
    responses:
      200: {description: All ads deleted}
    """
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    for name in db.list_collection_names():
        db['Ads'].delete_many({})
    return jsonify({"message": "All ads deleted successfully"}), 200


#---------------- Application Information -------------------------#

#1. update clicks per ad in a spesific app
@ad_sdk_blueprint.route('/ad_sdk/<ad_id>/click', methods=['POST'])
def record_ad_click(ad_id):  
    package_name = request.args.get("package_name")
    if not package_name:
        return jsonify({"error": "Missing package_name parameter"}), 400
    
    db = MongoConnectionManager.get_db()
    stats_collection = db["AdClickStats"]
    ads_collection = db["Ads"]
    now = datetime.datetime.utcnow()

    try:
        ad_doc = ads_collection.find_one({"_id": ad_id})
        ad_name = ad_doc["name"] if ad_doc and "name" in ad_doc else "Unknown Ad"
        category = ad_doc["category"] if ad_doc and "category" in ad_doc else "Unknown"

        result = stats_collection.update_one(
            {"ad_id": ad_id, "package_name": package_name},
            {
                "$inc": {"clicks_count": 1},
                "$setOnInsert": {
                    "views_count": 0,
                    "completed_views_count": 0,
                    "created_at": now,
                    "ad_name": ad_name,
                    "category": category
                },
                "$set": {
                    "last_clicked_at": now,
                    "ad_name": ad_name,
                    "category": category
                }
            },
            upsert=True
        )

        return jsonify({
            "message": "Click recorded successfully",
            "upserted": result.upserted_id is not None
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#2 . Update views count 
@ad_sdk_blueprint.route('/ad_sdk/<ad_id>/view', methods=['POST'])
def record_ad_view(ad_id):
    """
    Record a view for a specific ad in a specific app
    ---
    parameters:
      - name: ad_id
        in: path
        type: string
        required: true
        description: The ID of the ad
      - name: package_name
        in: query
        type: string
        required: true
        description: The app's package name reporting the view
      - name: category
        in: query
        type: string
        required: true
        description: The ad's category (Hotel, Restaurant, etc.)
    responses:
      200:
        description: View recorded successfully
      400:
        description: Missing package_name parameter
      500:
        description: Internal server error
    """

    package_name = request.args.get("package_name")
    if not package_name:
        return jsonify({"error": "Missing package_name parameter"}), 400
    
    category = request.args.get("category")
    if not category:
        return jsonify({"error": "Missing category parameter"}), 400
    
    print("===== RECORD VIEW START =====")
    print("ad_id:", ad_id)
    print("package_name:", package_name)
    print("category:", category)
    
    db = MongoConnectionManager.get_db()
    stats_collection = db["AdClickStats"]
    ads_collection = db["Ads"]

    now = datetime.datetime.utcnow()

    try:
        ad_doc = ads_collection.find_one({"_id": ad_id})
        ad_name = ad_doc["name"] if ad_doc and "name" in ad_doc else "Unknown Ad"

        result = stats_collection.update_one(
            {"ad_id": ad_id, "package_name": package_name, "category": category},
            {
                "$inc": {"views_count": 1},
                "$setOnInsert": {
                    "clicks_count": 0,
                    "completed_views_count": 0,
                    "created_at": now,
                    "ad_name": ad_name,
                    "category": category
 
                },
                "$set": {
                "ad_name": ad_name,
                "category": category

                }

            },
            upsert=True
        )

        return jsonify({
            "message": "View recorded successfully",
            "upserted": result.upserted_id is not None
        }), 200

    except Exception as e:
        print("⚠️ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

#3 Update - for ads videos - count of completed views
@ad_sdk_blueprint.route('/ad_sdk/<ad_id>/view/completed', methods=['POST'])
def record_completed_view(ad_id):
    """
    Record a completed view for a video ad in a specific app
    ---
    parameters:
      - name: ad_id
        in: path
        type: string
        required: true
        description: The ID of the ad
      - name: package_name
        in: query
        type: string
        required: true
        description: The app's package name reporting the completed view
      - name: category
        in: query
        type: string
        required: true
        description: The ad's category (Hotel, Restaurant, etc.)
    responses:
      200:
        description: Completed view recorded successfully
      400:
        description: Missing package_name parameter
      500:
        description: Internal server error
    """
    package_name = request.args.get("package_name")
    if not package_name:
        return jsonify({"error": "Missing package_name parameter"}), 400

    db = MongoConnectionManager.get_db()
    stats_collection = db["AdClickStats"]
    ads_collection = db["Ads"]

    now = datetime.datetime.utcnow()

    try:
        ad_doc = ads_collection.find_one({"_id": ad_id})
        ad_name = ad_doc["name"] if ad_doc and "name" in ad_doc else "Unknown Ad"
        category = ad_doc["category"] if ad_doc and "category" in ad_doc else "Unknown"

        result = stats_collection.update_one(
            {"ad_id": ad_id, "package_name": package_name},
            {
                "$inc": {"completed_views_count": 1},
                "$setOnInsert": {
                    "clicks_count": 0,
                    "views_count": 0,
                    "created_at": now,
                    "ad_name": ad_name,
                    "category": category
                },
                "$set": {
                    "ad_name": ad_name,
                    "category": category
                }
            },
            upsert=True
        )

        return jsonify({
            "message": "Completed view recorded successfully",
            "upserted": result.upserted_id is not None
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 4. Get summarized ad stats
@ad_sdk_blueprint.route('/ad_sdk/AdClickStats/summary', methods=['GET'])
def get_ad_click_summary():
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    stats = db["AdClickStats"].aggregate([
        {
            "$group": {
                "_id": None,
                "total_clicks": {"$sum": "$clicks_count"},
                "total_views": {"$sum": "$views_count"},
                "total_completed_views": {"$sum": "$completed_views_count"}
            }
        }
    ])

    result = next(stats, None)
    if not result:
        return jsonify({
            "total_clicks": 0,
            "total_views": 0,
            "total_completed_views": 0
        }), 200

    return jsonify({
        "total_clicks": result["total_clicks"],
        "total_views": result["total_views"],
        "total_completed_views": result["total_completed_views"]
    }), 200
