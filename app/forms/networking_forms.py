from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional
from flask_wtf.file import FileField, FileAllowed


class NetworkingRequestForm(FlaskForm):
    request_type = SelectField('نوع الطلب', choices=[
        ('mentorship', 'طلب توجيه وإرشاد من خبير'),
        ('investment', 'استفسار واهتمام استثماري'),
        ('partnership', 'طلب شراكة وتكامل تجاري/تقني'),
        ('consultation', 'استشارة فنية متخصصة')
    ], default='mentorship')
    subject = StringField('موضوع الطلب', validators=[DataRequired(message='يرجى إدخال الموضوع')])
    message = TextAreaField('تفاصيل الطلب والغرض منه', validators=[DataRequired(message='يرجى كتابة رسالتك بوضوح')])
    sender_contact_email = StringField('البريد الإلكتروني للتواصل عند القبول', validators=[DataRequired(), Email()])
    sender_contact_phone = StringField('رقم الهاتف للتواصل المباشر', validators=[Optional()])
    submit = SubmitField('إرسال طلب التشبيك')


class EventRegistrationForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    phone = StringField('رقم الهاتف', validators=[DataRequired()])
    organization = StringField('الجهة أو الجامعة أو التخصص', validators=[Optional()])
    notes = TextAreaField('ملاحظات إضافية', validators=[Optional()])
    submit = SubmitField('تأكيد التسجيل في الفعالية')


class CourseEnrollmentForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    phone = StringField('رقم الهاتف', validators=[DataRequired()])
    motivation = TextAreaField('ما هو دافعك للالتحاق بهذا البرنامج التدريبي وماذا تأمل أن تتعلم؟', validators=[DataRequired()])
    submit = SubmitField('تقديم طلب الالتحاق بالدورة')


class OpportunityApplicationForm(FlaskForm):
    applicant_name = StringField('اسم مقدم الطلب / قائد الفريق', validators=[DataRequired()])
    applicant_email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    applicant_phone = StringField('رقم الهاتف', validators=[DataRequired()])
    proposal_summary = TextAreaField('موجز المقترح والدافع للمشاركة في هذه الفرصة', validators=[DataRequired()])
    attachment = FileField('المستندات أو الملفات الداعمة (PDF/ZIP)', validators=[Optional(), FileAllowed(['pdf', 'zip', 'docx', 'pptx'], 'ملفات PDF أو مستندات فقط')])
    submit = SubmitField('إرسال طلب التقديم للفرصة')
