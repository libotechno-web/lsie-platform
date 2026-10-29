from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """التحقق من أن المستخدم يمتلك دوراً واحداً على الأقل من الأدوار المحددة (Server-Side RBAC)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # إذا كان المستخدم مسؤولاً عاماً (admin)، يُمنح حق الوصول دائماً
            if current_user.is_admin:
                return f(*args, **kwargs)
                
            user_roles = [r.name for r in current_user.roles]
            if not any(r in user_roles for r in roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """قصر الوصول على مدراء النظام فقط"""
    return role_required('admin')(f)


def reviewer_required(f):
    """صلاحية الوصول للمراجعين واللجان الفنية والمدراء"""
    return role_required('admin', 'reviewer')(f)


def editor_required(f):
    """صلاحية الوصول لمحرري المحتوى والمدراء"""
    return role_required('admin', 'editor')(f)
