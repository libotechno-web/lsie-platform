from datetime import datetime
from app.extensions import db


class NetworkingRequest(db.Model):
    """طلبات التشبيك: إرشاد وتوجيه، فرص استثمارية، شراكات أعمال، استشارات تقنية"""
    __tablename__ = 'networking_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # نوع الطلب: mentorship, investment, partnership, consultation
    request_type = db.Column(db.String(40), nullable=False, default='mentorship')
    
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # معلومات الاتصال المقترحة للمشاركة بعد الموافقة
    sender_contact_email = db.Column(db.String(120), nullable=True)
    sender_contact_phone = db.Column(db.String(30), nullable=True)
    
    # حالة الطلب: pending, accepted, declined, completed
    status = db.Column(db.String(30), default='pending', index=True)
    response_note = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)

    @property
    def type_label_ar(self):
        types = {
            'mentorship': 'طلب توجيه وإرشاد خبير',
            'investment': 'اهتمام واستفسار استثماري',
            'partnership': 'طلب شراكة وتكامل أعمال',
            'consultation': 'استشارة متخصصة'
        }
        return types.get(self.request_type, 'طلب تواصل')

    @property
    def status_label_ar(self):
        labels = {
            'pending': 'قيد الانتظار',
            'accepted': 'تم القبول والربط',
            'declined': 'معتذر عنه',
            'completed': 'مكتمل'
        }
        return labels.get(self.status, self.status)


class Notification(db.Model):
    """نظام التنبيهات الداخلية للمستخدمين"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), default='bi-bell')
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
