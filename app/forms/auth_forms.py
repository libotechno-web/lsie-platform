from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from flask_wtf.file import FileField, FileAllowed
from app.models.user import User


class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(message='يرجى إدخال البريد الإلكتروني'), Email(message='صيغة البريد الإلكتروني غير صحيحة')])
    password = PasswordField('كلمة المرور', validators=[DataRequired(message='يرجى إدخال كلمة المرور')])
    remember_me = BooleanField('تذكرني في هذه الجلسة')
    submit = SubmitField('تسجيل الدخول')


class RegisterForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(message='يرجى إدخال الاسم الكامل'), Length(min=3, max=150, message='يجب أن يكون الاسم بين 3 و 150 حرفاً')])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(message='يرجى إدخال البريد الإلكتروني'), Email(message='صيغة البريد الإلكتروني غير صحيحة')])
    phone = StringField('رقم الهاتف', validators=[DataRequired(message='يرجى إدخال رقم الهاتف')])
    city = SelectField('المدينة', choices=[
        ('غريان', 'غريان (المقر الرئيسي)'),
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
        ('جادو', 'جادو'),
        ('أخرى', 'مدينة أخرى')
    ], default='غريان')
    account_type = SelectField('نوع الحساب والمسار', choices=[
        ('member', 'عضو في الجمعية'),
        ('innovator', 'مبتكر / صاحب فكرة إبداعية'),
        ('startup', 'رائد أعمال / شركة ناشئة'),
        ('investor', 'مستثمر / جهة تمويل'),
        ('expert', 'خبير / موجه / مدرب'),
        ('partner_org', 'جامعة / حاضنة / مؤسسة داعمة')
    ], default='innovator')
    password = PasswordField('كلمة المرور', validators=[DataRequired(message='يرجى إدخال كلمة المرور'), Length(min=8, message='يجب ألا تقل كلمة المرور عن 8 أحرف')])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(message='يرجى تأكيد كلمة المرور'), EqualTo('password', message='كلمتا المرور غير متطابقتين')])
    terms = BooleanField('أوافق على الشروط والأحكام وسياسة الخصوصية الخاصة بالجمعية', validators=[DataRequired(message='يجب الموافقة على الشروط للمتابعة')])
    submit = SubmitField('إنشاء الحساب')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError('البريد الإلكتروني مسجل بالفعل. يرجى استخدام بريد آخر أو تسجيل الدخول.')


class ProfileForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired()])
    phone = StringField('رقم الهاتف', validators=[Optional()])
    city = StringField('المدينة', validators=[Optional()])
    headline = StringField('العنوان المهني / المسمى', validators=[Optional(), Length(max=200)])
    bio = TextAreaField('نبذة تعريفية شخصية', validators=[Optional()])
    avatar = FileField('تحديث الصورة الشخصية', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'يُسمح بالصور فقط')])
    
    # بيانات الملف الإضافية
    skills = StringField('المهارات والخبرات (مفصولة بفواصل)', validators=[Optional()])
    interests = StringField('مجالات الاهتمام والابتكار', validators=[Optional()])
    experience_years = IntegerField('سنوات الخبرة', validators=[Optional()])
    education_level = StringField('المؤهل العلمي', validators=[Optional()])
    specialization = StringField('التخصص الدقيق', validators=[Optional()])
    linkedin_url = StringField('رابط LinkedIn', validators=[Optional()])
    github_url = StringField('رابط GitHub', validators=[Optional()])
    website_url = StringField('الموقع الشخصي أو الرابط المهني', validators=[Optional()])
    
    available_for_mentoring = BooleanField('مستعد لتقديم التوجيه والإرشاد للمبتكرين')
    is_public_in_directory = BooleanField('إظهار بياناتي في دليل الابتكار الليبي العام')
    
    submit = SubmitField('حفظ التعديلات')
