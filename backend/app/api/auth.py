from flask import request, jsonify
from app.api import api_bp
from app import db, bcrypt
from app.models.user import User
from app.models.role import Role
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            secret = os.environ.get('SESSION_SECRET', 'nirix-secret-key')
            data = jwt.decode(token, secret, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            if not current_user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 403
            if not current_user.is_approved:
                return jsonify({'error': 'Account pending approval'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_approved:
        return jsonify({'error': 'Account pending approval'}), 403
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    secret = os.environ.get('SESSION_SECRET', 'nirix-secret-key')
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'role': user.role.name if user.role else 'Viewer',
        'exp': datetime.utcnow() + timedelta(days=7)
    }, secret, algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    })


@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    technician_role = Role.query.filter_by(name='Technician').first()
    if not technician_role:
        technician_role = Role(name='Technician', description='Field technician with test execution rights')
        db.session.add(technician_role)
        db.session.commit()
    
    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role_id=technician_role.id,
        is_approved=False
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful. Please wait for admin approval.',
        'user': user.to_dict()
    }), 201


@api_bp.route('/auth/me', methods=['GET'])
@token_required
def api_me(current_user):
    return jsonify({'user': current_user.to_dict()})


@api_bp.route('/auth/refresh', methods=['POST'])
@token_required
def api_refresh_token(current_user):
    secret = os.environ.get('SESSION_SECRET', 'nirix-secret-key')
    token = jwt.encode({
        'user_id': current_user.id,
        'email': current_user.email,
        'role': current_user.role.name if current_user.role else 'Viewer',
        'exp': datetime.utcnow() + timedelta(days=7)
    }, secret, algorithm='HS256')
    
    return jsonify({
        'message': 'Token refreshed',
        'token': token
    })
