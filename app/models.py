from datetime import datetime, date
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(150))
    address = db.Column(db.String(300))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Installer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(150))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    collection = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100), nullable=False)
    supplier = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    variants = db.relationship('TileVariant', backref='series', lazy=True, cascade="all, delete-orphan")

class TileVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    finish = db.Column(db.String(50))
    color = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    sqft_per_box = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), default='each')
    photo = db.Column(db.String(200))
    sample_status = db.Column(db.String(50), default='In Store')
    checked_out_to_name = db.Column(db.String(150))
    checked_out_to_phone = db.Column(db.String(30))
    checked_out_date = db.Column(db.DateTime)
    arrival_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Estimate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    customer_name = db.Column(db.String(150))
    customer_phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.Text)
    is_archived = db.Column(db.Boolean, default=False)

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    estimate_id = db.Column(db.Integer, db.ForeignKey('estimate.id'))
    po_number = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(150))
    status = db.Column(db.String(50), default='To be ordered')
    arrival_date = db.Column(db.Date)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', foreign_keys=[project_id], back_populates='purchase_orders')

class ProjectInstaller(db.Model):
    __tablename__ = 'project_installers'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    installer_id = db.Column(db.Integer, db.ForeignKey('installer.id'), nullable=False)
    role = db.Column(db.String(80), default='Tile Installer')
    assigned_date = db.Column(db.Date, default=date.today)
    scheduled_date = db.Column(db.Date, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    finish_date = db.Column(db.Date, nullable=True)
    installer = db.relationship('Installer', backref='project_installations')

class ProjectETA(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    eta_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='Pending')
    received_date = db.Column(db.Date, nullable=True)
    pickup_location = db.Column(db.String(50))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estimate_id = db.Column(db.Integer, db.ForeignKey('estimate.id'))
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=True)
    project_name = db.Column(db.String(200))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    customer_name = db.Column(db.String(150))
    status = db.Column(db.String(50), default='Installer Assigned / Work Order Created')
    deposit_amount = db.Column(db.Float, default=0.0)
    deposit_method = db.Column(db.String(50))
    deposit_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)
    install_scheduled_date = db.Column(db.Date)
    installer_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_install_job = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)

    assigned_installers = db.relationship('ProjectInstaller', backref='project', cascade="all, delete-orphan")
    etas = db.relationship('ProjectETA', backref='project', cascade="all, delete-orphan")
    purchase_orders = db.relationship('PurchaseOrder', foreign_keys='PurchaseOrder.project_id', back_populates='project', lazy=True)

    @property
    def fulfillment_status(self):
        if self.purchase_orders:
            arrived = sum(1 for po in self.purchase_orders if po.status in ["Delivered to site / picked up by client", "Completed"])
            return f"📦 {arrived} of {len(self.purchase_orders)} Orders Delivered"
        if not self.etas:
            return "No materials"
        arrived = sum(1 for e in self.etas if e.status == 'Arrived at Torino' or e.received_date)
        return f"📦 {arrived} of {len(self.etas)} Suppliers Arrived"

    @property
    def all_materials_received(self):
        if self.purchase_orders:
            return all(po.status in ["Delivered to site / picked up by client", "Completed"] for po in self.purchase_orders)
        if not self.etas:
            return True
        return all(e.status == 'Arrived at Torino' or e.received_date for e in self.etas)

class ProjectLayoutSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    area = db.Column(db.String(150), nullable=False)
    tile = db.Column(db.String(300))
    pattern = db.Column(db.String(100))
    grout_color = db.Column(db.String(100))
    notes = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)

    project = db.relationship('Project', backref=db.backref('layout_sections', cascade="all, delete-orphan", lazy=True))