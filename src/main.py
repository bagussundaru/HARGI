import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.routes.dashboard import dashboard_bp
from src.routes.auth import auth_bp
from src.config import Config

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG

# Enable CORS for all routes
CORS(app, origins=Config.CORS_ORIGINS)

app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/login')
def login_page():
    """Serve login page"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    
    login_path = os.path.join(static_folder_path, 'login.html')
    if os.path.exists(login_path):
        return send_from_directory(static_folder_path, 'login.html')
    else:
        return "login.html not found", 404

@app.route('/dashboard')
def dashboard_page():
    """Serve dashboard page"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404
    
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    else:
        return "index.html not found", 404

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    # Redirect root to login page
    if path == "":
        return send_from_directory(static_folder_path, 'login.html')
    
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Default to login page for unknown routes
        login_path = os.path.join(static_folder_path, 'login.html')
        if os.path.exists(login_path):
            return send_from_directory(static_folder_path, 'login.html')
        else:
            return "login.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
