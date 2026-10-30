from datetime import datetime
from app.extensions import db


class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, index=True)
    slug = db.Column(db.String(270), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), default='news') # news, article, success_story, announcement, report
    summary = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text, nullable=False)
    featured_image = db.Column(db.String(255), nullable=True)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    author_name = db.Column(db.String(120), nullable=True, default='إدارة الجمعية')
    
    # حالة النشر: draft, published, archived
    status = db.Column(db.String(30), default='published', index=True)
    is_featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship('User', backref='articles')

    @property
    def category_label_ar(self):
        categories = {
            'news': 'أخبار الجمعية',
            'article': 'مقال تحليلي',
            'success_story': 'قصة نجاح ريادية',
            'announcement': 'إعلان رسمي',
            'report': 'تقرير وإحصاء'
        }
        return categories.get(self.category, 'خبر')

    def get_category_label(self, lang='ar'):
        if lang == 'en':
            categories_en = {
                'news': 'Society News',
                'article': 'Analytical Article',
                'success_story': 'Startup Success Story',
                'announcement': 'Official Announcement',
                'report': 'Report & Statistics'
            }
            return categories_en.get(self.category, 'News')
        return self.category_label_ar


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, index=True)
    title_en = db.Column(db.String(250), nullable=True) # العنوان باللغة الإنجليزية
    slug = db.Column(db.String(270), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(50), default='conference') # conference, workshop, hackathon, forum, demo_day, networking
    
    summary = db.Column(db.Text, nullable=False)
    summary_en = db.Column(db.Text, nullable=True) # الموجز باللغة الإنجليزية
    description = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=True) # التفاصيل وجدول الأعمال باللغة الإنجليزية
    cover_image = db.Column(db.String(255), nullable=True)
    
    location_type = db.Column(db.String(30), default='in_person') # in_person, online, hybrid
    location_name = db.Column(db.String(255), default='مقر الجمعية - جامعة غريان')
    location_name_en = db.Column(db.String(255), nullable=True) # اسم المكان بالإنجليزية
    city = db.Column(db.String(60), default='غريان')
    city_en = db.Column(db.String(60), nullable=True) # المدينة بالإنجليزية
    online_link = db.Column(db.String(255), nullable=True)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    
    capacity = db.Column(db.Integer, default=100)
    registered_count = db.Column(db.Integer, default=0)
    is_registration_open = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    registrations = db.relationship('EventRegistration', backref='event', cascade='all, delete-orphan')

    def get_title(self, lang='ar'):
        if lang == 'en' and self.title_en and self.title_en.strip():
            return self.title_en.strip()
        return self.title

    def get_summary(self, lang='ar'):
        if lang == 'en' and self.summary_en and self.summary_en.strip():
            return self.summary_en.strip()
        return self.summary

    def get_description(self, lang='ar'):
        if lang == 'en' and self.description_en and self.description_en.strip():
            return self.description_en.strip()
        return self.description

    def get_location_name(self, lang='ar'):
        if lang == 'en' and self.location_name_en and self.location_name_en.strip():
            return self.location_name_en.strip()
        return self.location_name

    def get_city(self, lang='ar'):
        if lang == 'en' and self.city_en and self.city_en.strip():
            return self.city_en.strip()
        return self.city

    def get_event_type_label(self, lang='ar'):
        types_ar = {
            'conference': 'مؤتمر علمي / ريادي',
            'forum': 'منتدى حواري',
            'workshop': 'ورشة عمل تدريبية',
            'hackathon': 'هاكاثون ومنافسة برمجية',
            'demo_day': 'يوم العروض (Demo Day)',
            'networking': 'لقاء تشبيك وتواصل'
        }
        types_en = {
            'conference': 'Scientific / Entrepreneurial Conference',
            'forum': 'Discussion Forum',
            'workshop': 'Training Workshop',
            'hackathon': 'Hackathon & Tech Challenge',
            'demo_day': 'Demo Day & Pitching',
            'networking': 'Networking Meetup'
        }
        if lang == 'en':
            return types_en.get(self.event_type, self.event_type)
        return types_ar.get(self.event_type, self.event_type)

    def get_location_type_label(self, lang='ar'):
        loc_ar = {
            'in_person': 'حضوري بالمقر',
            'online': 'افتراضي عن بُعد',
            'hybrid': 'مدمج (حضوري وافتراضي)'
        }
        loc_en = {
            'in_person': 'In-Person at Venue',
            'online': 'Virtual / Online',
            'hybrid': 'Hybrid (In-Person & Online)'
        }
        if lang == 'en':
            return loc_en.get(self.location_type, self.location_type)
        return loc_ar.get(self.location_type, self.location_type)


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    organization = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(30), default='confirmed') # confirmed, attended, cancelled
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)


