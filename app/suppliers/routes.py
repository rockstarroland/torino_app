from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..models import db, Supplier
from ..auth.routes import login_required

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/suppliers')
@login_required
def suppliers_list():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('suppliers/suppliers.html', suppliers=suppliers)

@suppliers_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        collection = request.form.get('collection', '').strip() or None
        if name:
            if Supplier.query.filter_by(name=name).first():
                flash('Supplier already exists!', 'danger')
            else:
                supplier = Supplier(name=name, collection=collection)
                db.session.add(supplier)
                db.session.commit()
                flash('Supplier added!', 'success')
                return redirect(url_for('suppliers.suppliers_list'))
    return render_template('suppliers/add_supplier.html')

@suppliers_bp.route('/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    if request.method == 'POST':
        supplier.name = request.form.get('name', supplier.name).strip()
        supplier.collection = request.form.get('collection', '').strip() or None
        db.session.commit()
        flash('Supplier updated!', 'success')
        return redirect(url_for('suppliers.suppliers_list'))
    return render_template('suppliers/edit_supplier.html', supplier=supplier)