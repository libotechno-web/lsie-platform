from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime

from app.extensions import db
from app.models import (
    InnovationProject, ProjectAttachment, Organization,
    CourseEnrollment, EventRegistration, OpportunityApplication,
    NetworkingRequest, Notification
)
from app.forms import ProjectSubmissionForm
from app.utils.helpers import save_uploaded_file, slugify_text, create_notification, log_audit_action

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.before_request
def require_approved_membership():
    """حظر وصول أي مستخدم للوحة التحكم أو نشر المشاريع حتى يتم اعتماده وتأكيده من قبل الأدمن"""
    if not current_user.is_authenticated:
        return None # يتولى @login_required التوجيه لصفحة الدخول
    if not current_user.is_approved_member and not current_user.is_admin:
        flash('عذراً، حسابك بانتظار المراجعة والاعتماد من قبل الأدمن الرئيسي. لا يمكنك الوصول للوحة التحكم أو نشر الطلبات والمشاريع قبل الاعتماد.', 'warning')
        return redirect(url_for('auth.pending_approval', email=current_user.email))


@dashboard_bp.route('/')
@login_required
def index():
    """لوحة تحكم المستخدم الرئيسية"""
    my_projects = InnovationProject.query.filter_by(user_id=current_user.id).order_by(InnovationProject.updated_at.desc()).limit(5).all()
    my_courses = CourseEnrollment.query.filter_by(user_id=current_user.id).order_by(CourseEnrollment.enrolled_at.desc()).limit(5).all()
    my_events = EventRegistration.query.filter_by(user_id=current_user.id).order_by(EventRegistration.registered_at.desc()).limit(5).all()
    my_applications = OpportunityApplication.query.filter_by(user_id=current_user.id).order_by(OpportunityApplication.submitted_at.desc()).limit(5).all()
    
    pending_networking = NetworkingRequest.query.filter_by(recipient_id=current_user.id, status='pending').count()
    
    return render_template(
        'dashboard/index.html',
        my_projects=my_projects,
        my_courses=my_courses,
        my_events=my_events,
        my_applications=my_applications,
        pending_networking=pending_networking
    )


@dashboard_bp.route('/submit-project', methods=['GET', 'POST'])
@login_required
def submit_project():
    """تقديم فكرة أو مشروع جديد لمنظومة الابتكار"""
    form = ProjectSubmissionForm()
    if form.validate_on_submit():
        base_slug = slugify_text(form.title.data)
        slug = f"{base_slug}-{datetime.utcnow().strftime('%y%m%d%H%M')}"
        
        cover_image_path = None
        if form.cover_image.data:
            try:
                cover_image_path = save_uploaded_file(form.cover_image.data, 'projects')
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('dashboard/submit_project.html', form=form)
                
        project = InnovationProject(
            user_id=current_user.id,
            title=form.title.data.strip(),
            slug=slug,
            tagline=form.tagline.data.strip() if form.tagline.data else None,
            summary=form.summary.data.strip(),
            problem_statement=form.problem_statement.data.strip(),
            proposed_solution=form.proposed_solution.data.strip(),
            target_market=form.target_market.data.strip() if form.target_market.data else None,
            sector=form.sector.data,
            city=form.city.data,
            stage=form.stage.data,
            business_model=form.business_model.data.strip() if form.business_model.data else None,
            needed_support=form.needed_support.data.strip() if form.needed_support.data else None,
            team_description=form.team_description.data.strip() if form.team_description.data else None,
            demo_url=form.demo_url.data.strip() if form.demo_url.data else None,
            video_url=form.video_url.data.strip() if form.video_url.data else None,
            cover_image=cover_image_path,
            status='submitted',
            is_public_in_directory=form.is_public_in_directory.data
        )
        db.session.add(project)
        db.session.flush()
        
        # حفظ ملف Pitch Deck إن وجد
        if form.pitch_deck.data:
            try:
                deck_path = save_uploaded_file(form.pitch_deck.data, 'pitch_decks')
                attachment = ProjectAttachment(
                    project_id=project.id,
                    file_name=form.pitch_deck.data.filename,
                    file_path=deck_path,
                    file_type='pitch_deck'
                )
                db.session.add(attachment)
            except ValueError as e:
                flash(f"تحذير: لم يتم حفظ الملف المرفق: {e}", 'warning')
                
        db.session.commit()
        
        log_audit_action('project_submitted', 'project', project.id, f"تقديم فكرة جديدة: {project.title}", current_user)
        create_notification(current_user.id, "تم استلام فكرتك بنجاح", f"مشروعك '{project.title}' قيد المراجعة والفرز من قبل اللجنة الفنية.", url_for('dashboard.project_detail', project_id=project.id))
        
        flash('تم إرسال فكرتك ومشروعك بنجاح! شكراً لمساهمتك في منظومة الابتكار الليبية.', 'success')
        return redirect(url_for('dashboard.projects'))
        
    return render_template('dashboard/submit_project.html', form=form)


