from datetime import datetime, date
import json

INSTALLER_LABOUR_RATE = 0.40

ORDER_STATUSES = [
    "To be ordered", "Ordered", "Confirmed / In transit",
    "In Wpg / pick ups", "At Torino / ready for client pickup",
    "Delivered to site / picked up by client", "Completed"
]

PROJECT_STATUSES = [
    "Installer Assigned / Work Order Created",
    "Install Scheduled",
    "Project In Progress",
    "Completed"
]

def nl2br(value):
    if not isinstance(value, str):
        return value
    return value.replace('\n', '<br>\n')

def fromjson(value):
    return json.loads(value) if value else []

def generate_po_number(PurchaseOrder):
    last_po = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
    next_num = (last_po.id + 1) if last_po else 1
    return f"INV-{datetime.now().year}-{str(next_num).zfill(4)}"

def get_supplier_collection(supplier_name, Supplier):
    supplier = Supplier.query.filter_by(name=supplier_name).first()
    return supplier.collection if supplier else None

def get_selling_price(variant):
    return variant.price if variant else 0

def calculate_estimate_totals(data):
    subtotal = overage = fuel = 0
    for item in data:
        qty = float(item.get('qty', 0))
        price = float(item.get('price', 0))
        line = price * qty
        subtotal += line
        if not item.get('is_labour') and item.get('unit') == 'sqft':
            overage_sqft = qty * 0.125
            overage += overage_sqft * price
            fuel += line * 0.03
    total = subtotal + overage + fuel
    return subtotal, overage, fuel, total

def prepare_work_order_data(project, Estimate, PurchaseOrder, Customer, INSTALLER_LABOUR_RATE):
    data = {
        'work_order_number': f"WO-{datetime.now().year}-{str(project.id).zfill(4)}",
        'generated_date': datetime.now().strftime('%B %d, %Y'),
        'po_number': None,
        'project_name': project.project_name or f"Project #{project.id}",
        'client': {'name': project.customer_name or 'Unknown Client', 'address': '', 'phone': ''},
        'installers': [],
        'schedule': project.install_scheduled_date,
        'materials': [],
        'labour': [],
        'total_labour_payout': 0.0,
        'notes': project.notes or ''
    }

    if project.customer_id:
        cust = Customer.query.get(project.customer_id)
        if cust:
            data['client']['address'] = cust.address or ''
            data['client']['phone'] = cust.phone or ''

    if project.purchase_order_id:
        po = PurchaseOrder.query.get(project.purchase_order_id)
        if po:
            data['po_number'] = po.po_number

    for pi in project.assigned_installers:
        data['installers'].append({
            'name': pi.installer.name,
            'phone': pi.installer.phone or '—',
            'role': pi.role,
            'scheduled_date': pi.scheduled_date,
            'start_date': pi.start_date,
            'finish_date': pi.finish_date
        })

    if project.estimate_id:
        est = Estimate.query.get(project.estimate_id)
        if est and est.data:
            try:
                items = json.loads(est.data)
                labour_total = 0.0
                for item in items:
                    if item.get('is_labour', False):
                        retail = float(item.get('price', 0))
                        qty = float(item.get('qty', 0))
                        installer_rate = round(retail * INSTALLER_LABOUR_RATE, 2)
                        line_total = round(installer_rate * qty, 2)
                        labour_total += line_total
                        data['labour'].append({
                            'description': item.get('description') or item.get('finish') or item.get('series') or 'Tile Installation Labour',
                            'qty': qty,
                            'unit': item.get('unit', 'sqft'),
                            'retail_rate': retail,
                            'installer_rate': installer_rate,
                            'total_pay': line_total
                        })
                    else:
                        desc_parts = []
                        if item.get('series'): desc_parts.append(item.get('series'))
                        if item.get('size'): desc_parts.append(item.get('size'))
                        if item.get('finish'): desc_parts.append(item.get('finish'))
                        if item.get('color'): desc_parts.append(item.get('color'))
                        description = " • ".join(desc_parts) or item.get('description', 'Material')
                        data['materials'].append({
                            'description': description,
                            'qty': float(item.get('qty', 0)),
                            'unit': item.get('unit', 'sqft')
                        })
                data['total_labour_payout'] = round(labour_total, 2)
            except Exception as e:
                print(f"⚠️ Work order data parse error: {e}")

    return data

def get_or_create_customer(db, Customer, name, phone=None, email=None):
    if not name or str(name).strip() == "":
        return None
    name = str(name).strip()
    customer = Customer.query.filter_by(name=name).first()
    if not customer:
        customer = Customer(name=name, phone=phone, email=email)
        db.session.add(customer)
        db.session.flush()
    return customer