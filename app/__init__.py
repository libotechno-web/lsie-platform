import os
import sqlite3
from flask import Flask, render_template, request, session
from sqlalchemy import event, inspect, text
from sqlalchemy.engine import Engine

from config import config_by_name
from app.extensions import db, login_manager, csrf, migrate


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # تفعيل قيود المفاتيح الخارجية في SQLite تلقائياً
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

    # تهيئة إضافات Flask
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # إنشاء المجلدات الضرورية إذا لم تكن موجودة
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'data'), exist_ok=True)

    # تسجيل Blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # معالجات الأخطاء المخصصة
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('public/error.html', code=403, message='ليس لديك الصلاحية للوصول إلى هذه الصفحة.'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('public/error.html', code=404, message='الصفحة المطلوبة غير موجودة.'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('public/error.html', code=500, message='حدث خطأ داخلي في الخادم. تم تسجيل الخطأ وسيقوم الفريق بمعالجته.'), 500

    # التحقق من لغة العرض وتحديدها
    @app.before_request
    def determine_language():
        req_lang = request.args.get('lang')
        if req_lang in ['ar', 'en']:
            session['lang'] = req_lang

    # معالج السياق العام لجميع القوالب (Data-Driven Global Context)
    @app.context_processor
    def inject_global_data():
        from app.models.settings import SiteSetting, NavigationItem
        from app.models.networking import Notification
        from flask_login import current_user
        from app.translations import translate

        current_lang = session.get('lang', 'ar')

        def trans(ar_text, en_text=None):
            return translate(ar_text, en_text, current_lang)

        settings_dict = {}
        try:
            all_settings = SiteSetting.query.all()
            for s in all_settings:
                settings_dict[s.key] = s.value
        except Exception:
            pass

        # القائمة الرئيسية والروابط
        header_nav = []
        try:
            header_nav = NavigationItem.query.filter_by(is_active=True).order_by(NavigationItem.order_index).all()
        except Exception:
            pass

        unread_notifications = 0
        if current_user.is_authenticated:
            try:
                unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            except Exception:
                pass

        return {
            'site_settings': settings_dict,
            'header_nav': header_nav,
            'unread_notifications': unread_notifications,
            'current_lang': current_lang,
            'trans': trans,
            '_': trans
        }

    # التحديث التلقائي لأعمدة جدول الفعاليات عند الحاجة
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            if 'events' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('events')]
                new_cols = [
                    ('title_en', 'VARCHAR(250)'),
                    ('summary_en', 'TEXT'),
                    ('description_en', 'TEXT'),
                    ('location_name_en', 'VARCHAR(255)'),
                    ('city_en', 'VARCHAR(60)')
                ]
                for cname, ctype in new_cols:
                    if cname not in cols:
                        with db.engine.connect() as conn:
                            conn.execute(text(f"ALTER TABLE events ADD COLUMN {cname} {ctype}"))
                            conn.commit()
    except Exception:
        pass

    return app