class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, index=True)
    slug = db.Column(db.String(270), unique=True, nullable=False, index=True)
    opportunity_type = db.Column(db.String(50), default='grant') # grant, competition, incubation, acceleration, award, funding
    
    provider_name = db.Column(db.String(150), nullable=False, default='الجمعية الليبية للابتكار وريادة الأعمال')
    provider_logo = db.Column(db.String(255), nullable=True)
    
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, nullable=True) # شروط الأهلية والتقديم
    target_audience = db.Column(db.String(255), nullable=True) # المبتكرون، أصحاب الشركات الناشئة، طلاب الجامعات
    award_or_funding = db.Column(db.String(150), nullable=True) # قيمة المنحة أو الجائزة أو طبيعة الدعم
    
    sector = db.Column(db.String(80), nullable=True, default='كافة القطاعات')
    city = db.Column(db.String(60), nullable=True, default='كل المدن الليبية')
    
    deadline = db.Column(db.DateTime, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    
    external_link = db.Column(db.String(255), nullable=True)
    allow_internal_apply = db.Column(db.Boolean, default=True) # هل يتم التقديم من خلال المنصة
    
    # open, upcoming, closed, archived
    status = db.Column(db.String(30), default='open', index=True)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship('OpportunityApplication', backref='opportunity', cascade='all, delete-orphan')

    @property
    def status_label_ar(self):
        labels = {
            'open': 'التقديم متاح حالياً',
            'upcoming': 'يبدأ قريباً',
            'closed': 'مغلق',
            'archived': 'مؤرشف'
        }
        return labels.get(self.status, self.status)

    def get_status_label(self, lang='ar'):
        if lang == 'en':
            labels_en = {
                'open': 'Open for Application',
                'upcoming': 'Opening Soon',
                'closed': 'Closed',
                'archived': 'Archived'
            }
            return labels_en.get(self.status, self.status)
        return self.status_label_ar

    @property
    def type_label_ar(self):
        types = {
            'grant': 'منحة ابتكارية',
            'competition': 'مسابقة وجوائز',
            'incubation': 'برنامج احتضان',
            'acceleration': 'برنامج تسريع أعمال',
            'funding': 'فرصة استثمارية',
            'award': 'جائزة سنوية'
        }
        return types.get(self.opportunity_type, self.opportunity_type)

    def get_type_label(self, lang='ar'):
        if lang == 'en':
            types_en = {
                'grant': 'Innovation Grant',
                'competition': 'Challenge & Competition',
                'incubation': 'Incubation Program',
                'acceleration': 'Business Acceleration',
                'funding': 'Investment Opportunity',
                'award': 'National Award'
            }
            return types_en.get(self.opportunity_type, self.opportunity_type)
        return self.type_label_ar


class OpportunityApplication(db.Model):
    __tablename__ = 'opportunity_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('innovation_projects.id', ondelete='SET NULL'), nullable=True)
    
    applicant_name = db.Column(db.String(150), nullable=False)
    applicant_email = db.Column(db.String(120), nullable=False)
    applicant_phone = db.Column(db.String(30), nullable=False)
    proposal_summary = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(255), nullable=True)
    
    status = db.Column(db.String(30), default='submitted') # submitted, under_review, shortlisted, accepted, rejected
    admin_notes = db.Column(db.Text, nullable=True)
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='opportunity_applications')
    project = db.relationship('InnovationProject', backref='opportunity_applications')


class TrainingCourse(db.Model):
    __tablename__ = 'training_courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, index=True)
    slug = db.Column(db.String(270), unique=True, nullable=False, index=True)
    
    trainer_name = db.Column(db.String(120), nullable=False)
    trainer_title = db.Column(db.String(150), nullable=True)
    trainer_avatar = db.Column(db.String(255), nullable=True)
    
    course_type = db.Column(db.String(50), default='course') # course, workshop, bootcamp, webinar
    delivery_mode = db.Column(db.String(30), default='online') # online, in_person, hybrid
    location_or_link = db.Column(db.String(255), nullable=True)
    
    summary = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    learning_objectives = db.Column(db.Text, nullable=True) # مخرجات التعلم
    prerequisites = db.Column(db.Text, nullable=True) # المتطلبات المسبقة
    
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    duration_hours = db.Column(db.Integer, default=10)
    
    max_seats = db.Column(db.Integer, default=30)
    enrolled_count = db.Column(db.Integer, default=0)
    
    certificate_included = db.Column(db.Boolean, default=True)
    is_free = db.Column(db.Boolean, default=True)
    cover_image = db.Column(db.String(255), nullable=True)
    
    # open, closing_soon, closed, completed
    registration_status = db.Column(db.String(30), default='open')
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    enrollments = db.relationship('CourseEnrollment', backref='course', cascade='all, delete-orphan')

    def get_delivery_mode_label(self, lang='ar'):
        modes_en = {
            'online': 'Online / Virtual',
            'in_person': 'In-Person',
            'hybrid': 'Hybrid'
        }
        modes_ar = {
            'online': 'عن بُعد (افتراضي)',
            'in_person': 'حضوري',
            'hybrid': 'مدمج'
        }
        if lang == 'en':
            return modes_en.get(self.delivery_mode, self.delivery_mode)
        return modes_ar.get(self.delivery_mode, self.delivery_mode)

    def get_registration_status_label(self, lang='ar'):
        statuses_en = {
            'open': 'Open for Registration',
            'closing_soon': 'Closing Soon',
            'closed': 'Closed / Seats Filled',
            'completed': 'Completed'
        }
        statuses_ar = {
            'open': 'التسجيل متاح',
            'closing_soon': 'يغلق قريباً',
            'closed': 'اكتمل العدد / مغلق',
            'completed': 'مكتمل ومنتهي'
        }
        if lang == 'en':
            return statuses_en.get(self.registration_status, self.registration_status)
        return statuses_ar.get(self.registration_status, self.registration_status)


class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('training_courses.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    motivation = db.Column(db.Text, nullable=True) # دافع المشاركة
    
    status = db.Column(db.String(30), default='confirmed') # pending, confirmed, attended, certified, cancelled
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)


class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(300), nullable=True)
    content_html = db.Column(db.Text, nullable=False)
    
    is_published = db.Column(db.Boolean, default=True)
    show_in_footer = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Partner(db.Model):
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    partner_type = db.Column(db.String(60), default='governmental') # governmental, academic, private_sector, incubator, international
    logo = db.Column(db.String(255), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
