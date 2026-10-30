from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, BooleanField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed


class ArticleForm(FlaskForm):
    title = StringField('عنوان المحتوى / الخبر', validators=[DataRequired(), Length(max=250)])
    category = SelectField('التصنيف', choices=[
        ('news', 'أخبار الجمعية'),
        ('article', 'مقال تحليلي ورأي'),
        ('success_story', 'قصة نجاح ريادية'),
        ('announcement', 'إعلان رسمي وتنويه'),
        ('report', 'تقرير وإحصاءات')
    ], default='news')
    summary = TextAreaField('ملخص موجز', validators=[DataRequired()])
    content_html = TextAreaField('المحتوى الكامل (يدعم التنسيق)', validators=[DataRequired()])
    featured_image = FileField('الصورة الرئيسية', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'صور فقط')])
    author_name = StringField('اسم الكاتب أو الجهة', validators=[Optional()])
    status = SelectField('حالة النشر', choices=[
        ('published', 'منشور للعامة'),
        ('draft', 'مسودة غير منشورة'),
        ('archived', 'مؤرشف')
    ], default='published')
    is_featured = BooleanField('تثبيت في واجهة الأخبار الرئيسية')
    submit = SubmitField('حفظ المحتوى')


class EventForm(FlaskForm):
    # البيانات الأساسية بالعربية
    title = StringField('عنوان الفعالية / المنشط (بالعربية)', validators=[DataRequired(), Length(max=250)])
    event_type = SelectField('نوع الفعالية / المنشط', choices=[
        ('conference', 'مؤتمر علمي / ريادي'),
        ('forum', 'منتدى حواري'),
        ('workshop', 'ورشة عمل تدريبية'),
        ('hackathon', 'هاكاثون ومنافسة برمجية'),
        ('demo_day', 'يوم العروض (Demo Day)'),
        ('networking', 'لقاء تشبيك وتواصل')
    ], default='conference')
    summary = TextAreaField('موجز الفعالية (بالعربية)', validators=[DataRequired()])
    description = TextAreaField('التفاصيل الكاملة وجدول الأعمال (بالعربية)', validators=[DataRequired()])
    cover_image = FileField('صورة الفعالية', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'صور فقط')])
    
    # خيار إضافة المنشط باللغة الإنجليزية (English Activity Information)
    title_en = StringField('عنوان المنشط بالإنجليزية (English Title)', validators=[Optional(), Length(max=250)])
    city_en = StringField('المدينة بالإنجليزية (English City)', validators=[Optional(), Length(max=60)])
    location_name_en = StringField('اسم المكان أو المنصة بالإنجليزية (English Venue)', validators=[Optional(), Length(max=255)])
    summary_en = TextAreaField('موجز المنشط بالإنجليزية (English Summary)', validators=[Optional()])
    description_en = TextAreaField('التفاصيل الكاملة بالإنجليزية (English Description)', validators=[Optional()])

    location_type = SelectField('طريقة الانعقاد', choices=[
        ('in_person', 'حضوري'),
        ('online', 'عبر الإنترنت (افتراضي)'),
        ('hybrid', 'مدمج (حضوري وافتراضي)')
    ], default='in_person')
    location_name = StringField('اسم المكان أو المنصة (بالعربية)', default='مقر الجمعية - جامعة غريان')
    city = StringField('المدينة (بالعربية)', default='غريان')
    online_link = StringField('رابط البث / اللقاء الافتراضي إن وجد', validators=[Optional()])
    
    start_time = DateTimeLocalField('موعد وتاريخ البداية', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField('موعد وتاريخ النهاية', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    capacity = IntegerField('الطاقة الاستيعابية للمقاعد', default=100)
    
    is_registration_open = BooleanField('التسجيل مفتوح للجمهور', default=True)
    is_featured = BooleanField('إبراز في الصفحة الرئيسية')
    is_published = BooleanField('منشور ومتاح للعامة', default=True)
    submit = SubmitField('حفظ الفعالية / المنشط')


class OpportunityForm(FlaskForm):
    title = StringField('عنوان الفرصة / المنحة', validators=[DataRequired(), Length(max=250)])
    opportunity_type = SelectField('نوع الفرصة', choices=[
        ('grant', 'منحة ابتكار وتمويل'),
        ('competition', 'مسابقة وجوائز تحفيزية'),
        ('incubation', 'برنامج احتضان مشاريع'),
        ('acceleration', 'برنامج تسريع نمو'),
        ('funding', 'فرصة استثمارية وتشبيك'),
        ('award', 'جائزة وطنية سنوية')
    ], default='grant')
    provider_name = StringField('الجهة المانحة أو المنظمة', default='الجمعية الليبية للابتكار وريادة الأعمال', validators=[DataRequired()])
    provider_logo = FileField('شعار الجهة المعلنة', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'صور فقط')])
    summary = TextAreaField('ملخص الفرصة', validators=[DataRequired()])
    description = TextAreaField('التفاصيل الكاملة والدعم المقدم', validators=[DataRequired()])
    eligibility_criteria = TextAreaField('شروط الأهلية والتقديم', validators=[Optional()])
    target_audience = StringField('الفئة المستهدفة', default='المبتكرون ورواد الأعمال والشركات الناشئة')
    award_or_funding = StringField('قيمة الدعم / الجائزة / المزايا', validators=[Optional()])
    
    sector = StringField('القطاع المستهدف', default='كافة القطاعات')
    city = StringField('النطاق الجغرافي', default='كل المدن الليبية')
    
    deadline = DateTimeLocalField('الموعد النهائي للتقديم', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    external_link = StringField('رابط التقديم الخارجي (إن كان التقديم خارجياً)', validators=[Optional()])
    allow_internal_apply = BooleanField('السماح بالتقديم المباشر عبر منصة الجمعية', default=True)
    
    status = SelectField('حالة الفرصة', choices=[
        ('open', 'مفتوحة للتقديم حالياً'),
        ('upcoming', 'تبدأ قريباً'),
        ('closed', 'مغلقة (انتهى التقديم)'),
        ('archived', 'مؤرشفة')
    ], default='open')
    is_featured = BooleanField('إبراز في الصفحة الرئيسية')
    submit = SubmitField('حفظ الفرصة')


class TrainingCourseForm(FlaskForm):
    title = StringField('عنوان البرنامج / الدورة', validators=[DataRequired(), Length(max=250)])
    trainer_name = StringField('اسم المدرب / الخبير', validators=[DataRequired()])
    trainer_title = StringField('المسمى المهني للمدرب', validators=[Optional()])
    trainer_avatar = FileField('صورة المدرب', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'صور فقط')])
    cover_image = FileField('صورة غلاف الدورة', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'صور فقط')])
    
    course_type = SelectField('نوع التدريب', choices=[
        ('course', 'دورة تدريبية متخصصة'),
        ('workshop', 'ورشة عمل تطبيقية'),
        ('bootcamp', 'مخيم تدريبي مكثف'),
        ('webinar', 'ندوة معرفية افتراضية')
    ], default='course')
    delivery_mode = SelectField('نمط الحضور', choices=[
        ('online', 'عن بُعد (Online)'),
        ('in_person', 'حضوري'),
        ('hybrid', 'مدمج')
    ], default='online')
    location_or_link = StringField('القاعة أو رابط المنصة التعليمية', validators=[Optional()])
    
    summary = TextAreaField('موجز البرنامج التدريبي', validators=[DataRequired()])
    description = TextAreaField('المنهج والمحاور التفصيلية', validators=[DataRequired()])
    learning_objectives = TextAreaField('المخرجات المتوقعة من التدريب', validators=[Optional()])
    prerequisites = TextAreaField('المتطلبات المسبقة للملتحقين', validators=[Optional()])
    
    start_date = DateTimeLocalField('تاريخ البدء', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('تاريخ الانتهاء', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    duration_hours = IntegerField('عدد الساعات التدريبية', default=12)
    max_seats = IntegerField('الحد الأقصى للمتدربين', default=25)
    
    certificate_included = BooleanField('شهادة حضور معتمدة من الجمعية', default=True)
    is_free = BooleanField('برنامج تدريبي مجاني بالكامل', default=True)
    
    registration_status = SelectField('حالة التسجيل', choices=[
        ('open', 'التسجيل متاح'),
        ('closing_soon', 'يغلق قريباً'),
        ('closed', 'اكتمل العدد / مغلق'),
        ('completed', 'مكتمل ومنتهي')
    ], default='open')
    is_featured = BooleanField('إبراز في الصفحة الرئيسية')
    submit = SubmitField('حفظ البرنامج التدريبي')


class PartnerForm(FlaskForm):
    name = StringField('اسم الجهة الشريكة', validators=[DataRequired()])
    partner_type = SelectField('نوع الشراكة', choices=[
        ('governmental', 'جهة حكومية / هيئة رسمية'),
        ('academic', 'جامعة أو مركز بحث علمي'),
        ('incubator', 'حاضنة / مسرعة أعمال'),
        ('private_sector', 'قطاع خاص وشركات رائدة'),
        ('international', 'منظمة دولية / جهة مانحة')
    ], default='academic')
    website_url = StringField('رابط موقع الشريك', validators=[Optional()])
    description = TextAreaField('نبذة موجزة عن التعاون', validators=[Optional()])
    logo = FileField('شعار الشريك', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp', 'svg'], 'صور فقط')])
    order_index = IntegerField('الترتيب', default=0)
    is_active = BooleanField('مفعّل ويظهر في الموقع', default=True)
    submit = SubmitField('حفظ الشريك')


class PageForm(FlaskForm):
    title = StringField('عنوان الصفحة', validators=[DataRequired(), Length(max=200)])
    slug = StringField('المعرف اللطيف (Slug)', validators=[DataRequired(), Length(max=200)])
    summary = TextAreaField('وصف تعريفي مختصر', validators=[Optional()])
    content_html = TextAreaField('محتوى الصفحة الكامل (HTML)', validators=[DataRequired()])
    is_published = BooleanField('منشورة', default=True)
    show_in_footer = BooleanField('إظهار رابطها في التذييل', default=True)
    order_index = IntegerField('الترتيب', default=0)
    submit = SubmitField('حفظ الصفحة')
