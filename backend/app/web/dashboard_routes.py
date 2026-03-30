from flask import render_template, request
from flask_login import login_required, current_user
from app.web import web_bp
from app.models.vehicle import Vehicle
from app.models.log import Log


@web_bp.route('/dashboard')
@login_required
def dashboard():

    # Read filters
    category = request.args.get('category', 'All Models')
    search = request.args.get('search', "")

    # Allowed categories (final)
    categories = ["MOTOR CYCLE", "Scooter", "3-Wheeler"]

    # Base query
    query = Vehicle.query.filter_by(is_active=True)

    # Category Filter
    if category and category != "All Models":
        query = query.filter_by(category=category)

    # Search Filter
    if search:
        query = query.filter(Vehicle.name.ilike(f"%{search}%"))

    # Fetch vehicles
    vehicles = query.order_by(Vehicle.name).all()

    # Stats tracking
    if current_user.role.name == 'Admin':
        total_logs = Log.query.count()
        pass_count = Log.query.filter_by(status='PASS').count()
        fail_count = Log.query.filter_by(status='FAIL').count()
    else:
        total_logs = Log.query.filter_by(user_id=current_user.id).count()
        pass_count = Log.query.filter_by(user_id=current_user.id, status='PASS').count()
        fail_count = Log.query.filter_by(user_id=current_user.id, status='FAIL').count()

    stats = {
        "total_vehicles": len(vehicles),
        "total_logs": total_logs,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": round((pass_count / total_logs * 100), 2) if total_logs else 0
    }

    return render_template(
        "dashboard.html",
        vehicles=vehicles,
        categories=categories,
        selected_category=category,
        search=search,
        stats=stats
    )
