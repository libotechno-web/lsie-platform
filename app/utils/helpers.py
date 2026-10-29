import os
import re
import uuid
from datetime import datetime
from flask import current_app, request
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.settings import AuditLog
from app.models.networking import Notification


def slugify_text(text):
    """توليد slug نظيف وآمن يدعم الحروف العربية والإنجليزية"""
    if not text:
        return str(uuid.uuid4())[:8]
    # إزالة التشكيل
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # استبدال المسافات والرموز بشرطة
    text = re.sub(r'[\s_]+', '-', text.strip())
    # الإبقاء فقط على الأحرف العربية والإنجليزية والأرقام والشرطة
    text = re.sub(r'[^\w\-\u0600-\u06FF]', '', text)
    # تنظيف تكرار الشرطات
    text = re.sub(r'-+', '-', text).strip('-')
    if not text:
        text = f"item-{str(uuid.uuid4())[:8]}"
    return text


def save_uploaded_file(file_storage, subfolder='general'):
    """حفظ الملفات المرفوعة بأمان والتحقق من الامتداد"""
    if not file_storage or file_storage.filename == '':
        return None
    
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        raise ValueError(f"امتداد الملف غير مسموح به ({ext}). الامتدادات المقبولة: {', '.join(current_app.config['ALLOWED_EXTENSIONS'])}")
    
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(target_dir, unique_name)
    file_storage.save(file_path)
    
    # إرجاع المسار النسبي لاستخدامه في الروابط
    return f"uploads/{subfolder}/{unique_name}"


def log_audit_action(action, resource_type=None, resource_id=None, details=None, user=None):
    """تسجيل العمليات الإدارية الحساسة في سجل التدقيق"""
    try:
        user_id = user.id if user and user.is_authenticated else None
        user_email = user.email if user and user.is_authenticated else 'مجهول'
        ip_addr = request.remote_addr if request else '127.0.0.1'
        
        log_entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details,
            ip_address=ip_addr
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Audit log failure: {e}")


def create_notification(user_id, title, message, link=None, icon='bi-bell'):
    """إرسال إشعار داخلي للمستخدم"""
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            link=link,
            icon=icon
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Notification creation error: {e}")
