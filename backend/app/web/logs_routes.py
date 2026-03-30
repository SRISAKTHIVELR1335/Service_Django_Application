from flask import render_template, request
from flask_login import login_required, current_user
from app.web import web_bp
from app.models.log import Log
from app.models.vehicle import Vehicle
from app.models.test import Test
from app.models.user import User
from datetime import datetime


@web_bp.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
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
    
    vehicles = Vehicle.query.filter_by(is_active=True).order_by(Vehicle.name).all()
    tests_list = Test.query.filter_by(is_active=True).order_by(Test.name).all()
    users = []
    if current_user.role.name == 'Admin':
        users = User.query.filter_by(is_active=True).order_by(User.email).all()
    
    return render_template('logs.html',
                         logs=pagination.items,
                         pagination=pagination,
                         vehicles=vehicles,
                         tests=tests_list,
                         users=users,
                         filters={
                             'user_id': user_id,
                             'vehicle_id': vehicle_id,
                             'test_id': test_id,
                             'status': status,
                             'vin': vin,
                             'date_from': date_from,
                             'date_to': date_to
                         })
