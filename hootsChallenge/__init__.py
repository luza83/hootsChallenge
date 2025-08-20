import os
from flask import Flask
from .extensions import db
from dotenv import load_dotenv
from .routes import main
load_dotenv()  

def create_app():
    app = Flask(__name__)
    print("✅ Flask app is being created!")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv("APP_KEY")
    db.init_app(app)

    with app.app_context():
        from .models import User
        db.create_all()
    app.register_blueprint(main)

    return app