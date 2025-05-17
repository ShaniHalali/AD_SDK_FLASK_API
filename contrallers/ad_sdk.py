from flask import Blueprint, request, jsonify
from mongodb_connection_manager import MongoConnectionManager
import datetime
from bson.objectid import ObjectId
import uuid

ad_sdk_blueprint = Blueprint('ad_sdk', __name__)

#1.create a new ad
@ad_sdk_blueprint.route('/ad_sdk', methods=['POST'])
def create_ad():
    """Create a new ad 
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

    # Check if the database connection is successful
    if db is None:
        return jsonify({"error": "Database connection error"}), 500
    
    # Check if requist data is valid
    if not all(key in data for key in ('package_name', 'name', 'dicription', 'ad_type', 'beginning_date', 'expiration_date', 'ad_location', 'ad_link')):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if data is valid
    try:
        #parse dates
        beginning_date = datetime.datetime.strptime(data['beginning_date'], '%Y-%m-%d %H:%M:%S')
        expiration_date = datetime.datetime.strptime(data['expiration_date'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    
    if beginning_date > expiration_date:
        return jsonify({"error": "Beginning date must be before expiration date"}), 400
    
    # Create the ad item
    ad_item = {
        "_id": str(uuid.uuid4()),
        "name": data['name'],
        "dicription": data['dicription'],
        "ad_type": data['ad_type'],
        "beginning_date": beginning_date,
        "expiration_date": expiration_date,
        "ad_location": data['ad_location'],
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now()
    }

    # Insert the ad item into the database
    package_collection = db[data['package_name']]
    package_collection.insert_one(ad_item)
    
    
    return jsonify({"message": "Ad created successfully",'_id': ad_item['_id']}), 201

# 2. Get all ads for package name
@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_ads(package_name):
    """
    Get all ads for a specific package name
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
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



#3.get a ads by id for package name
@ad_sdk_blueprint.route('/ad_sdk/<package_name>/<ad_id>', methods=['GET'])
def get_ad_details(package_name, ad_id):
    """
    Get ad details by ID
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: Name of the package
      - name: ad_id
        in: path
        required: true
        description: ID of the ad
    responses:
      200:
        description: Ad details
      404:
        description: Ad not found
    """
    db = MongoConnectionManager.get_db()
    
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    package_collection = db[package_name]
    if package_collection is None:
        return jsonify({"error": "Package not found"}), 404

    # Find specific ad by ID
    for ad in package_collection.find({"_id": str(ad_id)}):
        ad['_id'] = str(ad['_id'])
        return jsonify(ad), 200
    
    if ad is None:
        return jsonify({"error": "Ad not found"}), 404

    return jsonify(ad), 200





