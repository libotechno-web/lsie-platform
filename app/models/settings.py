from datetime import datetime
from app.extensions import db


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    group_name = db.Column(db.String(50), default='general') # general, appearance, contact, social, about, official
    label_ar = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    setting_type = db.Column(db.String(30), default='text') # text, textarea, boolean, color, image
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_value(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting and setting.value is not None else default

    @classmethod
    def set_value(cls, key, value, group='general', label=None, setting_type='text'):
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, value=value, group_name=group, label_ar=label or key, setting_type=setting_type)
            db.session.add(setting)
        else:
            setting.value = value
            if label:
                setting.label_ar = label
        db.session.commit()
        return setting


class NavigationItem(db.Model):
    __tablename__ = 'navigation_items'
    
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), nullable=True)
    
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_external = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(30), default='header') # header, footer, both


class StrategicObjective(db.Model):
    __tablename__ = 'strategic_objectives'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(60), default='bi-bullseye')
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class OrganizationalValue(db.Model):
    __tablename__ = 'organizational_values'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(60), default='bi-star')
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_email = db.Column(db.String(120), nullable=True)
    
    action = db.Column(db.String(100), nullable=False) # e.g. login, create_user, update_settings, review_project, delete_item
    resource_type = db.Column(db.String(60), nullable=True) # project, user, article, setting
    resource_id = db.Column(db.String(60), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='audit_logs')
