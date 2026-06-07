from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from datetime import datetime, date, timedelta
from ..models import db, Project, ProjectInstaller, ProjectETA, PurchaseOrder, Estimate, Installer, Supplier, Customer
from ..utils import prepare_work_order_data, ORDER_STATUSES, PROJECT_STATUSES
from ..auth.routes import login_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects')
@login_required
def projects_list():
    projects = Project.query.filter_by(is_archived=False).order_by(Project.created_at.desc()).all()
    return render_template('projects/projects.html', projects=projects)

@projects_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    installers = Installer.query.order_by(Installer.name).all()
    return render_template('projects/project_detail.html', project=project, installers=installers)

@projects_bp.route('/projects/calendar')
@login_required
def project_calendar():
    suppliers = Supplier.query.order_by(Supplier.name).all()
    return render_template('projects/project_calendar.html',
                           suppliers=suppliers,
                           ORDER_STATUSES=ORDER_STATUSES,
                           PROJECT_STATUSES=PROJECT_STATUSES)

@projects_bp.route('/projects/calendar/data')
@login_required
def project_calendar_data():
    events = []

    # Projects / Installs (orange)
    for p in Project.query.filter_by(is_archived=False).all():
        event_date = p.install_scheduled_date or p.start_date
        if not event_date:
            continue
        title = f"🛠️ {p.project_name or 'Installation'}"
        if p.customer_name:
            title += f" — {p.customer_name}"
        if p.assigned_installers:
            names = ", ".join(pi.installer.name for pi in p.assigned_installers)
            title += f" ({names})"
        if p.status:
            title += f" [{p.status}]"
        events.append({
            'id': f"project-{p.id}",
            'title': title,
            'start': event_date.isoformat(),
            'end': (p.finish_date + timedelta(days=1)).isoformat() if p.finish_date else None,
            'allDay': True,
            'backgroundColor': '#f59e0b',
            'borderColor': '#b45309',
            'extendedProps': {
                'type': 'project',
                'status': p.status,
                'customer': p.customer_name
            }
        })

    # Purchase Orders (green)
    for po in PurchaseOrder.query.filter_by(is_archived=False).all():
        if not po.arrival_date:
            continue
        title = f"📦 Order {po.po_number}"
        if po.customer_name:
            title += f" — {po.customer_name}"
        if po.status:
            title += f" [{po.status}]"
        events.append({
            'id': f"po-{po.id}",
            'title': title,
            'start': po.arrival_date.isoformat(),
            'allDay': True,
            'backgroundColor': '#10b981',
            'borderColor': '#047857',
            'extendedProps': {
                'type': 'order',
                'status': po.status,
                'customer': po.customer_name
            }
        })

    # ETAs (green)
    for eta in ProjectETA.query.all():
        project = Project.query.get(eta.project_id)
        if project and project.is_archived:
            continue
        if not eta.eta_date:
            continue
        project_name = project.project_name or project.customer_name or "Project" if project else "Project"
        title = f"📦 {project_name} — {eta.supplier} Tiles"
        if eta.notes:
            title += f" ({eta.notes})"
        if eta.status:
            title += f" [{eta.status}]"
        events.append({
            'id': f"eta-{eta.id}",
            'title': title,
            'start': eta.eta_date.isoformat(),
            'allDay': True,
            'backgroundColor': '#10b981',
            'borderColor': '#047857',
            'extendedProps': {
                'type': 'eta',
                'status': eta.status,
                'customer': project.customer_name if project else None,
                'supplier': eta.supplier
            }
        })

    return jsonify(events)

@projects_bp.route('/projects/<int:project_id>/workorder')
@login_required
def project_workorder(project_id):
    project = Project.query.get_or_404(project_id)
    work_data = prepare_work_order_data(project, Estimate, PurchaseOrder, Customer, INSTALLER_LABOUR_RATE)
    return render_template('projects/work_order.html', project=project, work_data=work_data)