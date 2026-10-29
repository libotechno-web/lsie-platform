from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed


class ProjectSubmissionForm(FlaskForm):
    title = StringField('عنوان الفكرة أو المشروع', validators=[DataRequired(message='يرجى إدخال عنوان المشروع'), Length(max=200)])
    tagline = StringField('موجز المشروع بسطر واحد (Tagline)', validators=[Optional(), Length(max=255)])
    
    sector = SelectField('قطاع المشروع', choices=[
        ('تقنية المعلومات والذكاء الاصطناعي', 'تقنية المعلومات والذكاء الاصطناعي'),
        ('التقنيات المالية (FinTech)', 'التقنيات المالية (FinTech)'),
        ('التقنيات الصحية والطبية', 'التقنيات الصحية والطبية'),
        ('الزراعة والأمن الغذائي', 'الزراعة والأمن الغذائي'),
        ('الطاقة المتجددة والاستدامة', 'الطاقة المتجددة والاستدامة'),
        ('التعليم وتكنولوجيا المعرفة (EdTech)', 'التعليم وتكنولوجيا المعرفة (EdTech)'),
        ('التجارة الإلكترونية والخدمات اللوجستية', 'التجارة الإلكترونية والخدمات اللوجستية'),
        ('الصناعة والتصنيع المحلي', 'الصناعة والتصنيع المحلي'),
        ('السياحة والتراث الثقافي', 'السياحة والتراث الثقافي'),
        ('قطاع آخر', 'قطاع آخر')
    ], default='تقنية المعلومات والذكاء الاصطناعي')
    
    city = SelectField('المدينة / النطاق الجغرافي', choices=[
        ('غريان', 'غريان'),
        ('طرابلس', 'طرابلس'),
        ('بنغازي', 'بنغازي'),
        ('مصراتة', 'مصراتة'),
        ('الزاوية', 'الزاوية'),
        ('سبها', 'سبها'),
        ('طبرق', 'طبرق'),
        ('زليتن', 'زليتن'),
        ('الخمس', 'الخمس'),
        ('سرت', 'سرت'),
        ('درنة', 'درنة'),
        ('البيضاء', 'البيضاء'),
        ('يفرن', 'يفرن'),
        ('نالوت', 'نالوت'),
        ('أخرى', 'مدينة أخرى')
    ], default='غريان')
    
    stage = SelectField('مرحلة نضج المشروع', choices=[
        ('idea', 'فكرة نظرية تحت التطوير'),
        ('prototype', 'نموذج أولي تجريبي (Prototype)'),
        ('mvp', 'منتج قابل للإطلاق الأولي (MVP)'),
        ('operational', 'مشروع قائم في السوق'),
        ('scaling', 'مرحلة التوسع والنمو السريع')
    ], default='idea')
    
    summary = TextAreaField('الوصف العام للمشروع', validators=[DataRequired(message='يرجى كتابة وصف وافٍ للمشروع')])
    problem_statement = TextAreaField('المشكلة الواقعية التي يعالجها المشروع', validators=[DataRequired(message='وضح المشكلة التي يحلها المشروع')])
    proposed_solution = TextAreaField('الحل الابتكاري المقترح والقيمة المضافة', validators=[DataRequired(message='وضح الحل والابتكار')])
    target_market = StringField('الفئة المستهدفة وحجم السوق المتوقع', validators=[Optional()])
    business_model = TextAreaField('نموذج العمل ومصادر الإيرادات المتوقعة', validators=[Optional()])
    
    needed_support = StringField('نوع الدعم المطلوب (تمويل، احتضان، توجيه، شركاء تقنيين)', validators=[Optional()])
    team_description = TextAreaField('فريق العمل والخبرات والمهارات المتوفرة', validators=[Optional()])
    
    demo_url = StringField('رابط النموذج التجريبي أو الموقع إن وجد', validators=[Optional()])
    video_url = StringField('رابط فيديو توضيحي للفكرة (YouTube/Drive)', validators=[Optional()])
    
    cover_image = FileField('صورة معبرة عن المشروع', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'يُسمح بالصور فقط')])
    pitch_deck = FileField('العرض التقديمي للمشروع (Pitch Deck / ملف PDF)', validators=[Optional(), FileAllowed(['pdf', 'pptx', 'ppt', 'docx', 'zip'], 'ملفات PDF أو Presentation أو مستندات فقط')])
    
    is_public_in_directory = BooleanField('أوافق على ظهور فكرتي/مشروعي في دليل الابتكار بعد اعتماده')
    terms = BooleanField('أتعهد بأن الفكرة أصيلة ومملوكة لي وللفريق وأوافق على سياسة التقييم بالجمعية', validators=[DataRequired(message='يجب الموافقة على التعهد للمتابعة')])
    
    submit = SubmitField('إرسال الفكرة والمشروع للاعتماد')


class ProjectReviewForm(FlaskForm):
    score_innovation = IntegerField('درجة الأصالة والابتكار (من 25)', validators=[DataRequired(), NumberRange(min=0, max=25)])
    score_feasibility = IntegerField('درجة قابلية التنفيذ والواقعية (من 25)', validators=[DataRequired(), NumberRange(min=0, max=25)])
    score_market_impact = IntegerField('درجة حجم السوق والأثر الاقتصادي (من 25)', validators=[DataRequired(), NumberRange(min=0, max=25)])
    score_team = IntegerField('درجة قدرات الفريق وجديته (من 25)', validators=[DataRequired(), NumberRange(min=0, max=25)])
    
    recommendation = SelectField('توصية المقيم', choices=[
        ('accept', 'قبول واعتماد المشروع'),
        ('need_info', 'طلب استكمال بيانات ونواقص من صاحب الفكرة'),
        ('defer', 'تأجيل لدورة التقييم القادمة'),
        ('reject', 'اعتذار عن قبول الفكرة')
    ], default='accept')
    
    status = SelectField('تحديث الحالة العامة للمشروع', choices=[
        ('under_review', 'قيد المراجعة'),
        ('under_evaluation', 'قيد التقييم'),
        ('needs_info', 'مطلوب استكمال بيانات'),
        ('accepted', 'مقبول ومعتمد'),
        ('rejected', 'غير مقبول'),
        ('deferred', 'مؤجل'),
        ('closed', 'مغلق')
    ], default='accepted')
    
    internal_notes = TextAreaField('ملاحظات سرية للإدارة ولجنة التقييم (لا تظهر للمستخدم)', validators=[Optional()])
    applicant_feedback = TextAreaField('ملاحظات وتوجيهات لمقدم المشروع (تظهر له في حسابه)', validators=[Optional()])
    
    submit = SubmitField('حفظ التقييم واعتماد القرار')
