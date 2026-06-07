from flask import Blueprint, render_template, redirect, url_for, flash, request
import json
from ..models import db, Estimate, Customer, Series
from ..auth.routes import login_required

estimates_bp = Blueprint('estimates', __name__)

@estimates_bp.route('/estimate/builder', methods=['GET', 'POST'])
@login_required
def estimate_builder():
    if request.method == 'POST':
        flash('Estimate saved!', 'success')
        return redirect(url_for('estimates.estimates_list'))

    series_list = Series.query.order_by(Series.collection, Series.series).all()
    customers = Customer.query.order_by(Customer.name).all()

    return render_template('estimates/estimate_builder.html',
                           series_list=series_list,
                           customers=customers)

@estimates_bp.route('/estimates')
@login_required
def estimates_list():
    estimates = Estimate.query.filter_by(is_archived=False).order_by(Estimate.created_at.desc()).all()
    return render_template('estimates/estimates.html', estimates=estimates)