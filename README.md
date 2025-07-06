# 🚀 Flask Ads SDK Server

This is the backend server for the **Ads SDK**, built with Flask and MongoDB.  
It provides a set of RESTful API endpoints to manage, filter, and track smart ads by location and category – and is hosted on **Vercel**.

---

## 🌐 Live API (Hosted on Vercel)

🟢 Base URL:  https://ad-sdk-flask-api.vercel.app/

---

## 🧱 Tech Stack

- **Python** – Core backend language
- **Flask** – Web framework for building RESTful APIs
- **Flask-CORS** – Cross-Origin Resource Sharing for handling frontend/backend integration
- **Flasgger** – Swagger UI integration for automatic API documentation
- **PyMongo** – MongoDB driver to connect with MongoDB Atlas
- **python-dotenv** – Environment variable management (e.g., DB connection string)

---

## 📘 API Endpoints

### 🔧 Core Ad Management

| Endpoint                              | Method | Description                                                  |
|---------------------------------------|--------|--------------------------------------------------------------|
| `/ad_sdk`                             | POST   | Create a new ad                                              |
| `/ad_sdk/<package_name>/all`          | GET    | Get all ads for a package                                    |
| `/ad_sdk/<package_name>/<ad_id>`      | GET    | Get specific ad by ID                                        |
| `/ad_sdk/<package_name>/<ad_id>`      | PUT    | Update ad details by ID                                      |
| `/ad_sdk/<package_name>`              | GET    | Filter ads by `date`, `location`, or `category`              |
| `/ad_sdk`                             | DELETE | Delete all ads (dev/test use)                                |

---

### 📊 Tracking & Analytics

| Endpoint                                                    | Method | Description                                                     |
|-------------------------------------------------------------|--------|-----------------------------------------------------------------|
| `/ad_sdk/<ad_id>/click?package_name=...`                    | POST   | Record a click for the ad                                       |
| `/ad_sdk/<ad_id>/view?package_name=...&category=...`        | POST   | Record a view for the ad                                        |
| `/ad_sdk/<ad_id>/view/completed?package_name=...`           | POST   | Record a completed view (for video ads)                         |
| `/ad_sdk/AdClickStats/summary`                              | GET    | Get global stats: total clicks, views, completed views          |

## 🔗 Related Projects
- [SDK ADS Android Library](https://github.com/ShaniHalali/SDK_ADS_Android_Library)   
  Android library that displays dynamic ads based on city and category.  
  Includes built-in support for video/image ads, event tracking, and developer-friendly integration.
  
- [Ads Dashboard Portal](https://portal-ads-dashboard-react-typejs.vercel.app/)
A dashboard interface to visualize aggregated ad performance (clicks, views, completed views) in real time.   
You can find more details and documentation on [*Ads portal repository*](https://github.com/ShaniHalali/Portal_ads_dashboard_REACT_TYPEJS)



---

## 🧪 Example Request: Create Ad
http
POST https://your-vercel-project-name.vercel.app/ad_sdk
Content-Type: application/json

```
{
  "package_name": "Ads",
  "name": "TAIZU",
  "description": "TAIZU – מטבח אסייתי מודרני עטור פרסים בניצוחו של השף יובל בן נריה, עם מנות שף מוקפדות וחוויה קולינרית יוצאת דופן.",
  "ad_type": "video",
  "beginning_date": "2025-08-14 00:00:00",
  "expiration_date": "2025-08-19 23:59:59",
  "ad_location": "Tel Aviv",
  "ad_link": "https://www.taizu.co.il/",
  "category": "Restaurant",
  "ad_image_link": "https://firebasestorage.googleapis.com/v0/b/adssdkvideosandphotos.firebasestorage.app/o/video%2FTaizo%20Resturant.mp4?alt=media&token=312713cf-2a6c-4891-b485-ea782e94ee7f"
}
```
## Project Structure
```bash
📁 AD_SDK_Flask_Server/
├── app.py                         # Main Flask application entry point
├── routes.py                      # Route registration (optional use if needed)
├── controllers/
│   └── ad_sdk.py                  # Blueprint containing all ad-related endpoints
├── mongodb_connection_manager.py  # MongoDB connection handler using pymongo
├── requirements.txt               # Python package dependencies
├── runtime.txt                    # Specifies Python version for Vercel (e.g. python-3.10)
├── vercel.json                    # Vercel deployment configuration (builds & routes)
├── .gitignore                     # Files/folders excluded from Git tracking
├── .idea/                         # PyCharm/VSCode settings (not required for deployment)
```

## 📄 License

This project is licensed under the MIT License © 2025 Shani Halali



