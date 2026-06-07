from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..models import db, Installer
from ..auth.routes import login_required

installers_bp = Blueprint('installers', __name__)

@installers_bp.route('/installers')
@login_required
def installers_list():
    installers = Installer.query.order_by(Installer.name).all()
    return render_template('installers/installers.html', installers=installers)

@installers_bp.route('/installers/add', methods=['GET', 'POST'])
@login_required
def add_installer():
    if request.method == 'POST':
        installer = Installer(name=request.form.get('name'), phone=request.form.get('phone'),
                              email=request.form.get('email'), notes=request.form.get('notes'))
        db.session.add(installer)
        db.session.commit()
        flash('Installer added!', 'success')
        return redirect(url_for('installers.installers_list'))
    return render_template('installers/add_installer.html')

@installers_bp.route('/installers/<int:installer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_installer(installer_id):
    installer = Installer.query.get_or_404(installer_id)
    if request.method == 'POST':
        installer.name = request.form.get('name')
        installer.phone = request.form.get('phone')
        installer.email = request.form.get('email')
        installer.notes = request.form.get('notes')
        db.session.commit()
        flash('Installer updated!', 'success')
        return redirect(url_for('installers.installers_list'))
    return render_template('installers/edit_installer.html', installer=installer)