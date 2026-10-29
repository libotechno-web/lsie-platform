from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app.extensions import db
from app.models import InnovationProject, User, Organization

api_bp = Blueprint('api', __name__)


@api_bp.route('/stats/overview')
def stats_overview():
    """بيانات إحصائية حية لرسوم لوحة التحكم البيانية"""
    # توزيع المشاريع حسب القطاع
    sectors = db.session.query(
        InnovationProject.sector, func.count(InnovationProject.id)
    ).group_by(InnovationProject.sector).all()
    
    # توزيع المشاريع حسب الحالة
    statuses = db.session.query(
        InnovationProject.status, func.count(InnovationProject.id)
    ).group_by(InnovationProject.status).all()
    
    # توزيع المستخدمين حسب المدينة
    cities = db.session.query(
        User.city, func.count(User.id)
    ).group_by(User.city).limit(10).all()
    
    return jsonify({
        'sectors': [{'sector': s[0], 'count': s[1]} for s in sectors],
        'statuses': [{'status': st[0], 'count': st[1]} for st in statuses],
        'cities': [{'city': c[0] or 'غير محدد', 'count': c[1]} for c in cities]
    })
