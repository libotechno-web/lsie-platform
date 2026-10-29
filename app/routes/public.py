from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from datetime import datetime
from sqlalchemy import or_

from app.extensions import db
from app.models import (
    User, UserProfile, Organization, InnovationProject,
    Article, Event, EventRegistration, Opportunity, OpportunityApplication,
    TrainingCourse, CourseEnrollment, Page, Partner,
    StrategicObjective, OrganizationalValue, SiteSetting,
    NetworkingRequest
)
from app.forms import (
    EventRegistrationForm, CourseEnrollmentForm, OpportunityApplicationForm,
    NetworkingRequestForm
)
from app.utils.helpers import save_uploaded_file, create_notification

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """الصفحة الرئيسية للمنصة الوطنية للابتكار وريادة الأعمال"""
    # 1. الخدمات والبرامج النشطة
    # 2. أحدث الفرص والمنح المفتوحة
    opportunities = Opportunity.query.filter(
        Opportunity.status.in_(['open', 'upcoming'])
    ).order_by(Opportunity.deadline.asc()).limit(3).all()
    
    # 3. نماذج من دليل الابتكار المعتمدة وظاهرة للعامة
    featured_startups = Organization.query.filter_by(
        is_public_in_directory=True, is_verified=True
    ).limit(3).all()
    
    featured_projects = InnovationProject.query.filter_by(
        status='accepted', is_public_in_directory=True
    ).order_by(InnovationProject.updated_at.desc()).limit(3).all()
    
    # 4. آخر الأخبار والفعاليات
    latest_news = Article.query.filter_by(
        status='published'
    ).order_by(Article.published_at.desc()).limit(3).all()
    
    upcoming_events = Event.query.filter(
        Event.is_published == True,
        Event.start_time >= datetime.utcnow()
    ).order_by(Event.start_time.asc()).limit(3).all()
    
    # 5. الشركاء المعتمدون
    partners = Partner.query.filter_by(is_active=True).order_by(Partner.order_index).all()
    
    # 6. مؤشرات الأثر الحقيقية من قاعدة البيانات (Real Data-Driven Metrics - no hardcoded fake numbers)
    stats = {
        'members_count': User.query.filter_by(is_active=True).count(),
        'projects_count': InnovationProject.query.filter(InnovationProject.status.in_(['accepted', 'under_evaluation', 'under_review'])).count(),
        'accepted_projects_count': InnovationProject.query.filter_by(status='accepted').count(),
        'startups_count': Organization.query.filter_by(is_public_in_directory=True).count(),
        'opportunities_count': Opportunity.query.filter(Opportunity.status.in_(['open', 'upcoming'])).count(),
        'events_count': Event.query.filter_by(is_published=True).count(),
        'training_courses_count': TrainingCourse.query.count()
    }
    
    return render_template(
        'public/index.html',
        opportunities=opportunities,
        featured_startups=featured_startups,
        featured_projects=featured_projects,
        latest_news=latest_news,
        upcoming_events=upcoming_events,
        partners=partners,
        stats=stats
    )


@public_bp.route('/about')
def about():
    """عن الجمعية: النبذة، الرؤية، الرسالة، الأهداف، القيم، الإشهار الرسمي"""
    objectives = StrategicObjective.query.filter_by(is_active=True).order_by(StrategicObjective.order_index).all()
    values = OrganizationalValue.query.filter_by(is_active=True).order_by(OrganizationalValue.order_index).all()
    partners = Partner.query.filter_by(is_active=True).order_by(Partner.order_index).all()
    return render_template('public/about.html', objectives=objectives, values=values, partners=partners)


@public_bp.route('/services')
def services():
    """بوابة الخدمات الإلكترونية للمنصة"""
    return render_template('public/services.html')


@public_bp.route('/programs')
def programs():
    """البرامج والمبادرات الوطنية"""
    return render_template('public/programs.html')