@dashboard_bp.route('/projects')
@login_required
def projects():
    """قائمة مشاريعي وأفكاري المقدمة"""
    user_projects = InnovationProject.query.filter_by(user_id=current_user.id).order_by(InnovationProject.created_at.desc()).all()
    return render_template('dashboard/my_projects.html', projects=user_projects)


@dashboard_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    """عرض تفاصيل مشروعي ومتابعة حالة المراجعة والتقييم"""
    project = InnovationProject.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    return render_template('dashboard/project_detail.html', project=project)


@dashboard_bp.route('/courses')
@login_required
def my_courses():
    """الدورات التدريبية المسجل بها"""
    enrollments = CourseEnrollment.query.filter_by(user_id=current_user.id).order_by(CourseEnrollment.enrolled_at.desc()).all()
    return render_template('dashboard/my_courses.html', enrollments=enrollments)


@dashboard_bp.route('/events')
@login_required
def my_events():
    """الفعاليات المسجل بها"""
    registrations = EventRegistration.query.filter_by(user_id=current_user.id).order_by(EventRegistration.registered_at.desc()).all()
    return render_template('dashboard/my_events.html', registrations=registrations)


@dashboard_bp.route('/applications')
@login_required
def my_applications():
    """طلبات التقديم على المنح والفرص"""
    apps = OpportunityApplication.query.filter_by(user_id=current_user.id).order_by(OpportunityApplication.submitted_at.desc()).all()
    return render_template('dashboard/my_applications.html', applications=apps)


@dashboard_bp.route('/networking')
@login_required
def networking_requests():
    """طلبات التشبيك والتوجيه الواردة والصادرة"""
    received = NetworkingRequest.query.filter_by(recipient_id=current_user.id).order_by(NetworkingRequest.created_at.desc()).all()
    sent = NetworkingRequest.query.filter_by(sender_id=current_user.id).order_by(NetworkingRequest.created_at.desc()).all()
    return render_template('dashboard/networking.html', received=received, sent=sent)


@dashboard_bp.route('/networking/<int:req_id>/respond', methods=['POST'])
@login_required
def respond_networking(req_id):
    """الرد على طلب التشبيك (قبول / اعتذار)"""
    req = NetworkingRequest.query.filter_by(id=req_id, recipient_id=current_user.id).first_or_404()
    action = request.form.get('action') # accept or decline
    note = request.form.get('response_note', '').strip()
    
    if action == 'accept':
        req.status = 'accepted'
        flash('تم قبول طلب التشبيك بنجاح! تم مشاركة بيانات الاتصال مع الطرف الآخر.', 'success')
        create_notification(req.sender_id, "تم قبول طلب التشبيك!", f"وافق {current_user.full_name} على طلبك بخصوص '{req.subject}'.", url_for('dashboard.networking_requests'))
    elif action == 'decline':
        req.status = 'declined'
        flash('تم الاعتذار عن طلب التشبيك.', 'info')
        create_notification(req.sender_id, "اعتذار عن طلب التشبيك", f"اعتذر {current_user.full_name} عن قبول طلب '{req.subject}'.", url_for('dashboard.networking_requests'))
        
    req.response_note = note if note else None
    req.responded_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('dashboard.networking_requests'))


@dashboard_bp.route('/notifications')
@login_required
def notifications():
    """عرض الإشعارات وتحديدها كمقروءة"""
    user_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for n in user_notifs:
        n.is_read = True
    db.session.commit()
    return render_template('dashboard/notifications.html', notifications=user_notifs)
