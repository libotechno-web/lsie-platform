import os
import shutil
import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_file, Response
from flask_login import login_required, current_user
from sqlalchemy import or_, desc

from app.extensions import db
from app.models import (
    User, Role, UserRole, UserProfile,
    InnovationProject, ProjectAttachment, ProjectReview,
    Organization, Article, Event, EventRegistration,
    Opportunity, OpportunityApplication, TrainingCourse, CourseEnrollment,
    Page, Partner, SiteSetting, NavigationItem, StrategicObjective,
    OrganizationalValue, AuditLog, Notification
)
from app.forms import (
    SiteSettingsForm, StrategicObjectiveForm, OrganizationalValueForm,
    NavigationItemForm, UserManagementForm, ArticleForm, EventForm,
    OpportunityForm, TrainingCourseForm, PartnerForm, PageForm, ProjectReviewForm
)
from app.utils.decorators import admin_required, reviewer_required, editor_required
from app.utils.helpers import save_uploaded_file, slugify_text, log_audit_action, create_notification
from app.utils.excel import create_excel_response
from app.services.email_service import send_registration_confirmation_email

admin_bp = Blueprint('admin', __name__)


# -------------------------------------------------------------
# 1. لوحة المؤشرات الإدارية (Dashboard & Live KPIs)
# -------------------------------------------------------------
@admin_bp.route('/')
@login_required
@reviewer_required
def index():
    """لوحة التحكم الإدارية والمؤشرات الحية المشتقة من قاعدة البيانات"""
    stats = {
        'total_users': User.query.count(),
        'active_members': User.query.filter_by(is_approved_member=True).count(),
        'innovators_count': User.query.filter_by(account_type='innovator').count(),
        'startups_count': Organization.query.count(),
        'investors_count': User.query.filter_by(account_type='investor').count(),
        'experts_count': User.query.filter_by(account_type='expert').count(),
        'total_projects': InnovationProject.query.count(),
        'submitted_projects': InnovationProject.query.filter_by(status='submitted').count(),
        'under_review_projects': InnovationProject.query.filter(InnovationProject.status.in_(['under_review', 'under_evaluation'])).count(),
        'accepted_projects': InnovationProject.query.filter_by(status='accepted').count(),
        'opportunities_count': Opportunity.query.filter_by(status='open').count(),
        'courses_count': TrainingCourse.query.count(),
        'events_count': Event.query.count(),
        'articles_count': Article.query.count()
    }
    
    # أحدث المشاريع المقدمة التي تحتاج مراجعة
    recent_submissions = InnovationProject.query.filter(
        InnovationProject.status.in_(['submitted', 'under_review', 'under_evaluation'])
    ).order_by(InnovationProject.created_at.desc()).limit(5).all()
    
    # أحدث المستخدمين المسجلين
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # أحدث سجلات التدقيق
    recent_audit = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(6).all()
    
    return render_template(
        'admin/index.html',
        stats=stats,
        recent_submissions=recent_submissions,
        recent_users=recent_users,
        recent_audit=recent_audit
    )


# -------------------------------------------------------------
# 2. إدارة المستخدمين والأدوار (Users & Roles)
# -------------------------------------------------------------
@admin_bp.route('/users')
@login_required
@reviewer_required
def users():
    """قائمة وإدارة المستخدمين مع البحث والتصفية"""
    role_filter = request.args.get('role', '')
    account_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '') # pending, approved, suspended, all
    q = request.args.get('q', '').strip()
    
    query = User.query
    if role_filter:
        query = query.join(User.roles).filter(Role.name == role_filter)
    if account_filter:
        query = query.filter(User.account_type == account_filter)
    if status_filter == 'pending':
        query = query.filter(User.is_approved_member == False)
    elif status_filter == 'approved':
        query = query.filter(User.is_approved_member == True)
    elif status_filter == 'suspended':
        query = query.filter(User.is_active == False)
    if q:
        query = query.filter(or_(
            User.full_name.ilike(f'%{q}%'),
            User.email.ilike(f'%{q}%'),
            User.city.ilike(f'%{q}%')
        ))
        
    users_list = query.order_by(User.created_at.desc()).all()
    all_roles = Role.query.all()
    pending_count = User.query.filter_by(is_approved_member=False).count()
    return render_template('admin/users.html', users=users_list, all_roles=all_roles, query=q, status_filter=status_filter, pending_count=pending_count)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """تعديل بيانات المستخدم وأدواره وصلاحياته"""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)
    
    all_roles = Role.query.all()
    form.roles.choices = [(r.id, r.title_ar) for r in all_roles]
    
    ROLE_METADATA = {
        'admin': {
            'title': 'مدير النظام',
            'tag': 'Admin',
            'is_system_group': True,
            'icon': 'bi-shield-lock-fill',
            'color': 'danger',
            'desc': 'صلاحيات إدارية كاملة للمنصة وإعداداتها ومستخدميها والتحكم الشامل.'
        },
        'editor': {
            'title': 'محرر محتوى',
            'tag': 'Editor',
            'is_system_group': True,
            'icon': 'bi-pencil-square',
            'color': 'primary',
            'desc': 'إدارة وتحرير الأخبار والمقالات والفعاليات والصفحات التعريفية للمنصة.'
        },
        'reviewer': {
            'title': 'مراجع ومقيم مشاريع',
            'tag': 'Reviewer',
            'is_system_group': True,
            'icon': 'bi-clipboard-check-fill',
            'color': 'warning',
            'desc': 'مراجعة الأفكار والمشاريع الاستثمارية وتقييمها واعتماد انضمام الأعضاء.'
        },
        'member': {
            'title': 'عضو الجمعية',
            'tag': 'Member',
            'is_system_group': True,
            'icon': 'bi-person-badge-fill',
            'color': 'success',
            'desc': 'عضوية معتمدة ومسجلة رسمياً بالجمعية العلمية ومجتمع الابتكار.'
        },
        'innovator': {
            'title': 'مبتكر / صاحب فكرة',
            'tag': 'Innovator',
            'is_system_group': False,
            'icon': 'bi-lightbulb-fill',
            'color': 'warning',
            'desc': 'أصحاب الحلول الابتكارية وبراءات الاختراع والأفكار القابلة للتطبيق.'
        },
        'startup': {
            'title': 'شركة ناشئة / رائد أعمال',
            'tag': 'Startup',
            'is_system_group': False,
            'icon': 'bi-rocket-takeoff-fill',
            'color': 'primary',
            'desc': 'الشركات الناشئة ورواد الأعمال في مراحل التأسيس والنمو والاحتضان.'
        },
        'investor': {
            'title': 'مستثمر / جهة تمويل',
            'tag': 'Investor',
            'is_system_group': False,
            'icon': 'bi-cash-coin',
            'color': 'success',
            'desc': 'المستثمرون الأفراد وصناديق التمويل والاستثمار الجريء ودعم المشاريع.'
        },
        'expert': {
            'title': 'خبير / موجه / مدرب',
            'tag': 'Expert',
            'is_system_group': False,
            'icon': 'bi-mortarboard-fill',
            'color': 'info',
            'desc': 'الخبراء والاستشاريون في مجالات التوجيه والإرشاد والتدريب التخصصي.'
        },
        'partner_org': {
            'title': 'مؤسسة داعمة / جامعة',
            'tag': 'Partner',
            'is_system_group': False,
            'icon': 'bi-buildings-fill',
            'color': 'secondary',
            'desc': 'الجامعات وحاضنات الأعمال ومراكز البحوث والمؤسسات الشريكة للجمعية.'
        }
    }
    
    if request.method == 'GET':
        form.roles.data = [r.id for r in user.roles]
        if user.profile:
            form.current_job.data = user.profile.current_job or user.headline
            form.previous_activities.data = user.profile.previous_activities
        
    if form.validate_on_submit():
        was_approved = user.is_approved_member
        user.full_name = form.full_name.data.strip()
        user.phone = form.phone.data.strip() if form.phone.data else None
        user.city = form.city.data.strip() if form.city.data else None
        user.account_type = form.account_type.data
        user.is_active = form.is_active.data
        user.is_verified = form.is_verified.data
        user.is_approved_member = form.is_approved_member.data
        
        if form.current_job.data:
            user.headline = form.current_job.data.strip()
            
        if not user.profile:
            user.profile = UserProfile(user_id=user.id)
            
        user.profile.current_job = form.current_job.data.strip() if form.current_job.data else None
        user.profile.previous_activities = form.previous_activities.data.strip() if form.previous_activities.data else None
        
        # تحديث الأدوار الممنوحة
        selected_roles = Role.query.filter(Role.id.in_(form.roles.data)).all()
        user.roles = selected_roles
        
        db.session.commit()
        
        # إرسال بريد التأكيد إذا تم تأكيد الحساب
        if (not was_approved and user.is_approved_member) or (user.is_approved_member and form.send_confirmation_email.data and not was_approved):
            email_sent, email_msg = send_registration_confirmation_email(user)
            create_notification(
                user.id,
                'تم تأكيد واعتماد انضمامك لمجتمع الابتكار!',
                'تهانينا! تمت مراجعة واعتماد طلب انضمامك رسمياً من قبل إدارة الجمعية. يمكنك الآن الاستفادة من كافة برامج المنصة.',
                link=url_for('dashboard.index'),
                icon='bi-patch-check-fill'
            )
            if email_sent:
                flash(f'تم اعتماد وتفعيل حساب المستخدم {user.full_name} بنجاح وإرسال رسالة تأكيد رسمية إلى بريده الإلكتروني ({user.email}).', 'success')
            else:
                flash(f'تم اعتماد وتفعيل حساب المستخدم {user.full_name} بنجاح في المنظومة، ولكن تعذر إرسال البريد الإلكتروني: {email_msg}', 'warning')
        else:
            flash(f'تم تحديث بيانات المستخدم {user.full_name} بنجاح.', 'success')

        log_audit_action('user_updated', 'user', user.id, f"تعديل بيانات المستخدم: {user.email}", current_user)
        return redirect(url_for('admin.users'))
        
    current_selected_ids = set(form.roles.data or [])
    system_roles = []
    community_roles = []

    for r in all_roles:
        meta = ROLE_METADATA.get(r.name, {
            'title': r.title_ar,
            'tag': r.name.upper(),
            'is_system_group': r.is_system,
            'icon': 'bi-shield-check',
            'color': 'secondary',
            'desc': r.description or 'صلاحيات هذا الدور في المنصة.'
        })
        role_item = {
            'id': r.id,
            'name': r.name,
            'title': meta['title'],
            'tag': meta['tag'],
            'icon': meta['icon'],
            'color': meta['color'],
            'desc': r.description or meta['desc'],
            'is_system': r.is_system,
            'is_checked': r.id in current_selected_ids
        }
        if meta.get('is_system_group', r.is_system):
            system_roles.append(role_item)
        else:
            community_roles.append(role_item)

    return render_template(
        'admin/user_edit.html',
        user=user,
        form=form,
        system_roles=system_roles,
        community_roles=community_roles
    )


