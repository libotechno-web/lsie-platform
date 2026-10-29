from datetime import datetime
from app.extensions import db


class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    name = db.Column(db.String(150), nullable=False, index=True)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    org_type = db.Column(db.String(50), default='startup') # startup, university, incubator, accelerator, enterprise, support_entity
    logo = db.Column(db.String(255), nullable=True)
    
    city = db.Column(db.String(60), default='طرابلس')
    address = db.Column(db.String(255), nullable=True)
    sector = db.Column(db.String(80), default='تقنية المعلومات') # تقنية المعلومات، صحة، زراعة، طاقة، تعليم، صناعة، تجارة إلكترونية، نقل ولوجستيات
    stage = db.Column(db.String(50), default='early_stage') # idea, prototype, early_stage, growth, scaling
    
    founded_year = db.Column(db.Integer, nullable=True)
    team_size = db.Column(db.String(30), nullable=True, default='1-5')
    
    website = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    
    description = db.Column(db.Text, nullable=False)
    products_services = db.Column(db.Text, nullable=True)
    
    # احتياجات الشركة/المؤسسة
    funding_needs = db.Column(db.String(255), nullable=True) # تمويل أولي، تمويل نمو، لا يوجد
    partnership_needs = db.Column(db.String(255), nullable=True) # شركاء تقنيين، خبراء، موزعون
    
    # حالة الاعتماد والظهور
    is_verified = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_public_in_directory = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Organization {self.name} ({self.org_type})>'