#4 update a ad by id for package name
@ad_sdk_blueprint.route('/ad_sdk/<package_name>/<ad_id>', methods=['PUT'])
def update_ad(package_name, ad_id):
    """
    Update ad details by ID
    ---
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: Name of the package
      - name: ad_id
        in: path
        required: true
        description: ID of the ad
      - name: ad
        in: body
        required: true
        description: Ad object that needs to be updated
        schema:
          id: Ad
          properties:
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
      200:
        description: Ad updated successfully
      400:
        description: Invalid input or missing fields
      404:
        description: Ad not found or package not found

    """
    data = request.get_json()
    new_expiration_date = None
    new_beginning_date = None
    db = MongoConnectionManager.get_db()
    
    if db is None:
        return jsonify({"error": "Database connection error"}), 500
    
    if 'expiration_date' in data:
        new_expiration_date = data.get['expiration_date']
    if 'beginning_date' in data:
        new_beginning_date = data.get['beginning_date']

    if not 'expiration_date' in data and not 'beginning_date' in data:
        return jsonify({"error": "No data provied"}), 400 
    
    try:
        #parse new dates
        if new_expiration_date:
            new_expiration_date = datetime.datetime.strptime(new_expiration_date, '%Y-%m-%d %H:%M:%S')
        if new_beginning_date:
            new_beginning_date = datetime.datetime.strptime(new_beginning_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400
    
    if new_beginning_date and new_expiration_date and new_beginning_date > new_expiration_date:
        return jsonify({"error": "Beginning date must be before expiration date"}), 400

    package_collection = db[package_name]
    if package_collection is None:
        return jsonify({"error": "Package not found"}), 404
    
    #find and update the ad
    ad = package_collection.find_one({"_id": ad_id})
    if ad:
        if new_beginning_date:
            if new_beginning_date > new_expiration_date:
                return jsonify({"error": "Beginning date must be before expiration date"}), 400
            ad['beginning_date'] = new_beginning_date
        if new_expiration_date:
            if new_expiration_date < new_beginning_date:
                return jsonify({"error": "Expiration date must be after beginning date"}), 400
            ad['expiration_date'] = new_expiration_date

        package_collection.update_one(
            {"_id": ad['_id']},
            {"$set": ad}
        )
        return jsonify({"message": "Ad updated successfully"}), 200      

    return jsonify({"error": "Ad not found"}), 404  






# 5. Get all active ads for package name and date
@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_ad_by_date(package_name):
    """
    Get all active ads by a specific date
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        description: Name of the package
      - name: date
        in: query
        type: string
        required: true
        description: Date (format: YYYY-MM-DD)
    responses:
      200:
        description: List of active ads by date
      400:
        description: Invalid input
      404:
        description: Package not found
    """
    date_str = request.args.get('date', "")
    db = MongoConnectionManager.get_db()
    
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    try:
        specified_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format (use YYYY-MM-DD)"}), 400

    package_collection = db[package_name]
    if package_collection is None:
        return jsonify({"error": "Package not found"}), 404

    # Filter ads that are active on the specified date
    active_ads_by_date = list(package_collection.find({
        "expiration_date": {"$gte": specified_date},
        "beginning_date": {"$lte": specified_date}
    }))

    return jsonify(active_ads_by_date), 200
   



# 6. Get all active ads for package name for location
@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_ad_by_location(package_name):
    """
    Get all active ads by a specific location
    ---
    parameters:
      - name: package_name
        in: path
        required: true
        description: Name of the package
      - name: location
        in: query
        type: string
        required: true
        description: Location of the ad
    responses:
      200:
        description: List of active ads by location
      400:
        description: Invalid input
      404:
        description: Package not found
    """
    location = request.args.get('location', "")
    db = MongoConnectionManager.get_db()
    
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    package_collection = db[package_name]
    if package_collection is None:
        return jsonify({"error": "Package not found"}), 404

    # Filter active ads by location
    now = datetime.datetime.now()
    active_ads_by_location = list(package_collection.find({
        "expiration_date": {"$gte": now},
        "beginning_date": {"$lte": now},
        "ad_location": location
    }))

    # Convert ObjectId to string
    for ad in active_ads_by_location:
        ad['_id'] = str(ad['_id'])

    return jsonify(active_ads_by_location), 200



#7 Delete all ads 
@ad_sdk_blueprint.route('/ad_sdk', methods=['DELETE'])
def delete_all_ads(package_name):
    """
    Delete all ads 
    ---
    responses:
        200:
            description: All ads deleted successfully
      """
    db = MongoConnectionManager.get_db()
    
    if db is None:
        return jsonify({"error": "Database connection error"}), 500

    # Delete all ads from the database
    for collection_name in db.list_collection_names():
        db[collection_name].delete_many({})
    return jsonify({"message": "All ads deleted successfully"}), 200

 

#get all active ads for package name
@ad_sdk_blueprint.route('/ad_sdk/<package_name>', methods=['GET'])
def get_active_ads(package_name):
    """
    parameters:
      - name: package_name
        in: path
        type: string
        required: true
        description: Name of the package
    responses:
      200:
        description: List of active ads    

    """
    current = datetime.datetime.now()
    db = MongoConnectionManager.get_db()
    if db is None:
        return jsonify({"error": "Database connection error"}), 500
    package_collection = db[package_name]
    if package_collection is None:
        return jsonify({"error": "Package not found"}), 404
    
    #Find ads that are active
    active_ads = list(package_collection.find({
        "expiration_date": {"$gte": current},
        "beginning_date": {"$lte": current}
    }))
    return jsonify(active_ads), 200

