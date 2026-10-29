from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Role, UserProfile
from app.forms import LoginForm, RegisterForm, ProfileForm
from app.utils.helpers import save_uploaded_file, log_audit_action

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول للمنصة"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('هذا الحساب موقوف حالياً. يرجى التواصل مع إدارة الجمعية.', 'danger')
                return render_template('auth/login.html', form=form)
                
            login_user(user, remember=form.remember_me.data)
            log_audit_action('user_login', 'user', user.id, f"تسجيل دخول المستخدم {user.email}", user)
            
            flash(f'مرحباً بك مجدداً، {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/'):
                next_page = None
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'danger')
            
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """إنشاء حساب جديد بالمنصة"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.strip().lower(),
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip(),
            city=form.city.data,
            account_type=form.account_type.data,
            is_active=True,
            is_verified=False
        )
        user.set_password(form.password.data)
        
        # إسناد الدور المناسب للمستخدم
        role = Role.query.filter_by(name=form.account_type.data).first()
        if not role:
            role = Role.query.filter_by(name='member').first()
        if role:
            user.roles.append(role)
            
        db.session.add(user)
        db.session.flush() # للحصول على user.id
        
        # إنشاء ملف تعريفي مرتبط
        profile = UserProfile(
            user_id=user.id,
            is_public_in_directory=True
        )
        db.session.add(profile)
        db.session.commit()
        
        login_user(user)
        log_audit_action('user_registered', 'user', user.id, f"تسجيل حساب جديد: {user.email} بدور {user.account_type}", user)
        flash('تم إنشاء حسابك بنجاح! أهلاً بك في المنصة الوطنية للابتكار وريادة الأعمال.', 'success')
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    log_audit_action('user_logout', 'user', current_user.id, f"تسجيل خروج: {current_user.email}", current_user)
    logout_user()
    flash('تم تسجيل خروجك بنجاح.', 'info')
    return redirect(url_for('public.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """إدارة وتعديل الملف الشخصي"""
    form = ProfileForm(obj=current_user)
    profile_record = current_user.profile or UserProfile(user_id=current_user.id)
    
    if request.method == 'GET':
        form.skills.data = profile_record.skills
        form.interests.data = profile_record.interests
        form.experience_years.data = profile_record.experience_years
        form.education_level.data = profile_record.education_level
        form.specialization.data = profile_record.specialization
        form.linkedin_url.data = profile_record.linkedin_url
        form.github_url.data = profile_record.github_url
        form.website_url.data = profile_record.website_url
        form.available_for_mentoring.data = profile_record.available_for_mentoring
        form.is_public_in_directory.data = profile_record.is_public_in_directory
        
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        current_user.city = form.city.data.strip() if form.city.data else None
        current_user.headline = form.headline.data.strip() if form.headline.data else None
        current_user.bio = form.bio.data.strip() if form.bio.data else None
        
        if form.avatar.data:
            try:
                avatar_path = save_uploaded_file(form.avatar.data, 'avatars')
                current_user.avatar = avatar_path
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('auth/profile.html', form=form)
                
        # تحديث بيانات الملف
        profile_record.skills = form.skills.data.strip() if form.skills.data else None
        profile_record.interests = form.interests.data.strip() if form.interests.data else None
        profile_record.experience_years = form.experience_years.data
        profile_record.education_level = form.education_level.data.strip() if form.education_level.data else None
        profile_record.specialization = form.specialization.data.strip() if form.specialization.data else None
        profile_record.linkedin_url = form.linkedin_url.data.strip() if form.linkedin_url.data else None
        profile_record.github_url = form.github_url.data.strip() if form.github_url.data else None
        profile_record.website_url = form.website_url.data.strip() if form.website_url.data else None
        profile_record.available_for_mentoring = form.available_for_mentoring.data
        profile_record.is_public_in_directory = form.is_public_in_directory.data
        
        db.session.add(profile_record)
        db.session.commit()
        
        flash('تم حفظ بيانات ملفك الشخصي بنجاح!', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', form=form)
