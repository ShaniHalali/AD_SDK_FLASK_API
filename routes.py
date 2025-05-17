from contrallers.ad_sdk import ad_sdk_blueprint

def initial_routes(app):
    app.register_blueprint(ad_sdk_blueprint)