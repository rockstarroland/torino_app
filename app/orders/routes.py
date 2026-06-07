from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..models import db, PurchaseOrder
from ..auth.routes import login_required

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
@login_required
def orders_list():
    status = request.args.get('status')
    if status:
        purchase_orders = PurchaseOrder.query.filter_by(status=status, is_archived=False).order_by(PurchaseOrder.created_at.desc()).all()
    else:
        purchase_orders = PurchaseOrder.query.filter_by(is_archived=False).order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('orders/orders.html', purchase_orders=purchase_orders)

@orders_bp.route('/orders/<int:po_id>')
@login_required
def order_detail(po_id):
    po = PurchaseOrder.query.get_or_404(po_id)
    return render_template('orders/order_detail.html', po=po)

@orders_bp.route('/orders/<int:po_id>/update', methods=['POST'])
@login_required
def update_order(po_id):
    po = PurchaseOrder.query.get_or_404(po_id)
    po.status = request.form.get('status', po.status)
    if request.form.get('arrival_date'):
        po.arrival_date = datetime.strptime(request.form.get('arrival_date'), '%Y-%m-%d').date()
    db.session.commit()
    flash('Order updated!', 'success')
    return redirect(url_for('orders.order_detail', po_id=po.id))