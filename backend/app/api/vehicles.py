from flask import request, jsonify
from app.api import api_bp
from app import db
from app.models.vehicle import Vehicle
from app.api.auth import token_required


@api_bp.route('/vehicles', methods=['GET'])
@token_required
def get_vehicles(current_user):
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Vehicle.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Vehicle.name.ilike(f'%{search}%'))
    
    vehicles = query.order_by(Vehicle.name).all()
    
    return jsonify({
        'vehicles': [v.to_dict() for v in vehicles],
        'total': len(vehicles)
    })


@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@token_required
def get_vehicle(current_user, vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify({'vehicle': vehicle.to_dict()})


@api_bp.route('/vehicles', methods=['POST'])
@token_required
def create_vehicle(current_user):
    if current_user.role.name != 'Admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('name') or not data.get('category'):
        return jsonify({'error': 'Name and category are required'}), 400
    
    vehicle = Vehicle(
        name=data['name'],
        category=data['category'],
        description=data.get('description'),
        vin_pattern=data.get('vin_pattern'),
        image_url=data.get('image_url')
    )
    
    db.session.add(vehicle)
    db.session.commit()
    
    return jsonify({
        'message': 'Vehicle created successfully',
        'vehicle': vehicle.to_dict()
    }), 201


@api_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@token_required
def update_vehicle(current_user, vehicle_id):
    if current_user.role.name != 'Admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    
    if data.get('name'):
        vehicle.name = data['name']
    if data.get('category'):
        vehicle.category = data['category']
    if 'description' in data:
        vehicle.description = data['description']
    if 'vin_pattern' in data:
        vehicle.vin_pattern = data['vin_pattern']
    if 'image_url' in data:
        vehicle.image_url = data['image_url']
    if 'is_active' in data:
        vehicle.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Vehicle updated successfully',
        'vehicle': vehicle.to_dict()
    })


@api_bp.route('/vehicles/categories', methods=['GET'])
@token_required
def get_vehicle_categories(current_user):
    categories = db.session.query(Vehicle.category).distinct().all()
    return jsonify({
        'categories': [c[0] for c in categories if c[0]]
    })
