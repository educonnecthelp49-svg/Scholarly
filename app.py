import eventlet
eventlet.monkey_patch()

import os
from dotenv import load_dotenv
import logging
from datetime import timedelta
from flask import Flask
from flask_socketio import SocketIO
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///school_social.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize the app with the extension
db.init_app(app)


with app.app_context():
    # Drop all tables
    db.drop_all()
    db.create_all()

    # Create default admin user
    admin_user = User(
        username="school.admin",
        email="test@example.com",
        password_hash=generate_password_hash("123"),
        points=0,
        is_admin=True,
        full_name="School Administrator"
    )

    db.session.add(admin_user)
    db.session.commit()
    print("Database cleared and default admin user created.")

# Import routes after app initialization
from routes import *

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)