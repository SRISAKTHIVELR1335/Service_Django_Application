from flask import request, jsonify
from app.api import api_bp
from app import db
from app.models.user import User
from app.api.auth import token_required


@api_bp.route('/settings/theme', methods=['GET'])
@token_required
def get_theme(current_user):
    return jsonify({
        'theme': current_user.theme_preference
    })


@api_bp.route('/settings/theme', methods=['PUT'])
@token_required
def update_theme(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    theme = data.get('theme')
    if theme not in ['light', 'dark']:
        return jsonify({'error': 'Invalid theme. Must be light or dark'}), 400
    
    current_user.theme_preference = theme
    db.session.commit()
    
    return jsonify({
        'message': 'Theme updated successfully',
        'theme': current_user.theme_preference
    })


@api_bp.route('/settings/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'user': current_user.to_dict()
    })


@api_bp.route('/settings/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if data.get('first_name'):
        current_user.first_name = data['first_name']
    if data.get('last_name'):
        current_user.last_name = data['last_name']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    })


@api_bp.route('/settings/password', methods=['PUT'])
@token_required
def change_password(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password are required'}), 400
    
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'message': 'Password changed successfully'
    })


@api_bp.route('/settings/can-drivers', methods=['GET'])
def get_can_driver_urls():
    return jsonify({
        'drivers': [
            {
                'name': 'PCAN',
                'vendor': 'Peak Systems',
                'url': 'https://www.peak-system.com/PCAN-USB.199.0.html',
                'description': 'PEAK CAN USB Interface Driver'
            },
            {
                'name': 'Kvaser',
                'vendor': 'Kvaser',
                'url': 'https://www.kvaser.com/downloads/',
                'description': 'Kvaser CAN Interface Driver'
            },
            {
                'name': 'Vector',
                'vendor': 'Vector Informatik',
                'url': 'https://www.vector.com/int/en/products/products-a-z/software/xl-driver-library/',
                'description': 'Vector XL Driver Library'
            }
        ]
    })
