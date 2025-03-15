from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    with app.app_context():
        from .routes import api_bp
        app.register_blueprint(api_bp)

    return app
