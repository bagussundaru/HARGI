from flask import Blueprint, request, jsonify, session
from functools import wraps
import hashlib

auth_bp = Blueprint('auth', __name__)

# Simple user credentials (in production, use database)
USERS = {
    'admin': {
        'password': hashlib.sha256('0ktahermawan#'.encode()).hexdigest(),
        'role': 'admin'
    },
    'user': {
        'password': hashlib.sha256('athiet19'.encode()).hexdigest(),
        'role': 'user'
    }
}

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required', 'authenticated': False}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Hash the provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials
        if username in USERS and USERS[username]['password'] == hashed_password:
            session['user_id'] = username
            session['role'] = USERS[username]['role']
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'username': username,
                    'role': USERS[username]['role']
                },
                'authenticated': True
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({'message': 'Logout successful', 'authenticated': False})

@auth_bp.route('/status', methods=['GET'])
def status():
    """Check authentication status"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'username': session['user_id'],
                'role': session.get('role', 'user')
            }
        })
    else:
        return jsonify({'authenticated': False})

@auth_bp.route('/check', methods=['GET'])
@login_required
def check():
    """Protected route to verify authentication"""
    return jsonify({
        'message': 'Access granted',
        'user': {
            'username': session['user_id'],
            'role': session.get('role', 'user')
        }
    })