@admin_bp.route('/users/<int:user_id>/confirm-registration', methods=['POST'])
@login_required
@reviewer_required
def confirm_user_registration(user_id):
    """تأكيد واعتماد تسجيل المستخدم في مجتمع الابتكار وإرسال رسالة التأكيد عبر البريد الإلكتروني"""
    user = User.query.get_or_404(user_id)
    
    user.is_approved_member = True
    user.is_active = True
    user.is_verified = True
    db.session.commit()
    
    # إرسال بريد التأكيد الرسمي
    email_sent, email_msg = send_registration_confirmation_email(user)
    
    # إرسال إشعار داخلي في المنصة
    create_notification(
        user.id,
        'تم تأكيد واعتماد انضمامك لمجتمع الابتكار!',
        'تهانينا! تمت مراجعة واعتماد طلب انضمامك رسمياً لمجتمع الابتكار من قبل إدارة الجمعية. حسابك مفعل بالكامل الآن.',
        link=url_for('dashboard.index'),
        icon='bi-patch-check-fill'
    )
    
    log_audit_action('user_registration_confirmed', 'user', user.id, f"تأكيد تسجيل العضو: {user.email} وإرسال بريد التأكيد", current_user)
    
    if email_sent:
        flash(f'تم تأكيد واعتماد تسجيل المستخدم {user.full_name} بنجاح، وتم إرسال رسالة التأكيد إلى بريده الإلكتروني ({user.email}).', 'success')
    else:
        flash(f'تم تأكيد واعتماد تسجيل المستخدم {user.full_name} بنجاح في المنظومة، ولكن تنبيه: {email_msg}', 'warning')
    return redirect(request.referrer or url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """تفعيل أو تجميد حساب مستخدم"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('لا يمكنك تجميد حسابك الشخصي.', 'danger')
        return redirect(url_for('admin.users'))
        
    user.is_active = not user.is_active
    db.session.commit()
    log_audit_action('user_status_toggled', 'user', user.id, f"تغيير حالة حساب: {user.email} إلى {user.is_active}", current_user)
    flash(f"تم تغيير حالة حساب {user.full_name}.", 'info')
    return redirect(url_for('admin.users'))


# -------------------------------------------------------------
# 3. إدارة الأفكار والمشاريع والتقييم (Projects & Review System)
# -------------------------------------------------------------
@admin_bp.route('/projects')
@login_required
@reviewer_required
def projects():
    """قائمة المشاريع وإدارة دورة الحياة"""
    status_filter = request.args.get('status', '')
    sector_filter = request.args.get('sector', '')
    q = request.args.get('q', '').strip()
    
    query = InnovationProject.query
    if status_filter:
        query = query.filter(InnovationProject.status == status_filter)
    if sector_filter:
        query = query.filter(InnovationProject.sector == sector_filter)
    if q:
        query = query.filter(or_(
            InnovationProject.title.ilike(f'%{q}%'),
            InnovationProject.summary.ilike(f'%{q}%')
        ))
        
    projects_list = query.order_by(InnovationProject.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects_list, current_status=status_filter, query=q)


@admin_bp.route('/projects/<int:project_id>/review', methods=['GET', 'POST'])
@login_required
@reviewer_required
def review_project(project_id):
    """تقييم فكرة/مشروع وتسجيل الدرجات وتحديث الحالة والملاحظات"""
    project = InnovationProject.query.get_or_404(project_id)
    form = ProjectReviewForm()
    
    existing_review = ProjectReview.query.filter_by(project_id=project.id, reviewer_id=current_user.id).first()
    if request.method == 'GET' and existing_review:
        form.score_innovation.data = existing_review.score_innovation
        form.score_feasibility.data = existing_review.score_feasibility
        form.score_market_impact.data = existing_review.score_market_impact
        form.score_team.data = existing_review.score_team
        form.recommendation.data = existing_review.recommendation
        form.internal_notes.data = existing_review.internal_notes
        form.applicant_feedback.data = existing_review.applicant_feedback
        form.status.data = project.status
    elif request.method == 'GET':
        form.status.data = project.status
        
    if form.validate_on_submit():
        total = (form.score_innovation.data or 0) + (form.score_feasibility.data or 0) + \
                (form.score_market_impact.data or 0) + (form.score_team.data or 0)
                
        if not existing_review:
            existing_review = ProjectReview(
                project_id=project.id,
                reviewer_id=current_user.id
            )
            db.session.add(existing_review)
            
        existing_review.score_innovation = form.score_innovation.data
        existing_review.score_feasibility = form.score_feasibility.data
        existing_review.score_market_impact = form.score_market_impact.data
        existing_review.score_team = form.score_team.data
        existing_review.total_score = total
        existing_review.recommendation = form.recommendation.data
        existing_review.internal_notes = form.internal_notes.data.strip() if form.internal_notes.data else None
        existing_review.applicant_feedback = form.applicant_feedback.data.strip() if form.applicant_feedback.data else None
        
        # تحديث حالة المشروع في جدول المشاريع
        project.status = form.status.data
        project.status_notes_public = form.applicant_feedback.data.strip() if form.applicant_feedback.data else None
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        log_audit_action('project_reviewed', 'project', project.id, f"تقييم المشروع {project.title} بنتيجة {total}/100 وحالة {project.status}", current_user)
        create_notification(
            project.user_id,
            f"تحديث بخصوص مشروعك: {project.title}",
            f"تم تحديث حالة المشروع إلى: {project.status_label_ar}.",
            url_for('dashboard.project_detail', project_id=project.id)
        )
        
        flash(f'تم حفظ تقييم المشروع بنجاح (المجموع: {total}/100).', 'success')
        return redirect(url_for('admin.projects'))
        
    return render_template('admin/project_review.html', project=project, form=form, existing_review=existing_review)


@admin_bp.route('/projects/<int:project_id>/toggle-directory', methods=['POST'])
@login_required
@reviewer_required
def toggle_project_directory(project_id):
    """تفعيل أو تعطيل ظهور المشروع في الدليل العام"""
    project = InnovationProject.query.get_or_404(project_id)
    project.is_public_in_directory = not project.is_public_in_directory
    db.session.commit()
    flash(f'تم تحديث ظهور المشروع في الدليل العام: {"ظاهر" if project.is_public_in_directory else "مخفي"}.', 'info')
    return redirect(url_for('admin.projects'))


# -------------------------------------------------------------
# 4. إدارة الشركات الناشئة والمؤسسات الداعمة (Organizations)
# -------------------------------------------------------------
@admin_bp.route('/organizations')
@login_required
@reviewer_required
def organizations():
    """قائمة الشركات والمؤسسات والحاضنات"""
    orgs = Organization.query.order_by(Organization.created_at.desc()).all()
    return render_template('admin/organizations.html', organizations=orgs)


@admin_bp.route('/organizations/<int:org_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_organization(org_id):
    """اعتماد وتوثيق شركة ناشئة أو مؤسسة"""
    org = Organization.query.get_or_404(org_id)
    org.is_verified = not org.is_verified
    db.session.commit()
    flash(f'تم تحديث توثيق {org.name} إلى: {"موثقة" if org.is_verified else "غير موثقة"}.', 'success')
    return redirect(url_for('admin.organizations'))


# -------------------------------------------------------------
# 5. إدارة الفرص والمنح والمسابقات (Opportunities CRUD)
# -------------------------------------------------------------
@admin_bp.route('/opportunities')
@login_required
@editor_required
def opportunities():
    """قائمة الفرص والمنح المنشورة"""
    opps = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
    return render_template('admin/opportunities.html', opportunities=opps)


@admin_bp.route('/opportunities/new', methods=['GET', 'POST'])
@login_required
@editor_required
def new_opportunity():
    """إضافة فرصة أو منحة جديدة"""
    form = OpportunityForm()
    if form.validate_on_submit():
        slug = f"{slugify_text(form.title.data)}-{datetime.utcnow().strftime('%y%m%d%H%M')}"
        logo_path = None
        if form.provider_logo.data:
            try:
                logo_path = save_uploaded_file(form.provider_logo.data, 'opportunities')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/opportunity_form.html', form=form, title='إضافة فرصة جديدة')
                
        opp = Opportunity(
            title=form.title.data.strip(),
            slug=slug,
            opportunity_type=form.opportunity_type.data,
            provider_name=form.provider_name.data.strip(),
            provider_logo=logo_path,
            summary=form.summary.data.strip(),
            description=form.description.data.strip(),
            eligibility_criteria=form.eligibility_criteria.data.strip() if form.eligibility_criteria.data else None,
            target_audience=form.target_audience.data.strip() if form.target_audience.data else None,
            award_or_funding=form.award_or_funding.data.strip() if form.award_or_funding.data else None,
            sector=form.sector.data.strip() if form.sector.data else None,
            city=form.city.data.strip() if form.city.data else None,
            deadline=form.deadline.data,
            external_link=form.external_link.data.strip() if form.external_link.data else None,
            allow_internal_apply=form.allow_internal_apply.data,
            status=form.status.data,
            is_featured=form.is_featured.data
        )
        db.session.add(opp)
        db.session.commit()
        log_audit_action('opportunity_created', 'opportunity', opp.id, f"إضافة فرصة جديدة: {opp.title}", current_user)
        flash('تمت إضافة الفرصة بنجاح!', 'success')
        return redirect(url_for('admin.opportunities'))
        
    return render_template('admin/opportunity_form.html', form=form, title='إضافة فرصة جديدة')


@admin_bp.route('/opportunities/<int:opp_id>/edit', methods=['GET', 'POST'])
@login_required
@editor_required
def edit_opportunity(opp_id):
    """تعديل فرصة قائمة"""
    opp = Opportunity.query.get_or_404(opp_id)
    form = OpportunityForm(obj=opp)
    
    if form.validate_on_submit():
        opp.title = form.title.data.strip()
        opp.opportunity_type = form.opportunity_type.data
        opp.provider_name = form.provider_name.data.strip()
        opp.summary = form.summary.data.strip()
        opp.description = form.description.data.strip()
        opp.eligibility_criteria = form.eligibility_criteria.data.strip() if form.eligibility_criteria.data else None
        opp.target_audience = form.target_audience.data.strip() if form.target_audience.data else None
        opp.award_or_funding = form.award_or_funding.data.strip() if form.award_or_funding.data else None
        opp.sector = form.sector.data.strip() if form.sector.data else None
        opp.city = form.city.data.strip() if form.city.data else None
        opp.deadline = form.deadline.data
        opp.external_link = form.external_link.data.strip() if form.external_link.data else None
        opp.allow_internal_apply = form.allow_internal_apply.data
        opp.status = form.status.data
        opp.is_featured = form.is_featured.data
        
        if form.provider_logo.data:
            try:
                opp.provider_logo = save_uploaded_file(form.provider_logo.data, 'opportunities')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/opportunity_form.html', form=form, title='تعديل فرصة')
                
        db.session.commit()
        log_audit_action('opportunity_updated', 'opportunity', opp.id, f"تعديل الفرصة: {opp.title}", current_user)
        flash('تم حفظ تعديلات الفرصة بنجاح!', 'success')
        return redirect(url_for('admin.opportunities'))
        
    return render_template('admin/opportunity_form.html', form=form, title='تعديل الفرصة', opp=opp)


@admin_bp.route('/opportunities/<int:opp_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_opportunity(opp_id):
    """حذف فرصة"""
    opp = Opportunity.query.get_or_404(opp_id)
    title = opp.title
    db.session.delete(opp)
    db.session.commit()
    log_audit_action('opportunity_deleted', 'opportunity', opp_id, f"حذف الفرصة: {title}", current_user)
    flash(f"تم حذف الفرصة '{title}' بنجاح.", 'info')
    return redirect(url_for('admin.opportunities'))


@admin_bp.route('/opportunities/<int:opp_id>/applications')
@login_required
@reviewer_required
def opportunity_applications(opp_id):
    """عرض الطلبات المقدمة على فرصة محددة"""
    opp = Opportunity.query.get_or_404(opp_id)
    apps = OpportunityApplication.query.filter_by(opportunity_id=opp.id).order_by(OpportunityApplication.submitted_at.desc()).all()
    return render_template('admin/opportunity_applications.html', opportunity=opp, applications=apps)


@admin_bp.route('/opportunities/<int:opp_id>/toggle-active', methods=['POST'])
@login_required
@editor_required
def toggle_opportunity_active(opp_id):
    """تفعيل أو إلغاء تفعيل فرصة"""
    opp = Opportunity.query.get_or_404(opp_id)
    opp.is_active = not opp.is_active
    db.session.commit()
    status_str = 'تفعيل' if opp.is_active else 'تعطيل'
    log_audit_action('opportunity_status_toggled', 'opportunity', opp.id, f"{status_str} الفرصة: {opp.title}", current_user)
    flash(f"تم {status_str} الفرصة '{opp.title}' بنجاح.", 'success')
    return redirect(url_for('admin.opportunities'))


@admin_bp.route('/opportunities/<int:opp_id>/export-applications')
@login_required
@reviewer_required
def export_opportunity_applications(opp_id):
    """تصدير قائمة المتقدمين على فرصة محددة إلى ملف Excel (.xlsx) احترافي"""
    opp = Opportunity.query.get_or_404(opp_id)
    applications = OpportunityApplication.query.filter_by(opportunity_id=opp.id).order_by(OpportunityApplication.submitted_at.asc()).all()
    
    headers = ['#', 'المعرف', 'اسم المتقدم', 'البريد الإلكتروني', 'رقم الهاتف', 'موجز المقترح', 'الحالة', 'تاريخ التقديم']
    rows = []
    for idx, app_item in enumerate(applications, 1):
        rows.append([
            idx,
            app_item.id,
            app_item.applicant_name,
            app_item.applicant_email,
            app_item.applicant_phone or '-',
            app_item.proposal_summary or '-',
            app_item.status,
            app_item.submitted_at.strftime('%Y-%m-%d %H:%M') if app_item.submitted_at else '-'
        ])
        
    date_stamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
    ascii_filename = f"opportunity_{opp.id}_applicants_{date_stamp}.xlsx"
    arabic_filename = f"متقدمو_فرصة_{opp.id}_{date_stamp}.xlsx"
    
    log_audit_action('opportunity_applications_exported', 'opportunity', opp.id, f"تصدير إكسيل لطلبات فرصة: {opp.title}", current_user)
    return create_excel_response('المتقدمون', f"قائمة المتقدمين: {opp.title}", headers, rows, ascii_filename, arabic_filename)


# -------------------------------------------------------------
# 6. إدارة الدورات والتدريب (Training Courses CRUD)
# -------------------------------------------------------------
@admin_bp.route('/training')
@login_required
@editor_required
def training():
    """قائمة الدورات والبرامج التدريبية"""
    courses = TrainingCourse.query.order_by(TrainingCourse.start_date.desc()).all()
    return render_template('admin/training_list.html', courses=courses)


@admin_bp.route('/training/new', methods=['GET', 'POST'])
@login_required
@editor_required
def new_course():
    """إضافة دورة تدريبية جديدة"""
    form = TrainingCourseForm()
    if form.validate_on_submit():
        slug = f"{slugify_text(form.title.data)}-{datetime.utcnow().strftime('%y%m%d%H%M')}"
        cover_path = None
        if form.cover_image.data:
            try:
                cover_path = save_uploaded_file(form.cover_image.data, 'courses')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/training_form.html', form=form, title='إضافة برنامج تدريبي')
                
        course = TrainingCourse(
            title=form.title.data.strip(),
            slug=slug,
            trainer_name=form.trainer_name.data.strip(),
            trainer_title=form.trainer_title.data.strip() if form.trainer_title.data else None,
            course_type=form.course_type.data,
            delivery_mode=form.delivery_mode.data,
            location_or_link=form.location_or_link.data.strip() if form.location_or_link.data else None,
            summary=form.summary.data.strip(),
            description=form.description.data.strip(),
            learning_objectives=form.learning_objectives.data.strip() if form.learning_objectives.data else None,
            prerequisites=form.prerequisites.data.strip() if form.prerequisites.data else None,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            duration_hours=form.duration_hours.data,
            max_seats=form.max_seats.data,
            certificate_included=form.certificate_included.data,
            is_free=form.is_free.data,
            cover_image=cover_path,
            registration_status=form.registration_status.data,
            is_featured=form.is_featured.data
        )
        db.session.add(course)
        db.session.commit()
        log_audit_action('course_created', 'course', course.id, f"إضافة دورة تدريبية: {course.title}", current_user)
        flash('تمت إضافة الدورة التدريبية بنجاح!', 'success')
        return redirect(url_for('admin.training'))
        
    return render_template('admin/training_form.html', form=form, title='إضافة برنامج تدريبي')


@admin_bp.route('/training/<int:course_id>/enrollments')
@login_required
@editor_required
def course_enrollments(course_id):
    """عرض قائمة المتدربين المسجلين في الدورة"""
    course = TrainingCourse.query.get_or_404(course_id)
    enrollments = CourseEnrollment.query.filter_by(course_id=course.id).order_by(CourseEnrollment.enrolled_at.desc()).all()
    return render_template('admin/course_enrollments.html', course=course, enrollments=enrollments)


@admin_bp.route('/training/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@editor_required
def edit_course(course_id):
    """تعديل برنامج تدريبي قائم"""
    course = TrainingCourse.query.get_or_404(course_id)
    form = TrainingCourseForm(obj=course)
    if form.validate_on_submit():
        course.title = form.title.data.strip()
        course.trainer_name = form.trainer_name.data.strip()
        course.trainer_title = form.trainer_title.data.strip() if form.trainer_title.data else None
        course.course_type = form.course_type.data
        course.delivery_mode = form.delivery_mode.data
        course.location_or_link = form.location_or_link.data.strip() if form.location_or_link.data else None
        course.summary = form.summary.data.strip()
        course.description = form.description.data.strip()
        course.learning_objectives = form.learning_objectives.data.strip() if form.learning_objectives.data else None
        course.prerequisites = form.prerequisites.data.strip() if form.prerequisites.data else None
        course.start_date = form.start_date.data
        course.end_date = form.end_date.data
        course.duration_hours = form.duration_hours.data
        course.max_seats = form.max_seats.data
        course.certificate_included = form.certificate_included.data
        course.is_free = form.is_free.data
        course.registration_status = form.registration_status.data
        course.is_featured = form.is_featured.data
        
        if form.cover_image.data:
            try:
                course.cover_image = save_uploaded_file(form.cover_image.data, 'courses')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/training_form.html', form=form, title='تعديل برنامج تدريبي', course=course)
                
        db.session.commit()
        log_audit_action('course_updated', 'course', course.id, f"تعديل الدورة: {course.title}", current_user)
        flash('تم حفظ تعديلات البرنامج التدريبي بنجاح!', 'success')
        return redirect(url_for('admin.training'))
        
    return render_template('admin/training_form.html', form=form, title='تعديل برنامج تدريبي', course=course)


@admin_bp.route('/training/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    """حذف دورة تدريبية"""
    course = TrainingCourse.query.get_or_404(course_id)
    title = course.title
    db.session.delete(course)
    db.session.commit()
    log_audit_action('course_deleted', 'course', course_id, f"حذف دورة تدريبية: {title}", current_user)
    flash(f"تم حذف البرنامج التدريبي '{title}' بنجاح.", 'info')
    return redirect(url_for('admin.training'))


@admin_bp.route('/training/<int:course_id>/toggle-active', methods=['POST'])
@login_required
@editor_required
def toggle_course_active(course_id):
    """تفعيل أو تعطيل البرنامج التدريبي"""
    course = TrainingCourse.query.get_or_404(course_id)
    course.is_active = not course.is_active
    if not course.is_active:
        course.registration_status = 'closed'
    else:
        if course.registration_status == 'closed':
            course.registration_status = 'open'
    db.session.commit()
    status_str = 'تفعيل' if course.is_active else 'تعطيل'
    log_audit_action('course_status_toggled', 'course', course.id, f"{status_str} الدورة: {course.title}", current_user)
    flash(f"تم {status_str} البرنامج التدريبي '{course.title}' بنجاح.", 'success')
    return redirect(url_for('admin.training'))


@admin_bp.route('/training/<int:course_id>/export-enrollments')
@login_required
@editor_required
def export_course_enrollments(course_id):
    """تصدير قائمة المسجلين في دورة تدريبية محددة إلى ملف Excel (.xlsx) احترافي"""
    course = TrainingCourse.query.get_or_404(course_id)
    enrollments = CourseEnrollment.query.filter_by(course_id=course.id).order_by(CourseEnrollment.enrolled_at.asc()).all()
    
    headers = ['#', 'المعرف', 'اسم المتدرب', 'البريد الإلكتروني', 'رقم الهاتف', 'دافع الالتحاق', 'الحالة', 'تاريخ التسجيل']
    rows = []
    for idx, en in enumerate(enrollments, 1):
        rows.append([
            idx,
            en.id,
            en.full_name,
            en.email,
            en.phone or '-',
            en.motivation or '-',
            en.status,
            en.enrolled_at.strftime('%Y-%m-%d %H:%M') if en.enrolled_at else '-'
        ])
        
    date_stamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
    ascii_filename = f"course_{course.id}_trainees_{date_stamp}.xlsx"
    arabic_filename = f"متدربو_برنامج_{course.id}_{date_stamp}.xlsx"
    
    log_audit_action('course_enrollments_exported', 'course', course.id, f"تصدير إكسيل لمتدربي دورة: {course.title}", current_user)
    return create_excel_response('المتدربون', f"قائمة متدربي: {course.title}", headers, rows, ascii_filename, arabic_filename)


# -------------------------------------------------------------
# 7. إدارة الأخبار والمقالات (Articles & News CRUD)
# -------------------------------------------------------------
@admin_bp.route('/articles')
@login_required
@editor_required
def articles():
    """قائمة الأخبار والمقالات"""
    arts = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', articles=arts)


@admin_bp.route('/articles/new', methods=['GET', 'POST'])
@login_required
@editor_required
def new_article():
    """إضافة خبر أو مقال جديد"""
    form = ArticleForm()
    if form.validate_on_submit():
        slug = f"{slugify_text(form.title.data)}-{datetime.utcnow().strftime('%y%m%d%H%M')}"
        img_path = None
        if form.featured_image.data:
            try:
                img_path = save_uploaded_file(form.featured_image.data, 'news')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/article_form.html', form=form, title='إضافة خبر / مقال')
                
        article = Article(
            title=form.title.data.strip(),
            slug=slug,
            category=form.category.data,
            summary=form.summary.data.strip(),
            content_html=form.content_html.data.strip(),
            featured_image=img_path,
            author_id=current_user.id,
            author_name=form.author_name.data.strip() if form.author_name.data else current_user.full_name,
            status=form.status.data,
            is_featured=form.is_featured.data,
            published_at=datetime.utcnow() if form.status.data == 'published' else None
        )
        db.session.add(article)
        db.session.commit()
        log_audit_action('article_created', 'article', article.id, f"إضافة مقال: {article.title}", current_user)
        flash('تم نشر/حفظ الخبر بنجاح!', 'success')
        return redirect(url_for('admin.articles'))
        
    return render_template('admin/article_form.html', form=form, title='إضافة خبر / مقال')


@admin_bp.route('/articles/<int:art_id>/delete', methods=['POST'])
@login_required
@editor_required
def delete_article(art_id):
    """حذف خبر أو مقال"""
    art = Article.query.get_or_404(art_id)
    title = art.title
    db.session.delete(art)
    db.session.commit()
    log_audit_action('article_deleted', 'article', art_id, f"حذف مقال: {title}", current_user)
    flash(f"تم حذف '{title}' بنجاح.", 'info')
    return redirect(url_for('admin.articles'))


# -------------------------------------------------------------
# 8. إدارة الفعاليات (Events CRUD)
# -------------------------------------------------------------
@admin_bp.route('/events')
@login_required
@editor_required
def events():
    """قائمة الفعاليات"""
    events_list = Event.query.order_by(Event.start_time.desc()).all()
    return render_template('admin/events_list.html', events=events_list)


@admin_bp.route('/events/new', methods=['GET', 'POST'])
@login_required
@editor_required
def new_event():
    """إضافة فعالية جديدة"""
    form = EventForm()
    if form.validate_on_submit():
        slug = f"{slugify_text(form.title.data)}-{datetime.utcnow().strftime('%y%m%d%H%M')}"
        img_path = None
        if form.cover_image.data:
            try:
                img_path = save_uploaded_file(form.cover_image.data, 'events')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/event_form.html', form=form, title='إضافة فعالية جديدة')
                
        event = Event(
            title=form.title.data.strip(),
            title_en=form.title_en.data.strip() if form.title_en.data else None,
            slug=slug,
            event_type=form.event_type.data,
            summary=form.summary.data.strip(),
            summary_en=form.summary_en.data.strip() if form.summary_en.data else None,
            description=form.description.data.strip(),
            description_en=form.description_en.data.strip() if form.description_en.data else None,
            cover_image=img_path,
            location_type=form.location_type.data,
            location_name=form.location_name.data.strip() if form.location_name.data else None,
            location_name_en=form.location_name_en.data.strip() if form.location_name_en.data else None,
            city=form.city.data.strip() if form.city.data else 'غريان',
            city_en=form.city_en.data.strip() if form.city_en.data else None,
            online_link=form.online_link.data.strip() if form.online_link.data else None,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            capacity=form.capacity.data,
            is_registration_open=form.is_registration_open.data,
            is_featured=form.is_featured.data,
            is_published=form.is_published.data
        )
        db.session.add(event)
        db.session.commit()
        log_audit_action('event_created', 'event', event.id, f"إضافة فعالية: {event.title}", current_user)
        flash('تمت إضافة الفعالية بنجاح!', 'success')
        return redirect(url_for('admin.events'))
        
    return render_template('admin/event_form.html', form=form, title='إضافة فعالية جديدة')


@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@editor_required
def edit_event(event_id):
    """تعديل فعالية قائمة"""
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.title = form.title.data.strip()
        event.title_en = form.title_en.data.strip() if form.title_en.data else None
        event.event_type = form.event_type.data
        event.summary = form.summary.data.strip()
        event.summary_en = form.summary_en.data.strip() if form.summary_en.data else None
        event.description = form.description.data.strip()
        event.description_en = form.description_en.data.strip() if form.description_en.data else None
        event.location_type = form.location_type.data
        event.location_name = form.location_name.data.strip() if form.location_name.data else None
        event.location_name_en = form.location_name_en.data.strip() if form.location_name_en.data else None
        event.city = form.city.data.strip() if form.city.data else 'غريان'
        event.city_en = form.city_en.data.strip() if form.city_en.data else None
        event.online_link = form.online_link.data.strip() if form.online_link.data else None
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.capacity = form.capacity.data
        event.is_registration_open = form.is_registration_open.data
        event.is_featured = form.is_featured.data
        event.is_published = form.is_published.data
        
        if form.cover_image.data:
            try:
                event.cover_image = save_uploaded_file(form.cover_image.data, 'events')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/event_form.html', form=form, title='تعديل الفعالية', event=event)
                
        db.session.commit()
        log_audit_action('event_updated', 'event', event.id, f"تعديل فعالية: {event.title}", current_user)
        flash('تم حفظ تعديلات الفعالية بنجاح!', 'success')
        return redirect(url_for('admin.events'))
        
    return render_template('admin/event_form.html', form=form, title='تعديل الفعالية', event=event)


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """حذف فعالية"""
    event = Event.query.get_or_404(event_id)
    title = event.title
    db.session.delete(event)
    db.session.commit()
    log_audit_action('event_deleted', 'event', event_id, f"حذف فعالية: {title}", current_user)
    flash(f"تم حذف الفعالية '{title}' بنجاح.", 'info')
    return redirect(url_for('admin.events'))


@admin_bp.route('/events/<int:event_id>/toggle-active', methods=['POST'])
@login_required
@editor_required
def toggle_event_active(event_id):
    """تفعيل / تعطيل الفعالية (النشر والتسجيل)"""
    event = Event.query.get_or_404(event_id)
    event.is_published = not event.is_published
    event.is_registration_open = event.is_published
    db.session.commit()
    status_str = 'تفعيل وإتاحة' if event.is_published else 'تعطيل وإخفاء'
    log_audit_action('event_status_toggled', 'event', event.id, f"{status_str} الفعالية: {event.title}", current_user)
    flash(f"تم {status_str} الفعالية '{event.title}' بنجاح.", 'success')
    return redirect(url_for('admin.events'))


@admin_bp.route('/events/<int:event_id>/registrations')
@login_required
@editor_required
def event_registrations(event_id):
    """عرض قائمة المسجلين لحضور الفعالية"""
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event.id).order_by(EventRegistration.registered_at.desc()).all()
    return render_template('admin/event_registrations.html', event=event, registrations=registrations)


@admin_bp.route('/events/<int:event_id>/export-registrations')
@login_required
@editor_required
def export_event_registrations(event_id):
    """تصدير قائمة المسجلين في فعالية محددة إلى ملف Excel (.xlsx) احترافي"""
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event.id).order_by(EventRegistration.registered_at.asc()).all()
    
    headers = ['#', 'المعرف', 'اسم المشارك', 'البريد الإلكتروني', 'رقم الهاتف', 'الجهة / المنظمة', 'ملاحظات الحضور', 'الحالة', 'تاريخ التسجيل']
    rows = []
    for idx, r in enumerate(registrations, 1):
        rows.append([
            idx,
            r.id,
            r.full_name,
            r.email,
            r.phone or '-',
            r.organization or '-',
            r.notes or '-',
            r.status,
            r.registered_at.strftime('%Y-%m-%d %H:%M') if r.registered_at else '-'
        ])
        
    date_stamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
    ascii_filename = f"event_{event.id}_attendees_{date_stamp}.xlsx"
    arabic_filename = f"حضور_فعالية_{event.id}_{date_stamp}.xlsx"
    
    log_audit_action('event_registrations_exported', 'event', event.id, f"تصدير إكسيل لمسجلي فعالية: {event.title}", current_user)
    return create_excel_response('حضور الفعالية', f"قائمة حضور: {event.title}", headers, rows, ascii_filename, arabic_filename)


# -------------------------------------------------------------
# 9. إدارة الشركاء (Partners CRUD)
# -------------------------------------------------------------
@admin_bp.route('/partners')
@login_required
@editor_required
def partners():
    """قائمة الشركاء والرعاة"""
    partners_list = Partner.query.order_by(Partner.order_index).all()
    return render_template('admin/partners_list.html', partners=partners_list)


@admin_bp.route('/partners/new', methods=['GET', 'POST'])
@login_required
@editor_required
def new_partner():
    """إضافة شريك جديد"""
    form = PartnerForm()
    if form.validate_on_submit():
        logo_path = None
        if form.logo.data:
            try:
                logo_path = save_uploaded_file(form.logo.data, 'partners')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/partner_form.html', form=form, title='إضافة شريك')
                
        partner = Partner(
            name=form.name.data.strip(),
            partner_type=form.partner_type.data,
            website_url=form.website_url.data.strip() if form.website_url.data else None,
            description=form.description.data.strip() if form.description.data else None,
            logo=logo_path,
            order_index=form.order_index.data,
            is_active=form.is_active.data
        )
        db.session.add(partner)
        db.session.commit()
        log_audit_action('partner_added', 'partner', partner.id, f"إضافة شريك: {partner.name}", current_user)
        flash('تمت إضافة الشريك بنجاح!', 'success')
        return redirect(url_for('admin.partners'))
        
    return render_template('admin/partner_form.html', form=form, title='إضافة شريك')


# -------------------------------------------------------------
# 10. إدارة الصفحات والقوائم (Pages & Navigation Items)
# -------------------------------------------------------------
@admin_bp.route('/pages')
@login_required
@editor_required
def pages():
    """قائمة الصفحات الثابتة"""
    pages_list = Page.query.order_by(Page.order_index).all()
    return render_template('admin/pages_list.html', pages=pages_list)


@admin_bp.route('/pages/new', methods=['GET', 'POST'])
@login_required
@editor_required
def new_page():
    """إضافة صفحة جديدة"""
    form = PageForm()
    if form.validate_on_submit():
        page = Page(
            title=form.title.data.strip(),
            slug=slugify_text(form.slug.data.strip()),
            summary=form.summary.data.strip() if form.summary.data else None,
            content_html=form.content_html.data.strip(),
            is_published=form.is_published.data,
            show_in_footer=form.show_in_footer.data,
            order_index=form.order_index.data
        )
        db.session.add(page)
        db.session.commit()
        log_audit_action('page_created', 'page', page.id, f"إنشاء صفحة: {page.title}", current_user)
        flash('تم إنشاء الصفحة بنجاح!', 'success')
        return redirect(url_for('admin.pages'))
        
    return render_template('admin/page_form.html', form=form, title='إضافة صفحة جديدة')


@admin_bp.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
@editor_required
def edit_page(page_id):
    """تعديل صفحة قائمة"""
    page = Page.query.get_or_404(page_id)
    form = PageForm(obj=page)
    if form.validate_on_submit():
        page.title = form.title.data.strip()
        page.slug = slugify_text(form.slug.data.strip())
        page.summary = form.summary.data.strip() if form.summary.data else None
        page.content_html = form.content_html.data.strip()
        page.is_published = form.is_published.data
        page.show_in_footer = form.show_in_footer.data
        page.order_index = form.order_index.data
        db.session.commit()
        log_audit_action('page_updated', 'page', page.id, f"تعديل صفحة: {page.title}", current_user)
        flash('تم حفظ تعديلات الصفحة بنجاح!', 'success')
        return redirect(url_for('admin.pages'))
    return render_template('admin/page_form.html', form=form, title='تعديل الصفحة', page=page)


@admin_bp.route('/navigation')
@login_required
@admin_required
def navigation():
    """إدارة عناصر القوائم العلوية والتذييل"""
    nav_items = NavigationItem.query.order_by(NavigationItem.order_index).all()
    form = NavigationItemForm()
    return render_template('admin/navigation.html', items=nav_items, form=form)


@admin_bp.route('/navigation/new', methods=['POST'])
@login_required
@admin_required
def new_navigation_item():
    """إضافة عنصر قائمة جديد"""
    form = NavigationItemForm()
    if form.validate_on_submit():
        nav = NavigationItem(
            title_ar=form.title_ar.data.strip(),
            title_en=form.title_en.data.strip() if form.title_en.data else None,
            url=form.url.data.strip(),
            icon=form.icon.data.strip() if form.icon.data else None,
            order_index=form.order_index.data,
            is_active=form.is_active.data,
            is_external=form.is_external.data,
            location=form.location.data
        )
        db.session.add(nav)
        db.session.commit()
        flash('تمت إضافة عنصر القائمة بنجاح.', 'success')
    return redirect(url_for('admin.navigation'))


# -------------------------------------------------------------
# 11. إدارة الإعدادات الشاملة والشعار والهوية وروابط التواصل
# -------------------------------------------------------------
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """إدارة إعدادات المنصة: الشعار، الألوان، النبذة، الرؤية، الرسالة، التواصل، السوشيال ميديا"""
    form = SiteSettingsForm()
    
    # قائمة المفاتيح التي نديرها
    keys = [
        'site_name', 'site_name_en', 'site_acronym', 'hero_title', 'hero_subtitle',
        'about_intro', 'official_mission', 'official_vision', 'establishment_decree',
        'headquarters', 'certificate_number', 'primary_color', 'secondary_color', 'accent_color',
        'contact_email', 'contact_phone', 'contact_address',
        'facebook_url', 'instagram_url', 'twitter_x_url', 'linkedin_url', 'youtube_url',
        'mail_server', 'mail_port', 'mail_username', 'mail_password', 'mail_use_tls'
    ]
    
    if request.method == 'GET':
        for k in keys:
            if hasattr(form, k):
                field = getattr(form, k)
                if k == 'mail_port':
                    field.data = int(SiteSetting.get_value(k, 587) or 587)
                elif k == 'mail_use_tls':
                    field.data = str(SiteSetting.get_value(k, 'true')).lower() in ('true', '1')
                else:
                    field.data = SiteSetting.get_value(k, '')
                
    if form.validate_on_submit():
        for k in keys:
            if hasattr(form, k):
                val = getattr(form, k).data
                if isinstance(val, bool):
                    SiteSetting.set_value(k, 'true' if val else 'false')
                else:
                    SiteSetting.set_value(k, str(val).strip() if val is not None else '')
                
        # رفع الشعار الجديد إن تم تحديده
        if form.logo.data:
            try:
                logo_path = save_uploaded_file(form.logo.data, 'branding')
                SiteSetting.set_value('logo_path', logo_path, group='appearance', label='شعار المنصة')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('admin/settings.html', form=form)
                
        log_audit_action('settings_updated', 'settings', None, "تحديث إعدادات المنصة والهوية البصرية والبريد الإلكتروني", current_user)
        flash('تم حفظ جميع الإعدادات وإعدادات البريد بنجاح!', 'success')
        return redirect(url_for('admin.settings'))
        
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/settings/test-email', methods=['POST'])
@login_required
@admin_required
def test_email():
    """اختبار اتصال خادم البريد وإرسال رسالة تجريبية"""
    from app.services.email_service import send_test_email
    target_email = request.form.get('target_email', '').strip() or 'libotechno@gmail.com'
    success, message = send_test_email(target_email)
    if success:
        flash(f'نجح إرسال البريد التجريبي إلى ({target_email})! إعدادات خادم البريد الإلكتروني تعمل بنجاح.', 'success')
    else:
        flash(f'فشل إرسال البريد التجريبي: {message}', 'danger')
    return redirect(url_for('admin.settings'))


# -------------------------------------------------------------
# 12. إدارة الأهداف الاستراتيجية والقيم
# -------------------------------------------------------------
@admin_bp.route('/objectives', methods=['GET', 'POST'])
@login_required
@admin_required
def objectives():
    """إدارة الأهداف الاستراتيجية والقيم المؤسسية"""
    objs = StrategicObjective.query.order_by(StrategicObjective.order_index).all()
    vals = OrganizationalValue.query.order_by(OrganizationalValue.order_index).all()
    obj_form = StrategicObjectiveForm()
    val_form = OrganizationalValueForm()
    return render_template('admin/objectives.html', objectives=objs, values=vals, obj_form=obj_form, val_form=val_form)


@admin_bp.route('/objectives/new', methods=['POST'])
@login_required
@admin_required
def new_objective():
    form = StrategicObjectiveForm()
    if form.validate_on_submit():
        obj = StrategicObjective(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            icon=form.icon.data.strip() if form.icon.data else 'bi-bullseye',
            order_index=form.order_index.data,
            is_active=form.is_active.data
        )
        db.session.add(obj)
        db.session.commit()
        flash('تمت إضافة الهدف الاستراتيجي بنجاح.', 'success')
    return redirect(url_for('admin.objectives'))


@admin_bp.route('/values/new', methods=['POST'])
@login_required
@admin_required
def new_value():
    form = OrganizationalValueForm()
    if form.validate_on_submit():
        val = OrganizationalValue(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            icon=form.icon.data.strip() if form.icon.data else 'bi-shield-check',
            order_index=form.order_index.data,
            is_active=form.is_active.data
        )
        db.session.add(val)
        db.session.commit()
        flash('تمت إضافة القيمة المؤسسية بنجاح.', 'success')
    return redirect(url_for('admin.objectives'))


# -------------------------------------------------------------
# 13. سجل التدقيق والأنشطة الإدارية (Audit Logs)
# -------------------------------------------------------------
@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """سجل التدقيق لمراقبة العمليات الحساسة في النظام"""
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_template('admin/audit_logs.html', logs=logs)


# -------------------------------------------------------------
# 14. النسخ الاحتياطي والاستعادة (Backup & Restore)
# -------------------------------------------------------------
@admin_bp.route('/backups')
@login_required
@admin_required
def backups():
    """إدارة النسخ الاحتياطية لقاعدة البيانات"""
    backup_dir = current_app.config['BACKUP_FOLDER']
    files = []
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            if f.endswith('.db') or f.endswith('.sql'):
                fp = os.path.join(backup_dir, f)
                files.append({
                    'filename': f,
                    'size_kb': round(os.path.getsize(fp) / 1024, 1),
                    'created_at': datetime.fromtimestamp(os.path.getctime(fp)).strftime('%Y-%m-%d %H:%M:%S')
                })
    files = sorted(files, key=lambda x: x['created_at'], reverse=True)
    return render_template('admin/backups.html', backups=files)


@admin_bp.route('/backups/create', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """إنشاء نسخة احتياطية فورية لقاعدة بيانات SQLite"""
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if 'sqlite:///' in db_uri:
        source_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(source_path):
            source_path = os.path.join(current_app.root_path, '..', source_path)
        
        backup_filename = f"lsie_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
        dest_path = os.path.join(current_app.config['BACKUP_FOLDER'], backup_filename)
        
        try:
            shutil.copy2(source_path, dest_path)
            log_audit_action('backup_created', 'database', None, f"إنشاء نسخة احتياطية: {backup_filename}", current_user)
            flash(f"تم إنشاء النسخة الاحتياطية بنجاح: {backup_filename}", 'success')
        except Exception as e:
            flash(f"خطأ أثناء إنشاء النسخة الاحتياطية: {e}", 'danger')
    else:
        flash('قاعدة البيانات ليست SQLite محلية، يرجى استخدام أدوات النسخ الاحتياطي الخاصة بالخادم (مثل pg_dump).', 'info')
        
    return redirect(url_for('admin.backups'))


@admin_bp.route('/backups/<filename>/download')
@login_required
@admin_required
def download_backup(filename):
    """تنزيل ملف النسخة الاحتياطية"""
    backup_path = os.path.join(current_app.config['BACKUP_FOLDER'], filename)
    if os.path.exists(backup_path):
        return send_file(backup_path, as_attachment=True)
    abort(404)


# -------------------------------------------------------------
# 15. مركز التقارير الشامل وتصدير البيانات (Reports & Data Export)
# -------------------------------------------------------------
@admin_bp.route('/reports')
@login_required
@reviewer_required
def reports():
    """مركز التقارير الموحد وتصدير بيانات الحركات والمسجلين لجميع برامج وفعاليات الجمعية"""
    summary = {
        'total_enrollments': CourseEnrollment.query.count(),
        'total_event_registrations': EventRegistration.query.count(),
        'total_applications': OpportunityApplication.query.count(),
        'total_projects': InnovationProject.query.count(),
        'total_users': User.query.count(),
        'total_startups': Organization.query.count(),
        'total_audit_logs': AuditLog.query.count(),
        'courses_count': TrainingCourse.query.count(),
        'events_count': Event.query.count(),
        'opportunities_count': Opportunity.query.count()
    }
    return render_template('admin/reports.html', summary=summary)


@admin_bp.route('/reports/export/<report_type>')
@login_required
@reviewer_required
def export_report(report_type):
    """تصدير تقارير وبيانات المنصة بصيغة Microsoft Excel (.xlsx) الاحترافية"""
    date_stamp = datetime.utcnow().strftime('%Y%m%d_%H%M')
    
    if report_type == 'projects':
        headers = ['#', 'المعرف', 'عنوان المشروع', 'المبتكر / صاحب الفكرة', 'البريد الإلكتروني', 'القطاع', 'المدينة', 'مرحلة النضج', 'الحالة', 'تاريخ التقديم']
        rows = []
        projects_data = InnovationProject.query.order_by(InnovationProject.created_at.desc()).all()
        for idx, p in enumerate(projects_data, 1):
            rows.append([
                idx,
                p.id,
                p.title,
                p.owner.full_name if p.owner else '-',
                p.owner.email if p.owner else '-',
                p.sector or '-',
                p.city or '-',
                p.stage_label_ar,
                p.status_label_ar,
                p.created_at.strftime('%Y-%m-%d') if p.created_at else '-'
            ])
        ascii_filename = f"innovation_projects_{date_stamp}.xlsx"
        arabic_filename = f"سجل_المشاريع_الابتكارية_{date_stamp}.xlsx"
        sheet_title = "المشاريع"
        title_text = "السجل الوطني للمشاريع والأفكار الابتكارية"

    elif report_type == 'users':
        headers = ['#', 'المعرف', 'الاسم الكامل', 'البريد الإلكتروني', 'رقم الهاتف', 'المدينة', 'الوظيفة الحالية', 'نوع الحساب', 'عضوية معتمدة', 'سيرة ذاتية', 'نشط', 'موثق', 'تاريخ التسجيل']
        rows = []
        users_data = User.query.order_by(User.created_at.desc()).all()
        for idx, u in enumerate(users_data, 1):
            rows.append([
                idx,
                u.id,
                u.full_name,
                u.email,
                u.phone or '-',
                u.city or '-',
                u.current_job or u.headline or '-',
                u.account_type,
                'نعم (مؤكد)' if u.is_approved_member else 'قيد التأكيد',
                'نعم' if u.cv_file else 'لا',
                'نعم' if u.is_active else 'لا',
                'نعم' if u.is_verified else 'لا',
                u.created_at.strftime('%Y-%m-%d') if u.created_at else '-'
            ])
        ascii_filename = f"users_directory_{date_stamp}.xlsx"
        arabic_filename = f"دليل_المستخدمين_والأعضاء_{date_stamp}.xlsx"
        sheet_title = "المستخدمون"
        title_text = "دليل المستخدمين والأعضاء المسجلين بالجمعية"

    elif report_type == 'startups':
        headers = ['#', 'المعرف', 'اسم الشركة / المنظمة', 'النوع', 'القطاع', 'المدينة', 'مرحلة النمو', 'الموقع الإلكتروني', 'موثقة']
        rows = []
        startups_data = Organization.query.order_by(Organization.created_at.desc()).all()
        for idx, s in enumerate(startups_data, 1):
            rows.append([
                idx,
                s.id,
                s.name,
                s.org_type,
                s.sector or '-',
                s.city or '-',
                s.stage or '-',
                s.website or '-',
                'نعم' if s.is_verified else 'لا'
            ])
        ascii_filename = f"startups_directory_{date_stamp}.xlsx"
        arabic_filename = f"دليل_الشركات_والحاضنات_{date_stamp}.xlsx"
        sheet_title = "الشركات"
        title_text = "دليل الشركات الناشئة ومسرعات الأعمال والحاضنات"

    elif report_type == 'enrollments':
        headers = ['#', 'المعرف', 'البرنامج التدريبي', 'اسم المتدرب', 'البريد الإلكتروني', 'رقم الهاتف', 'دافع الالتحاق والملاحظات', 'الحالة', 'تاريخ التسجيل']
        rows = []
        enrollments_data = CourseEnrollment.query.order_by(CourseEnrollment.enrolled_at.desc()).all()
        for idx, e in enumerate(enrollments_data, 1):
            course_title = e.course.title if e.course else 'غير محدد'
            rows.append([
                idx,
                e.id,
                course_title,
                e.full_name,
                e.email,
                e.phone or '-',
                e.motivation or '-',
                e.status,
                e.enrolled_at.strftime('%Y-%m-%d %H:%M') if e.enrolled_at else '-'
            ])
        ascii_filename = f"all_enrollments_{date_stamp}.xlsx"
        arabic_filename = f"السجل_الشامل_للمتدربين_{date_stamp}.xlsx"
        sheet_title = "المتدربون"
        title_text = "السجل الشامل للملتحقين بكافة البرامج التدريبية والأكاديمية"

    elif report_type == 'event_registrations':
        headers = ['#', 'المعرف', 'الفعالية / المؤتمر', 'اسم المشارك', 'البريد الإلكتروني', 'رقم الهاتف', 'الجهة / المنظمة', 'ملاحظات الحضور', 'الحالة', 'تاريخ الحجز']
        rows = []
        registrations_data = EventRegistration.query.order_by(EventRegistration.registered_at.desc()).all()
        for idx, r in enumerate(registrations_data, 1):
            event_title = r.event.title if r.event else 'غير محدد'
            rows.append([
                idx,
                r.id,
                event_title,
                r.full_name,
                r.email,
                r.phone or '-',
                r.organization or '-',
                r.notes or '-',
                r.status,
                r.registered_at.strftime('%Y-%m-%d %H:%M') if r.registered_at else '-'
            ])
        ascii_filename = f"all_event_registrations_{date_stamp}.xlsx"
        arabic_filename = f"السجل_الشامل_لحضور_الفعاليات_{date_stamp}.xlsx"
        sheet_title = "حضور الفعاليات"
        title_text = "السجل الشامل للحضور وتذاكر الفعاليات والمؤتمرات"

    elif report_type == 'applications':
        headers = ['#', 'المعرف', 'الفرصة / المنحة', 'اسم المتقدم', 'البريد الإلكتروني', 'رقم الهاتف', 'موجز المقترح', 'الحالة', 'تاريخ التقديم']
        rows = []
        apps_data = OpportunityApplication.query.order_by(OpportunityApplication.submitted_at.desc()).all()
        for idx, a in enumerate(apps_data, 1):
            opp_title = a.opportunity.title if a.opportunity else 'غير محدد'
            rows.append([
                idx,
                a.id,
                opp_title,
                a.applicant_name,
                a.applicant_email,
                a.applicant_phone or '-',
                a.proposal_summary or '-',
                a.status,
                a.submitted_at.strftime('%Y-%m-%d %H:%M') if a.submitted_at else '-'
            ])
        ascii_filename = f"all_applications_{date_stamp}.xlsx"
        arabic_filename = f"السجل_الشامل_لطلبات_المنح_{date_stamp}.xlsx"
        sheet_title = "الطلبات"
        title_text = "السجل الشامل لطلبات التقديم على المنح والاحتضان والمسابقات"

    elif report_type == 'audit_logs':
        headers = ['#', 'المعرف', 'المستخدم المنفذ', 'نوع العملية', 'نوع المورد', 'معرف المورد', 'التفاصيل', 'عنوان IP', 'التاريخ والوقت']
        rows = []
        audit_data = AuditLog.query.order_by(AuditLog.created_at.desc()).all()
        for idx, log in enumerate(audit_data, 1):
            user_name = log.user.full_name if log.user else (log.user_email or 'النظام')
            rows.append([
                idx,
                log.id,
                user_name,
                log.action,
                log.resource_type or '-',
                log.resource_id or '-',
                log.details or '-',
                log.ip_address or '-',
                log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '-'
            ])
        ascii_filename = f"audit_logs_{date_stamp}.xlsx"
        arabic_filename = f"سجل_التدقيق_والرقابة_{date_stamp}.xlsx"
        sheet_title = "سجل التدقيق"
        title_text = "سجل التدقيق والرقابة والعمليات الإدارية الحساسة"
    else:
        abort(400)
        
    log_audit_action('report_exported', 'report', None, f"تصدير إكسيل لتقرير: {report_type}", current_user)
    return create_excel_response(sheet_title, title_text, headers, rows, ascii_filename, arabic_filename)
