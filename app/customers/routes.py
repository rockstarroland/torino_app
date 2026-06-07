from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..models import db, Customer
from ..auth.routes import login_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers')
@login_required
def customers_list():
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('customers/customers.html', customers=customers)

@customers_bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        customer = Customer(name=request.form.get('name'), phone=request.form.get('phone'),
                            email=request.form.get('email'), address=request.form.get('address'),
                            notes=request.form.get('notes'))
        db.session.add(customer)
        db.session.commit()
        flash('Customer added!', 'success')
        return redirect(url_for('customers.customers_list'))
    return render_template('customers/add_customer.html')

@customers_bp.route('/customers/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template('customers/customer_detail.html', customer=customer)