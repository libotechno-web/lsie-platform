from datetime import datetime
from app.extensions import db


class InnovationProject(db.Model):
    __tablename__ = 'innovation_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    tagline = db.Column(db.String(255), nullable=True) # وصف موجز بسطر واحد
    summary = db.Column(db.Text, nullable=False)
    
    problem_statement = db.Column(db.Text, nullable=False) # المشكلة التي يعالجها
    proposed_solution = db.Column(db.Text, nullable=False) # الحل المقترح
    target_market = db.Column(db.String(255), nullable=True) # الفئة المستهدفة
    sector = db.Column(db.String(80), nullable=False, default='تقنية المعلومات') # القطاع
    city = db.Column(db.String(60), nullable=False, default='غريان') # المدينة
    
    stage = db.Column(db.String(50), default='idea') # idea, prototype, mvp, operational, scaling
    business_model = db.Column(db.Text, nullable=True) # نموذج الإيرادات والعمل التجاري
    needed_support = db.Column(db.String(255), nullable=True) # تمويل، احتضان، توجيه، استشارات قانونية، شركاء
    team_description = db.Column(db.Text, nullable=True) # الفريق والخبرات
    
    demo_url = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    
    # دورة حياة الطلب والمشروع
    # draft, submitted, under_review, needs_info, under_evaluation, accepted, rejected, deferred, closed
    status = db.Column(db.String(40), default='submitted', index=True)
    status_notes_public = db.Column(db.Text, nullable=True) # ملاحظات توجه للمبتكر
    
    # إعدادات الخصوصية والظهور
    is_public_in_directory = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # العلاقات
    attachments = db.relationship('ProjectAttachment', backref='project', cascade='all, delete-orphan')
    reviews = db.relationship('ProjectReview', backref='project', cascade='all, delete-orphan')

    @property
    def status_badge_class(self):
        badges = {
            'draft': 'secondary',
            'submitted': 'info',
            'under_review': 'primary',
            'needs_info': 'warning text-dark',
            'under_evaluation': 'info',
            'accepted': 'success',
            'rejected': 'danger',
            'deferred': 'secondary',
            'closed': 'dark'
        }
        return badges.get(self.status, 'secondary')

    @property
    def status_label_ar(self):
        labels = {
            'draft': 'مسودة',
            'submitted': 'تم التقديم',
            'under_review': 'قيد المراجعة الأولية',
            'needs_info': 'مطلوب استكمال بيانات',
            'under_evaluation': 'قيد التقييم الفني',
            'accepted': 'مقبول ومعتمد',
            'rejected': 'غير مقبول',
            'deferred': 'مؤجل',
            'closed': 'مغلق'
        }
        return labels.get(self.status, self.status)

    @property
    def stage_label_ar(self):
        stages = {
            'idea': 'فكرة نظرية',
            'prototype': 'نموذج أولي (Prototype)',
            'mvp': 'منتج قابل للإطلاق (MVP)',
            'operational': 'قائم في السوق',
            'scaling': 'مرحلة التوسع والنمو'
        }
        return stages.get(self.stage, self.stage)

    def get_status_label(self, lang='ar'):
        if lang == 'en':
            labels_en = {
                'draft': 'Draft',
                'submitted': 'Submitted',
                'under_review': 'Under Initial Review',
                'needs_info': 'Additional Info Required',
                'under_evaluation': 'Technical Evaluation',
                'accepted': 'Accepted & Approved',
                'rejected': 'Declined',
                'deferred': 'Deferred',
                'closed': 'Closed'
            }
            return labels_en.get(self.status, self.status)
        return self.status_label_ar

    def get_stage_label(self, lang='ar'):
        if lang == 'en':
            stages_en = {
                'idea': 'Idea / Concept',
                'prototype': 'Working Prototype',
                'mvp': 'Minimum Viable Product (MVP)',
                'operational': 'Market Operational',
                'scaling': 'Growth & Scaling Stage'
            }
            return stages_en.get(self.stage, self.stage)
        return self.stage_label_ar

    def __repr__(self):
        return f'<InnovationProject {self.title} ({self.status})>'


class ProjectAttachment(db.Model):
    __tablename__ = 'project_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('innovation_projects.id', ondelete='CASCADE'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=True) # pitch_deck, business_plan, patent, prototype_video, other
    file_size_kb = db.Column(db.Integer, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProjectReview(db.Model):
    __tablename__ = 'project_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('innovation_projects.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # درجات التقييم (من 1 إلى 25 لكل معيار، المجموع 100)
    score_innovation = db.Column(db.Integer, default=0) # الأصالة والابتكار
    score_feasibility = db.Column(db.Integer, default=0) # قابلية التنفيذ والواقعية
    score_market_impact = db.Column(db.Integer, default=0) # حجم السوق والأثر الاقتصادي
    score_team = db.Column(db.Integer, default=0) # قدرات الفريق وجديته
    total_score = db.Column(db.Integer, default=0) # المجموع الكلي
    
    recommendation = db.Column(db.String(40), default='accept') # accept, reject, need_info, defer
    
    # سرية التقييم
    internal_notes = db.Column(db.Text, nullable=True) # ملاحظات سرية للجنة الإدارة والتقييم فقط
    applicant_feedback = db.Column(db.Text, nullable=True) # ملاحظات بناءة قابلة للمشاركة مع مقدم المشروع
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviewer = db.relationship('User', backref='project_reviews')
