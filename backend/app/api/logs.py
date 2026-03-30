from flask import request, jsonify
from app.api import api_bp
from app import db
from app.models.log import Log
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.test import Test
from app.api.auth import token_required
from datetime import datetime


@api_bp.route('/logs', methods=['GET'])
@token_required
def get_logs(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    vehicle_id = request.args.get('vehicle_id', type=int)
    test_id = request.args.get('test_id', type=int)
    status = request.args.get('status')
    vin = request.args.get('vin')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Log.query
    
    if current_user.role.name != 'Admin':
        query = query.filter_by(user_id=current_user.id)
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    if test_id:
        query = query.filter_by(test_id=test_id)
    if status:
        query = query.filter_by(status=status)
    if vin:
        query = query.filter(Log.vin.ilike(f'%{vin}%'))
    if date_from:
        try:
            date_from_dt = datetime.fromisoformat(date_from)
            query = query.filter(Log.created_at >= date_from_dt)
        except ValueError:
            pass
    if date_to:
        try:
            date_to_dt = datetime.fromisoformat(date_to)
            query = query.filter(Log.created_at <= date_to_dt)
        except ValueError:
            pass
    
    pagination = query.order_by(Log.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })


@api_bp.route('/logs/<int:log_id>', methods=['GET'])
@token_required
def get_log(current_user, log_id):
    log = Log.query.get_or_404(log_id)
    
    if current_user.role.name != 'Admin' and log.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'log': log.to_dict()})


@api_bp.route('/logs', methods=['POST'])
@token_required
def create_log(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['vehicle_id', 'test_id', 'status']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    test = Test.query.get(data['test_id'])
    if not test:
        return jsonify({'error': 'Test not found'}), 404
    
    log = Log(
        user_id=current_user.id,
        vehicle_id=data['vehicle_id'],
        test_id=data['test_id'],
        vin=data.get('vin'),
        status=data['status'],
        log_text=data.get('log_text'),
        client_version=data.get('client_version'),
        client_platform=data.get('client_platform'),
        execution_time=data.get('execution_time')
    )
    
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Log created successfully',
        'log': log.to_dict()
    }), 201


@api_bp.route('/logs/stats', methods=['GET'])
@token_required
def get_log_stats(current_user):
    if current_user.role.name != 'Admin':
        base_query = Log.query.filter_by(user_id=current_user.id)
    else:
        base_query = Log.query
    
    total_logs = base_query.count()
    pass_count = base_query.filter_by(status='PASS').count()
    fail_count = base_query.filter_by(status='FAIL').count()
    
    return jsonify({
        'total': total_logs,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'pass_rate': round((pass_count / total_logs * 100), 2) if total_logs > 0 else 0
    })
