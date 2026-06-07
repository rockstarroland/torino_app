from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash

from .config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(__name__, 
                template_folder=os.path.join(root_dir, 'templates'),
                static_folder=os.path.join(root_dir, 'static'))

    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    from .core.routes import core_bp
    from .auth.routes import auth_bp
    from .catalog.routes import catalog_bp
    from .estimates.routes import estimates_bp
    from .projects.routes import projects_bp
    from .orders.routes import orders_bp
    from .customers.routes import customers_bp
    from .installers.routes import installers_bp
    from .suppliers.routes import suppliers_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(catalog_bp, url_prefix='/catalog')
    app.register_blueprint(estimates_bp, url_prefix='/estimates')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(installers_bp, url_prefix='/installers')
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')

    with app.app_context():
        db.create_all()

        # Import User here to avoid circular imports
        from .models import User

        # Create default admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.password_hash = generate_password_hash('torino2026')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created (admin / torino2026)")

    return app