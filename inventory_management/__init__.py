import os

from flask import Flask
from .extensions import limiter
from .extensions import csrf
from datetime import timedelta

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='23cda5515df814ccd03d30c9c8b7616d7021813af966cf85f953da4d92dcaed1',
        DATABASE=os.path.join(app.instance_path, 'Inventory_Management.sqlite'),
    )

    app.config.update( 
        SESSION_COOKIE_SECURE=True,      # المتصفح لن يرسل الكوكي إلا عبر HTTPS في وضع الإنتاج
        SESSION_COOKIE_HTTPONLY=True,    # JS لا يقرأها
        SESSION_COOKIE_SAMESITE="Lax",   # حماية CSRF
    )

    # تفعيل الجلسات الدائمة
    app.config['SESSION_PERMANENT'] = True

    # تحديد صلاحية الجلسة (مثلاً 7 أيام)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # ربط Limiter مع التطبيق
    limiter.init_app(app)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import homepage
    app.register_blueprint(homepage.bp)
    app.add_url_rule('/', endpoint='index') 

    from . import products_management
    app.register_blueprint(products_management.bp)

    from . import movements
    app.register_blueprint(movements.bp)

    # علشان نحول اسماء الحركات الانجليزيه الى العربيه في صفحة السجل 
    movements_map = {
        "out": "خروج",
        "in": "دخول"
    }
    
    # فلتر jinja 
    @app.template_filter("translate_movements")
    def translate_movements_filter(value):
        return movements_map.get(value, value)  # إذا غير موجود يرجع نفس القيمة

    csrf.init_app(app)

    @app.after_request
    def set_security_headers(response):
        # Content Security Policy - allow local scripts/styles and data images/fonts
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    return app