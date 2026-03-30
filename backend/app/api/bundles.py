from flask import request, jsonify, send_file
from app.api import api_bp
from app import db
from app.models.bundle import Bundle
from app.models.vehicle import Vehicle
from app.api.auth import token_required
import os


@api_bp.route('/testbundle', methods=['GET'])
@token_required
def get_bundles(current_user):
    vehicle_id = request.args.get('vehicle_id', type=int)
    
    query = Bundle.query.filter_by(is_active=True)
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    
    bundles = query.order_by(Bundle.created_at.desc()).all()
    
    return jsonify({
        'bundles': [b.to_dict() for b in bundles],
        'total': len(bundles)
    })


@api_bp.route('/testbundle/<int:bundle_id>', methods=['GET'])
@token_required
def get_bundle(current_user, bundle_id):
    bundle = Bundle.query.get_or_404(bundle_id)
    return jsonify({'bundle': bundle.to_dict()})


@api_bp.route('/testbundle/latest/<int:vehicle_id>', methods=['GET'])
@token_required
def get_latest_bundle(current_user, vehicle_id):
    bundle = Bundle.query.filter_by(
        vehicle_id=vehicle_id,
        is_active=True
    ).order_by(Bundle.created_at.desc()).first()
    
    if not bundle:
        return jsonify({'error': 'No bundle found for this vehicle'}), 404
    
    return jsonify({'bundle': bundle.to_dict()})


@api_bp.route('/testbundle/download/<int:bundle_id>', methods=['GET'])
@token_required
def download_bundle(current_user, bundle_id):
    bundle = Bundle.query.get_or_404(bundle_id)
    
    if not bundle.file_path or not os.path.exists(bundle.file_path):
        return jsonify({'error': 'Bundle file not found'}), 404
    
    return send_file(
        bundle.file_path,
        as_attachment=True,
        download_name=f'{bundle.name}_v{bundle.version}.zip'
    )


@api_bp.route('/testbundle', methods=['POST'])
@token_required
def create_bundle(current_user):
    if current_user.role.name != 'Admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'version', 'vehicle_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    bundle = Bundle(
        name=data['name'],
        version=data['version'],
        vehicle_id=data['vehicle_id'],
        file_path=data.get('file_path'),
        file_size=data.get('file_size'),
        checksum=data.get('checksum'),
        description=data.get('description')
    )
    
    db.session.add(bundle)
    db.session.commit()
    
    return jsonify({
        'message': 'Bundle created successfully',
        'bundle': bundle.to_dict()
    }), 201


@api_bp.route('/testbundle/check-version', methods=['POST'])
@token_required
def check_bundle_version(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    vehicle_id = data.get('vehicle_id')
    current_version = data.get('current_version')
    
    if not vehicle_id:
        return jsonify({'error': 'vehicle_id is required'}), 400
    
    latest_bundle = Bundle.query.filter_by(
        vehicle_id=vehicle_id,
        is_active=True
    ).order_by(Bundle.created_at.desc()).first()
    
    if not latest_bundle:
        return jsonify({
            'update_available': False,
            'message': 'No bundle available'
        })
    
    update_available = current_version != latest_bundle.version if current_version else True
    
    return jsonify({
        'update_available': update_available,
        'latest_version': latest_bundle.version,
        'bundle': latest_bundle.to_dict() if update_available else None
    })
