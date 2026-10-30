from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed


class SiteSettingsForm(FlaskForm):
    # عام
    site_name = StringField('اسم المنصة / الجمعية بالعربية', validators=[DataRequired()])
    site_name_en = StringField('اسم الجمعية بالإنجليزية', validators=[DataRequired()])
    site_acronym = StringField('المختصر الرسمي', default='L.S.I.E')
    hero_title = StringField('عنوان الهيرو الرئيسي بالصفحة الرئيسية', default='من الفكرة إلى مشروع يصنع المستقبل')
    hero_subtitle = TextAreaField('النص التعريفي في الهيرو')
    
    # النبذة والرؤية والرسالة
    about_intro = TextAreaField('المقدمة الرسمية للجمعية', validators=[DataRequired()])
    official_mission = TextAreaField('الرسالة الرسمية للجمعية', validators=[DataRequired()])
    official_vision = TextAreaField('الرؤية الرسمية للجمعية')
    establishment_decree = StringField('بيانات قرار التأسيس والإشهار')
    headquarters = StringField('المقر الرئيسي الرسمي', default='غريان - جامعة غريان')
    certificate_number = StringField('رقم شهادة النشاط', default='LARS-SCS-2026-042')
    
    # الهوية والألوان
    logo = FileField('تغيير شعار الجمعية', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp', 'svg'], 'صور فقط')])
    primary_color = StringField('اللون الأساسي (Primary Color Hex)', default='#0d6e3f')
    secondary_color = StringField('اللون الثانوي (Secondary Color Hex)', default='#133b66')
    accent_color = StringField('لون التمييز (Accent Color Hex)', default='#e5a93c')
    
    # التواصل والعناوين
    contact_email = StringField('البريد الإلكتروني الرسمي للتواصل', validators=[Optional()])
    contact_phone = StringField('هاتف الجمعية الرسمي', validators=[Optional()])
    contact_address = StringField('العنوان التفصيلي', default='كلية الهندسة - جامعة غريان، غريان، ليبيا')
    
    # منصات التواصل الاجتماعي (Facebook, Instagram, X)
    facebook_url = StringField('رابط صفحة Facebook الرسمية', validators=[Optional()])
    instagram_url = StringField('رابط حساب Instagram الرسمي', validators=[Optional()])
    twitter_x_url = StringField('رابط حساب X (تويتر) الرسمي', validators=[Optional()])
    linkedin_url = StringField('رابط صفحة LinkedIn', validators=[Optional()])
    youtube_url = StringField('رابط قناة YouTube', validators=[Optional()])
    
    submit = SubmitField('حفظ الإعدادات الشاملة')


class StrategicObjectiveForm(FlaskForm):
    title = StringField('الهدف الاستراتيجي', validators=[DataRequired()])
    description = TextAreaField('شرح وتفاصيل الهدف', validators=[DataRequired()])
    icon = StringField('فئة أيقونة Bootstrap (مثال: bi-bullseye)', default='bi-bullseye')
    order_index = IntegerField('الترتيب', default=0)
    is_active = BooleanField('مفعّل', default=True)
    submit = SubmitField('حفظ الهدف')


class OrganizationalValueForm(FlaskForm):
    title = StringField('القيمة المؤسسية', validators=[DataRequired()])
    description = TextAreaField('تفاصيل القيمة', validators=[DataRequired()])
    icon = StringField('فئة أيقونة Bootstrap (مثال: bi-shield-check)', default='bi-shield-check')
    order_index = IntegerField('الترتيب', default=0)
    is_active = BooleanField('مفعّل', default=True)
    submit = SubmitField('حفظ القيمة')


class NavigationItemForm(FlaskForm):
    title_ar = StringField('عنوان الرابط بالعربية', validators=[DataRequired()])
    title_en = StringField('العنوان بالإنجليزية', validators=[Optional()])
    url = StringField('المسار أو الرابط (مثال: /services أو /about)', validators=[DataRequired()])
    icon = StringField('أيقونة الرابط إن وجدت', validators=[Optional()])
    order_index = IntegerField('ترتيب الظهور', default=0)
    is_active = BooleanField('مفعّل ويظهر في القائمة', default=True)
    is_external = BooleanField('فتح في تبويب جديد (رابط خارجي)')
    location = SelectField('موضع القائمة', choices=[
        ('header', 'القائمة العلوية (Header)'),
        ('footer', 'التذييل (Footer)'),
        ('both', 'في الاثنين معاً')
    ], default='header')
    submit = SubmitField('حفظ عنصر القائمة')


class UserManagementForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired()])
    phone = StringField('رقم الهاتف', validators=[Optional()])
    city = StringField('المدينة', validators=[Optional()])
    current_job = StringField('الوظيفة الحالية / المسمى المهني', validators=[Optional(), Length(max=150)])
    previous_activities = TextAreaField('أعمال ونشاطات سابقة في الابتكار وريادة الأعمال', validators=[Optional()])
    account_type = SelectField('نوع الحساب', choices=[
        ('member', 'عضو'),
        ('innovator', 'مبتكر'),
        ('startup', 'شركة ناشئة'),
        ('investor', 'مستثمر'),
        ('expert', 'خبير وموجه'),
        ('partner_org', 'جهة داعمة وجامعة')
    ])
    is_active = BooleanField('الحساب نشط')
    is_verified = BooleanField('حساب موثق رسمياً')
    is_approved_member = BooleanField('عضوية معتمدة بالجمعية')
    send_confirmation_email = BooleanField('إرسال بريد إلكتروني للمستخدم بتأكيد التسجيل والاعتماد', default=True)
    roles = SelectMultipleField('الأدوار والصلاحيات الممنوحة للمستخدم', coerce=int)
    submit = SubmitField('تحديث بيانات المستخدم')
