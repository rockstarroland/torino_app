from flask import Blueprint, render_template, redirect, url_for, flash, session
from functools import wraps
from ..models import db, User, PurchaseOrder, ProjectETA, Project, Supplier, TileVariant, Estimate
from datetime import date
from ..auth.routes import login_required

core_bp = Blueprint('core', __name__)

@core_bp.context_processor
def inject_status_lists():
    from ..utils import ORDER_STATUSES, PROJECT_STATUSES
    return {
        'ORDER_STATUSES': ORDER_STATUSES,
        'PROJECT_STATUSES': PROJECT_STATUSES
    }

@core_bp.route('/debug')
@login_required
def debug():
    data = {
        "Series count": Series.query.count(),
        "TileVariant count": TileVariant.query.count(),
    }
    return jsonify(data)

@core_bp.route('/')
@login_required
def index():
    today = date.today()
    pending = PurchaseOrder.query.filter_by(status='To be ordered', is_archived=False).count()
    # Add the rest of your original dashboard logic here
    return render_template('core/index.html')

@core_bp.route('/login', methods=['GET', 'POST'])
def login():
    return redirect(url_for('auth.login'))

@core_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))