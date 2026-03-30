from flask import request, jsonify
from app.api import api_bp
from app import db
from app.models.test import Test
from app.models.vehicle import Vehicle
from app.api.auth import token_required


@api_bp.route('/tests', methods=['GET'])
@token_required
def get_tests(current_user):
    vehicle_id = request.args.get('vehicle_id', type=int)
    test_type = request.args.get('type')
    search = request.args.get('search')
    
    query = Test.query.filter_by(is_active=True)
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    
    if test_type:
        query = query.filter_by(test_type=test_type)
    
    if search:
        query = query.filter(Test.name.ilike(f'%{search}%'))
    
    tests = query.order_by(Test.name).all()
    
    return jsonify({
        'tests': [t.to_dict() for t in tests],
        'total': len(tests)
    })


@api_bp.route('/tests/<int:test_id>', methods=['GET'])
@token_required
def get_test(current_user, test_id):
    test = Test.query.get_or_404(test_id)
    return jsonify({'test': test.to_dict()})


@api_bp.route('/tests', methods=['POST'])
@token_required
def create_test(current_user):
    if current_user.role.name != 'Admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'test_type', 'module_name', 'function_name', 'vehicle_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    test = Test(
        name=data['name'],
        test_type=data['test_type'],
        module_name=data['module_name'],
        function_name=data['function_name'],
        description=data.get('description'),
        requires_mac=data.get('requires_mac', False),
        version=data.get('version', '1.0.0'),
        vehicle_id=data['vehicle_id']
    )
    
    db.session.add(test)
    db.session.commit()
    
    return jsonify({
        'message': 'Test created successfully',
        'test': test.to_dict()
    }), 201


@api_bp.route('/tests/<int:test_id>', methods=['PUT'])
@token_required
def update_test(current_user, test_id):
    if current_user.role.name != 'Admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    test = Test.query.get_or_404(test_id)
    data = request.get_json()
    
    if data.get('name'):
        test.name = data['name']
    if data.get('test_type'):
        test.test_type = data['test_type']
    if data.get('module_name'):
        test.module_name = data['module_name']
    if data.get('function_name'):
        test.function_name = data['function_name']
    if 'description' in data:
        test.description = data['description']
    if 'requires_mac' in data:
        test.requires_mac = data['requires_mac']
    if data.get('version'):
        test.version = data['version']
    if 'is_active' in data:
        test.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Test updated successfully',
        'test': test.to_dict()
    })


@api_bp.route('/tests/types', methods=['GET'])
@token_required
def get_test_types(current_user):
    return jsonify({
        'types': ['check', 'read', 'write']
    })
