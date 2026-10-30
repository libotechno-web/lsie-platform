from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


# جدول الربط بين المستخدمين والأدوار (Many-to-Many)
class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)


class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True) # e.g. admin, member, innovator, startup, investor, expert, partner_org, editor, reviewer
    title_ar = db.Column(db.String(100), nullable=False) # e.g. مدير النظام، مبتكر، مستثمر
    description = db.Column(db.String(255), nullable=True)
    is_system = db.Column(db.Boolean, default=False) # Roles that cannot be deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', secondary='user_roles', back_populates='roles')

    def __repr__(self):
        return f'<Role {self.name}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(60), nullable=True, default='غريان')
    account_type = db.Column(db.String(30), default='member') # innovator, startup, investor, expert, partner_org, member
    headline = db.Column(db.String(200), nullable=True) # e.g. مهندس برمجيات ومؤسس ناشئ
    bio = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    
    # حالات الحساب والأمان
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_approved_member = db.Column(db.Boolean, default=False)
    privacy_level = db.Column(db.String(20), default='public') # public, members_only, private
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    projects = db.relationship('InnovationProject', backref='owner', cascade='all, delete-orphan', foreign_keys='InnovationProject.user_id')
    organizations = db.relationship('Organization', backref='owner', cascade='all, delete-orphan')
    course_enrollments = db.relationship('CourseEnrollment', backref='user', cascade='all, delete-orphan')
    event_registrations = db.relationship('EventRegistration', backref='user', cascade='all, delete-orphan')
    sent_requests = db.relationship('NetworkingRequest', foreign_keys='NetworkingRequest.sender_id', backref='sender', cascade='all, delete-orphan')
    received_requests = db.relationship('NetworkingRequest', foreign_keys='NetworkingRequest.recipient_id', backref='recipient', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(r.name == role_name for r in self.roles)

    @property
    def is_admin(self):
        return self.has_role('admin')

    @property
    def is_reviewer(self):
        return self.has_role('reviewer') or self.has_role('admin')

    @property
    def is_editor(self):
        return self.has_role('editor') or self.has_role('admin')

    @property
    def role_names(self):
        return [r.name for r in self.roles]

    @property
    def primary_role_title(self):
        if self.roles:
            return self.roles[0].title_ar
        return 'عضو'

    @property
    def current_job(self):
        if self.profile and self.profile.current_job:
            return self.profile.current_job
        return self.headline or 'عضو'

    @property
    def cv_file(self):
        return self.profile.cv_file if self.profile else None

    @property
    def previous_activities(self):
        return self.profile.previous_activities if self.profile else None

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # مهارات وخبرات وبيانات الانضمام
    current_job = db.Column(db.String(200), nullable=True) # الوظيفة الحالية / المسمى المهني
    previous_activities = db.Column(db.Text, nullable=True) # أعمال ونشاطات سابقة في الابتكار وريادة الأعمال
    skills = db.Column(db.String(255), nullable=True) # مفصولة بفواصل
    interests = db.Column(db.String(255), nullable=True) # مجالات الاهتمام
    experience_years = db.Column(db.Integer, nullable=True, default=0)
    education_level = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(150), nullable=True)
    
    # روابط خارجية
    cv_file = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)
    
    # تفضيلات الظهور والتشبيك
    available_for_mentoring = db.Column(db.Boolean, default=False)
    is_public_in_directory = db.Column(db.Boolean, default=True)
    
    # مجالات الاستثمار (للمستثمرين)
    investment_stages = db.Column(db.String(255), nullable=True)
    investment_ticket_size = db.Column(db.String(100), nullable=True)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
