from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..models import db, Series, TileVariant, Supplier
from ..utils import get_supplier_collection, get_selling_price, calculate_estimate_totals
from ..auth.routes import login_required

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/admin/tiles')
@login_required
def admin_tiles():
    series_list = Series.query.order_by(Series.collection, Series.series).all()
    for series in series_list:
        for v in series.variants:
            v.selling_price = get_selling_price(v)
    return render_template('catalog/admin_tiles.html', series_list=series_list)

@catalog_bp.route('/admin/catalog', methods=['GET', 'POST'])
@login_required
def admin_catalog():
    if request.method == 'POST':
        variant = TileVariant(
            series_id=int(request.form.get('series_id')),
            size=request.form.get('size'),
            finish=request.form.get('finish'),
            color=request.form.get('color'),
            price=float(request.form.get('price') or 0),
            sqft_per_box=float(request.form.get('sqft_per_box') or 1),
            unit=request.form.get('unit', 'each'),
            sample_status='In Store'
        )
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                variant.photo = filename
        db.session.add(variant)
        db.session.commit()
        flash('✅ Tile added to catalog!', 'success')
        return redirect(url_for('catalog.admin_catalog'))

    series_list = Series.query.order_by(Series.collection, Series.series).all()
    all_variants = []
    for s in series_list:
        for v in s.variants:
            v.selling_price = get_selling_price(v)
            all_variants.append(v)

    return render_template('catalog/admin_catalog.html', series_list=series_list, variants=all_variants)

@catalog_bp.route('/catalog')
@login_required
def catalog():
    return redirect(url_for('catalog.admin_tiles'))

@catalog_bp.route('/admin/tiles/import', methods=['GET', 'POST'])
@login_required
def import_tiles():
    # Full original import logic would go here (CSV/Excel handling)
    return render_template('catalog/import_tiles.html')

@catalog_bp.route('/admin/tiles/add', methods=['GET', 'POST'])
@login_required
def add_tile():
    return render_template('catalog/add_tile.html')

@catalog_bp.route('/admin/tile/<int:tile_id>', methods=['GET', 'POST'])
@login_required
def tile_detail(tile_id):
    tile = TileVariant.query.get_or_404(tile_id)
    return render_template('catalog/tile_detail.html', tile=tile)

@catalog_bp.route('/admin/series/<int:series_id>')
@login_required
def series_detail(series_id):
    series = Series.query.get_or_404(series_id)
    return render_template('catalog/series_detail.html', series=series)

@catalog_bp.route('/admin/sample/<int:variant_id>/signout', methods=['POST'])
@login_required
def sign_out_sample(variant_id):
    # original sign out logic
    return redirect(url_for('catalog.tile_detail', tile_id=variant_id))

@catalog_bp.route('/admin/sample/<int:variant_id>/checkin', methods=['POST'])
@login_required
def check_in_sample(variant_id):
    # original check in logic
    return redirect(url_for('catalog.tile_detail', tile_id=variant_id))

@catalog_bp.route('/visualizer')
@login_required
def visualizer():
    return render_template('catalog/visualizer.html')