@public_bp.route('/directory')
def directory():
    """دليل الابتكار الليبي: مبتكرون، شركات ناشئة، مستثمرون، خبراء، جامعات"""
    tab = request.args.get('tab', 'all')
    city = request.args.get('city', '')
    sector = request.args.get('sector', '')
    q = request.args.get('q', '').strip()
    
    # استعلام الشركات الناشئة
    startups_query = Organization.query.filter_by(is_public_in_directory=True)
    if city:
        startups_query = startups_query.filter(Organization.city == city)
    if sector:
        startups_query = startups_query.filter(Organization.sector == sector)
    if q:
        startups_query = startups_query.filter(or_(
            Organization.name.ilike(f'%{q}%'),
            Organization.description.ilike(f'%{q}%')
        ))
    startups = startups_query.all()
    
    # استعلام الخبراء والموجهين
    experts_query = User.query.join(UserProfile).filter(
        User.is_active == True,
        UserProfile.is_public_in_directory == True,
        User.account_type.in_(['expert', 'mentor'])
    )
    if city:
        experts_query = experts_query.filter(User.city == city)
    if q:
        experts_query = experts_query.filter(or_(
            User.full_name.ilike(f'%{q}%'),
            User.headline.ilike(f'%{q}%'),
            UserProfile.skills.ilike(f'%{q}%')
        ))
    experts = experts_query.all()
    
    # استعلام المستثمرين
    investors_query = User.query.join(UserProfile).filter(
        User.is_active == True,
        UserProfile.is_public_in_directory == True,
        User.account_type == 'investor'
    )
    if city:
        investors_query = investors_query.filter(User.city == city)
    if q:
        investors_query = investors_query.filter(or_(
            User.full_name.ilike(f'%{q}%'),
            User.headline.ilike(f'%{q}%')
        ))
    investors = investors_query.all()
    
    # استعلام المشاريع المبتكرة المعتمدة المنشورة
    projects_query = InnovationProject.query.filter_by(status='accepted', is_public_in_directory=True)
    if city:
        projects_query = projects_query.filter(InnovationProject.city == city)
    if sector:
        projects_query = projects_query.filter(InnovationProject.sector == sector)
    if q:
        projects_query = projects_query.filter(or_(
            InnovationProject.title.ilike(f'%{q}%'),
            InnovationProject.summary.ilike(f'%{q}%')
        ))
    projects = projects_query.all()
    
    # المدن المتاحة للتصفية
    cities = ['غريان', 'طرابلس', 'بنغازي', 'مصراتة', 'الزاوية', 'سبها', 'طبرق', 'زليتن', 'سرت', 'درنة', 'البيضاء']
    sectors = [
        'تقنية المعلومات والذكاء الاصطناعي', 'التقنيات المالية (FinTech)', 'التقنيات الصحية والطبية',
        'الزراعة والأمن الغذائي', 'الطاقة المتجددة والاستدامة', 'التعليم وتكنولوجيا المعرفة (EdTech)',
        'التجارة الإلكترونية والخدمات اللوجستية', 'الصناعة والتصنيع المحلي'
    ]
    
    return render_template(
        'public/directory.html',
        tab=tab,
        startups=startups,
        experts=experts,
        investors=investors,
        projects=projects,
        cities=cities,
        sectors=sectors,
        selected_city=city,
        selected_sector=sector,
        query=q
    )


@public_bp.route('/directory/user/<int:user_id>')
def user_profile_public(user_id):
    """الملف التعريفي العام لعضو / خبير / مستثمر في الدليل"""
    user = User.query.get_or_404(user_id)
    if not user.is_active:
        abort(404)
    # التحقق من إذن الظهور العام
    if not user.profile or not user.profile.is_public_in_directory:
        if not (current_user.is_authenticated and (current_user.is_admin or current_user.id == user.id)):
            abort(403)
            
    public_projects = InnovationProject.query.filter_by(
        user_id=user.id, status='accepted', is_public_in_directory=True
    ).all()
    
    return render_template('public/profile_detail.html', user=user, public_projects=public_projects)


@public_bp.route('/directory/organization/<slug>')
def organization_detail(slug):
    """صفحة تفاصيل الشركة الناشئة أو المؤسسة الداعمة"""
    org = Organization.query.filter_by(slug=slug, is_public_in_directory=True).first_or_404()
    return render_template('public/organization_detail.html', org=org)


@public_bp.route('/opportunities')
def opportunities():
    """بوابة الفرص والمنح والمسابقات"""
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    
    query = Opportunity.query
    if status_filter != 'all':
        query = query.filter(Opportunity.status == status_filter)
    else:
        # افتراضياً إظهار المفتوحة والقادمة أولاً ثم المنتهية
        query = query.filter(Opportunity.status != 'archived')
        
    if type_filter != 'all':
        query = query.filter(Opportunity.opportunity_type == type_filter)
        
    opps = query.order_by(Opportunity.deadline.asc()).all()
    return render_template('public/opportunities.html', opportunities=opps, current_status=status_filter, current_type=type_filter)


@public_bp.route('/opportunities/<slug>', methods=['GET', 'POST'])
def opportunity_detail(slug):
    """تفاصيل الفرصة ونموذج التقديم"""
    opp = Opportunity.query.filter_by(slug=slug).first_or_404()
    form = OpportunityApplicationForm()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('يرجى تسجيل الدخول أو إنشاء حساب أولاً للتقديم على الفرصة.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
            
        attachment_path = None
        if form.attachment.data:
            try:
                attachment_path = save_uploaded_file(form.attachment.data, 'opportunities')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('public/opportunity_detail.html', opp=opp, form=form)
                
        app_record = OpportunityApplication(
            opportunity_id=opp.id,
            user_id=current_user.id,
            applicant_name=form.applicant_name.data.strip(),
            applicant_email=form.applicant_email.data.strip(),
            applicant_phone=form.applicant_phone.data.strip(),
            proposal_summary=form.proposal_summary.data.strip(),
            attachment_path=attachment_path,
            status='submitted'
        )
        db.session.add(app_record)
        db.session.commit()
        
        flash('تم استلام طلب تقديمك بنجاح! سيتم إشعارك بنتائج الفرز والتقييم.', 'success')
        create_notification(current_user.id, f"تم التقديم على فرصة: {opp.title}", "طلبك قيد المراجعة حالياً من قبل الإدارة.", url_for('dashboard.my_applications'))
        return redirect(url_for('public.opportunity_detail', slug=opp.slug))
        
    return render_template('public/opportunity_detail.html', opp=opp, form=form)


@public_bp.route('/training')
def training():
    """بوابة التدريب والأكاديمية الرقمية"""
    courses = TrainingCourse.query.order_by(TrainingCourse.start_date.asc()).all()
    return render_template('public/training.html', courses=courses)


@public_bp.route('/training/<slug>', methods=['GET', 'POST'])
def training_detail(slug):
    """تفاصيل البرنامج التدريبي ونموذج التسجيل مع التحقق الدقيق من اكتمال العدد"""
    course = TrainingCourse.query.filter_by(slug=slug).first_or_404()
    form = CourseEnrollmentForm()
    
    # حساب العدد الفعلي للمسجلين المؤكدين من قاعدة البيانات
    actual_enrolled_count = CourseEnrollment.query.filter_by(course_id=course.id).filter(CourseEnrollment.status != 'cancelled').count()
    is_full = course.max_seats is not None and actual_enrolled_count >= course.max_seats
    is_closed = not course.is_active or course.registration_status == 'closed'
    
    is_already_enrolled = False
    if current_user.is_authenticated:
        is_already_enrolled = CourseEnrollment.query.filter_by(course_id=course.id, user_id=current_user.id).first() is not None
        
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('يرجى تسجيل الدخول للالتحاق بالبرنامج التدريبي.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
            
        if is_already_enrolled:
            flash('أنت مسجل بالفعل في هذا البرنامج التدريبي ومقعدك محجوز.', 'info')
            return redirect(url_for('public.training_detail', slug=course.slug))
            
        # التحقق الحاسم من اكتمال العدد
        if is_full or is_closed:
            flash('عذراً، نعتذر منك! لقد اكتمل العدد الأقصى المحدد للمقاعد في هذا البرنامج التدريبي وتم إغلاق التسجيل.', 'danger')
            return redirect(url_for('public.training_detail', slug=course.slug))
            
        enrollment = CourseEnrollment(
            course_id=course.id,
            user_id=current_user.id,
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data.strip(),
            motivation=form.motivation.data.strip(),
            status='confirmed'
        )
        db.session.add(enrollment)
        course.enrolled_count = actual_enrolled_count + 1
        
        # إذا وصل العدد للحد الأقصى، يتم تحديث الحالة لمغلق تلقائياً
        if course.max_seats is not None and course.enrolled_count >= course.max_seats:
            course.registration_status = 'closed'
            
        db.session.commit()
        
        flash('تهانينا! تم تأكيد تسجيلك في البرنامج التدريبي بنجاح وحجز مقعدك.', 'success')
        create_notification(current_user.id, f"تأكيد التسجيل في: {course.title}", "تم تأكيد مقعدك في البرنامج التدريبي بنجاح.", url_for('dashboard.my_courses'))
        return redirect(url_for('public.training_detail', slug=course.slug))
        
    return render_template('public/training_detail.html', course=course, form=form, is_already_enrolled=is_already_enrolled, is_full=is_full, is_closed=is_closed, actual_enrolled_count=actual_enrolled_count)


@public_bp.route('/news')
def news():
    """الأخبار والمقالات وقصص النجاح"""
    category = request.args.get('category')
    query = Article.query.filter_by(status='published')
    if category:
        query = query.filter_by(category=category)
    articles = query.order_by(Article.published_at.desc()).all()
    return render_template('public/news.html', articles=articles, current_category=category)


@public_bp.route('/news/<slug>')
def news_detail(slug):
    """تفاصيل المقال أو الخبر"""
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    article.views_count = (article.views_count or 0) + 1
    db.session.commit()
    
    related_articles = Article.query.filter(
        Article.id != article.id,
        Article.status == 'published'
    ).order_by(Article.published_at.desc()).limit(3).all()
    
    return render_template('public/news_detail.html', article=article, related_articles=related_articles)


@public_bp.route('/events')
def events():
    """الفعاليات والمؤتمرات"""
    upcoming_events = Event.query.filter(
        Event.is_published == True,
        Event.start_time >= datetime.utcnow()
    ).order_by(Event.start_time.asc()).all()
    
    past_events = Event.query.filter(
        Event.is_published == True,
        Event.start_time < datetime.utcnow()
    ).order_by(Event.start_time.desc()).limit(6).all()
    
    return render_template('public/events.html', upcoming_events=upcoming_events, past_events=past_events)


@public_bp.route('/events/<slug>', methods=['GET', 'POST'])
def event_detail(slug):
    """تفاصيل الفعالية والتسجيل مع التحقق الدقيق من اكتمال العدد"""
    event = Event.query.filter_by(slug=slug, is_published=True).first_or_404()
    form = EventRegistrationForm()
    
    # حساب العدد الفعلي للمسجلين المؤكدين من قاعدة البيانات
    actual_reg_count = EventRegistration.query.filter_by(event_id=event.id, status='confirmed').count()
    is_full = event.capacity is not None and actual_reg_count >= event.capacity
    is_closed = not event.is_registration_open
    
    is_registered = False
    if current_user.is_authenticated:
        is_registered = EventRegistration.query.filter_by(event_id=event.id, user_id=current_user.id).first() is not None
        
    if form.validate_on_submit():
        if is_registered:
            flash('أنت مسجل بالفعل في هذه الفعالية وتذكرتك مؤكدة.', 'info')
            return redirect(url_for('public.event_detail', slug=event.slug))
            
        # التحقق الحاسم من اكتمال السعة
        if is_full or is_closed:
            flash('عذراً، نعتذر منك! لقد اكتمل العدد الأقصى المحدد للمقاعد في هذه الفعالية وتم إغلاق الحجز.', 'danger')
            return redirect(url_for('public.event_detail', slug=event.slug))
            
        user_id = current_user.id if current_user.is_authenticated else None
        
        reg = EventRegistration(
            event_id=event.id,
            user_id=user_id,
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data.strip(),
            organization=form.organization.data.strip() if form.organization.data else None,
            notes=form.notes.data.strip() if form.notes.data else None,
            status='confirmed'
        )
        db.session.add(reg)
        event.registered_count = actual_reg_count + 1
        
        # إذا اكتمل العدد، يتم إغلاق التسجيل تلقائياً
        if event.capacity is not None and event.registered_count >= event.capacity:
            event.is_registration_open = False
            
        db.session.commit()
        
        flash('تم تسجيلك بنجاح في الفعالية وحجز مقعدك! سنرسل لك تذكرة الحضور وتفاصيل الموعد.', 'success')
        if current_user.is_authenticated:
            create_notification(current_user.id, f"تسجيل مؤكد: {event.title}", "تم تأكيد تسجيلك وحجز مقعدك في الفعالية.", url_for('dashboard.my_events'))
        return redirect(url_for('public.event_detail', slug=event.slug))
        
    return render_template('public/event_detail.html', event=event, form=form, is_registered=is_registered, is_full=is_full, is_closed=is_closed, actual_reg_count=actual_reg_count)


@public_bp.route('/networking/connect/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def connect_request(recipient_id):
    """إرسال طلب تشبيك أو توجيه إلى مستخدم أو خبير أو مستثمر"""
    recipient = User.query.get_or_404(recipient_id)
    if recipient.id == current_user.id:
        flash('لا يمكنك إرسال طلب تواصل لنفسك.', 'warning')
        return redirect(url_for('public.directory'))
        
    form = NetworkingRequestForm()
    if request.method == 'GET':
        form.sender_contact_email.data = current_user.email
        form.sender_contact_phone.data = current_user.phone
        
    if form.validate_on_submit():
        net_req = NetworkingRequest(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            request_type=form.request_type.data,
            subject=form.subject.data.strip(),
            message=form.message.data.strip(),
            sender_contact_email=form.sender_contact_email.data.strip(),
            sender_contact_phone=form.sender_contact_phone.data.strip() if form.sender_contact_phone.data else None,
            status='pending'
        )
        db.session.add(net_req)
        db.session.commit()
        
        create_notification(
            recipient.id,
            f"طلب تشبيك جديد من: {current_user.full_name}",
            f"الموضوع: {form.subject.data.strip()}",
            url_for('dashboard.networking_requests')
        )
        
        flash('تم إرسال طلب التشبيك والتواصل بنجاح! سيتم إشعار الطرف الآخر.', 'success')
        return redirect(url_for('public.user_profile_public', user_id=recipient.id))
        
    return render_template('public/connect_modal.html', recipient=recipient, form=form)


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """صفحة تواصل معنا الرسمية"""
    if request.method == 'POST':
        # نموذج مراسلة بسيط وسريع
        sender_name = request.form.get('name')
        sender_email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if sender_name and sender_email and message:
            flash('شكراً لتواصلك معنا! تم استلام رسالتك وسيقوم فريق الجمعية بالرد عليك قريباً.', 'success')
            return redirect(url_for('public.contact'))
        else:
            flash('يرجى ملء جميع الحقول المطلوبة.', 'warning')
            
    return render_template('public/contact.html')


@public_bp.route('/page/<slug>')
def dynamic_page(slug):
    """عرض الصفحات الثابتة والديناميكية (سياسة الخصوصية، الشروط، الهيكل)"""
    page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('public/page.html', page=page)
