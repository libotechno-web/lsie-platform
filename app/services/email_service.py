import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from flask import current_app, url_for


def get_mail_config():
    """الحصول على إعدادات خادم البريد من قاعدة البيانات (SiteSetting) أو ملف البيئة (.env)"""
    db_server = db_port = db_tls = db_ssl = db_user = db_password = db_sender = contact_email = None
    try:
        from app.models.settings import SiteSetting
        db_server = SiteSetting.get_value('mail_server')
        db_port = SiteSetting.get_value('mail_port')
        db_tls = SiteSetting.get_value('mail_use_tls')
        db_ssl = SiteSetting.get_value('mail_use_ssl')
        db_user = SiteSetting.get_value('mail_username')
        db_password = SiteSetting.get_value('mail_password')
        db_sender = SiteSetting.get_value('mail_default_sender')
        contact_email = SiteSetting.get_value('contact_email')
    except Exception:
        pass

    server = db_server or os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    port = int(db_port or os.environ.get('MAIL_PORT', 587))
    use_tls_val = db_tls if db_tls is not None else os.environ.get('MAIL_USE_TLS', 'true')
    use_tls = str(use_tls_val).lower() in ('true', '1', 'yes')
    use_ssl_val = db_ssl if db_ssl is not None else os.environ.get('MAIL_USE_SSL', 'false')
    use_ssl = str(use_ssl_val).lower() in ('true', '1', 'yes')
    username = db_user or os.environ.get('MAIL_USERNAME') or 'libotechno@gmail.com'
    password = db_password or os.environ.get('MAIL_PASSWORD', '')
    default_sender = db_sender or os.environ.get('MAIL_DEFAULT_SENDER') or contact_email or 'libotechno@gmail.com'

    return {
        'server': server,
        'port': port,
        'use_tls': use_tls,
        'use_ssl': use_ssl,
        'username': username,
        'password': password,
        'default_sender': default_sender
    }


def send_email(to_email, subject, html_content, text_content=None):
    """
    إرسال رسالة بريد إلكتروني مع دعم RTL والقوالب الجميلة.
    في بيئة الاختبار، يتم توثيق الرسالة ومحاكاتها بنجاح دون الحاجة لشبكة خارجية.
    """
    try:
        from app.models.settings import SiteSetting
        site_name = SiteSetting.get_value('site_name', 'الجمعية الليبية للابتكار وريادة الأعمال')
    except Exception:
        site_name = 'الجمعية الليبية للابتكار وريادة الأعمال'

    cfg = get_mail_config()
    sender_email = cfg['default_sender'] or 'libotechno@gmail.com'
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = f"{Header(site_name, 'utf-8').encode()} <{sender_email}>"
    msg['To'] = to_email

    if text_content:
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
    if html_content:
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    # التحقق من نمط الاختبار (unit tests)
    if current_app.config.get('TESTING'):
        current_app.logger.info(f"[EmailService] المحاكاة (بيئة الاختبار): تم إرسال بريد إلى '{to_email}' بعنوان: '{subject}'.")
        return True, "تم تسجيل وإرسال البريد بنجاح (نمط بيئة الاختبار)."

    # التحقق من وجود كلمة مرور التطبيقات
    if not cfg['password']:
        err_msg = f"لم يتم تعيين كلمة مرور التطبيقات (App Password) لحساب {cfg['username']}. يرجى إدخالها في إعدادات المنصة (/admin/settings) أو ملف .env لتفعيل الإرسال الفعلي."
        current_app.logger.warning(f"[EmailService] {err_msg}")
        return False, err_msg

    try:
        if cfg['use_ssl']:
            server = smtplib.SMTP_SSL(cfg['server'], cfg['port'], timeout=12)
        else:
            server = smtplib.SMTP(cfg['server'], cfg['port'], timeout=12)
            if cfg['use_tls']:
                server.starttls()

        if cfg['username'] and cfg['password']:
            server.login(cfg['username'], cfg['password'])

        server.send_message(msg)
        server.quit()
        current_app.logger.info(f"[EmailService] تم إرسال البريد بنجاح إلى '{to_email}'.")
        return True, "تم إرسال البريد الإلكتروني بنجاح."
    except smtplib.SMTPAuthenticationError as e:
        err_msg = "فشلت مصادقة بريد Gmail. يرجى التأكد من استخدام 'كلمة مرور التطبيقات' (App Password المكونة من 16 حرفاً) وليس كلمة المرور العادية لحساب libotechno@gmail.com."
        current_app.logger.error(f"[EmailService] {err_msg} ({e})")
        return False, err_msg
    except Exception as e:
        err_msg = f"تعذر إرسال البريد عبر خادم SMTP: {str(e)}"
        current_app.logger.error(f"[EmailService] {err_msg}")
        return False, err_msg


def send_registration_confirmation_email(user):
    """
    إرسال رسالة تأكيد رسمية للمستخدم فور اعتماد وتسجيل انضمامه لمجتمع الابتكار
    """
    try:
        from app.models.settings import SiteSetting
        site_name = SiteSetting.get_value('site_name', 'الجمعية الليبية للابتكار وريادة الأعمال')
        contact_email = SiteSetting.get_value('contact_email', 'libotechno@gmail.com')
        contact_phone = SiteSetting.get_value('contact_phone', '+218 21 000 0000')
    except Exception:
        site_name = 'الجمعية الليبية للابتكار وريادة الأعمال'
        contact_email = 'libotechno@gmail.com'
        contact_phone = '+218 21 000 0000'

    try:
        login_url = url_for('auth.login', _external=True)
    except Exception:
        login_url = "https://lsie.ly/auth/login"

    subject = f"تأكيد واعتماد انضمامك إلى مجتمع الابتكار الليبي - {site_name}"
    
    current_job = user.current_job or 'عضو في مجتمع الابتكار'
    account_type_arabic = {
        'member': 'عضو في الجمعية',
        'innovator': 'مبتكر / صاحب فكرة إبداعية',
        'startup': 'رائد أعمال / شركة ناشئة',
        'investor': 'مستثمر / جهة تمويل',
        'expert': 'خبير / موجه / مدرب',
        'partner_org': 'جامعة / حاضنة / مؤسسة داعمة'
    }.get(user.account_type, user.account_type)

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 0; padding: 25px 0; direction: rtl; text-align: right; color: #333333;">
        <div style="max-width: 620px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e1e7ec;">
            
            <!-- رأس الرسالة -->
            <div style="background: linear-gradient(135deg, #0d6e3f 0%, #133b66 100%); padding: 35px 25px; text-align: center; color: #ffffff;">
                <h1 style="margin: 0 0 10px 0; font-size: 24px; font-weight: bold; color: #ffffff;">{site_name}</h1>
                <p style="margin: 0; font-size: 15px; color: #f1c40f; font-weight: 500;">المنصة الوطنية لتمكين المبتكرين ورواد الأعمال</p>
            </div>
            
            <!-- محتوى الرسالة -->
            <div style="padding: 35px 30px;">
                <div style="display: inline-block; background-color: #e8f8f0; color: #0d6e3f; font-weight: bold; padding: 6px 14px; border-radius: 20px; font-size: 13px; margin-bottom: 20px;">
                    ✓ تم تأكيد واعتماد العضوية رسمياً
                </div>
                
                <h2 style="font-size: 20px; color: #133b66; margin-top: 0; margin-bottom: 15px;">
                    مرحباً بك يا {user.full_name}،
                </h2>
                
                <p style="font-size: 15px; line-height: 1.8; color: #495057; margin-bottom: 20px;">
                    يسرنا إبلاغك بأنه قد تمت مراجعة واعتماد طلب انضمامك إلى <strong>مجتمع الابتكار الليبي</strong> بنجاح من قبل إدارة الجمعية. أصبح حسابك الآن مفعلاً وجاهزاً للاستخدام، ويمكنك الآن تسجيل الدخول ونشر أفكارك ومشاريعك والاستفادة من كافة الفرص والبرامج الوطنية.
                </p>

                <!-- بطاقة ملخص الحساب المعتمد -->
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px 20px; margin-bottom: 25px;">
                    <h3 style="margin: 0 0 12px 0; font-size: 15px; color: #0d6e3f; font-weight: bold; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                        بيانات العضوية المعتمدة:
                    </h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr>
                            <td style="padding: 6px 0; color: #718096; width: 35%;">الاسم الكامل:</td>
                            <td style="padding: 6px 0; font-weight: bold; color: #2d3748;">{user.full_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">البريد الإلكتروني:</td>
                            <td style="padding: 6px 0; font-weight: bold; color: #2d3748;">{user.email}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">الوظيفة الحالية:</td>
                            <td style="padding: 6px 0; font-weight: bold; color: #2d3748;">{current_job}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">المسار المعتمد:</td>
                            <td style="padding: 6px 0; font-weight: bold; color: #2d3748;">{account_type_arabic}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">المدينة:</td>
                            <td style="padding: 6px 0; font-weight: bold; color: #2d3748;">{user.city or 'ليبيا'}</td>
                        </tr>
                    </table>
                </div>

                <!-- المزايا المتاحة الآن -->
                <h4 style="font-size: 16px; color: #133b66; margin-bottom: 10px;">ما الذي يمكنك البدء به الآن؟</h4>
                <ul style="font-size: 14px; line-height: 1.8; color: #4a5568; margin-bottom: 30px; padding-right: 20px;">
                    <li>تقديم أفكارك ومشاريعك الإبداعية للتقييم والتوجيه عبر لوحة التحكم.</li>
                    <li>التقديم المباشر في فرص الدعم، المنح المالية، وبرامج الاحتضان والمسرعات.</li>
                    <li>المشاركة في ورش العمل والبرامج التدريبية المعتمدة مجاناً.</li>
                    <li>التشبيك والتعاون المباشر مع نخبة المبتكرين والخبراء والمستثمرين في ليبيا.</li>
                </ul>

                <!-- زر الإجراء -->
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_url}" style="background-color: #0d6e3f; color: #ffffff; text-decoration: none; padding: 14px 35px; border-radius: 8px; font-size: 16px; font-weight: bold; display: inline-block; box-shadow: 0 4px 10px rgba(13, 110, 63, 0.3);">
                        الدخول إلى لوحة التحكم وحسابك
                    </a>
                </div>

                <p style="font-size: 13px; color: #718096; text-align: center; margin-top: 25px;">
                    إذا واجهتك أي صعوبة في الدخول، يمكنك التواصل مباشرة مع إدارة الجمعية عبر: <a href="mailto:{contact_email}" style="color: #0d6e3f;">{contact_email}</a>
                </p>
            </div>

            <!-- التذييل -->
            <div style="background-color: #f1f5f9; padding: 20px 25px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0 0 5px 0; font-weight: bold; color: #334155;">{site_name}</p>
                <p style="margin: 0 0 8px 0;">بموجب قرار إشهار رسمي رقم (525) لسنة 2026م</p>
                <p style="margin: 0; color: #94a3b8;">البريد الرسمي: {contact_email} | هاتف: {contact_phone}</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    {site_name}
    --------------------------------------------------
    تأكيد واعتماد انضمامك إلى مجتمع الابتكار الليبي

    مرحباً بك يا {user.full_name}،

    يسرنا إبلاغك بأنه قد تمت مراجعة واعتماد طلب انضمامك إلى مجتمع الابتكار الليبي بنجاح من قبل إدارة الجمعية.
    أصبح حسابك مفعلاً بالكامل الآن لتسجيل الدخول ونشر مشاريعك والاستفادة من كافة الفرص، مسرعات الأعمال، والتشبيك مع المبتكرين والخبراء.

    بيانات الحساب:
    - الاسم: {user.full_name}
    - البريد الإلكتروني: {user.email}
    - الوظيفة الحالية: {current_job}
    - المسار: {account_type_arabic}

    رابط الدخول لحسابك:
    {login_url}

    مع تحيات،
    مجلس إدارة {site_name}
    البريد الرسمي: {contact_email} | الهاتف: {contact_phone}
    """

    return send_email(user.email, subject, html_content, text_content)


def send_test_email(to_email):
    """إرسال رسالة تجريبية لفحص إعدادات البريد الإلكتروني وخادم SMTP"""
    cfg = get_mail_config()
    subject = "رسالة تجريبية - فحص إعدادات البريد الإلكتروني (libotechno@gmail.com)"
    html_content = f"""
    <div dir="rtl" style="font-family: Arial, Tahoma, sans-serif; padding: 25px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;">
        <h2 style="color: #0d6e3f; margin-top: 0;">✓ فحص اتصال البريد الإلكتروني ناجح</h2>
        <p style="font-size: 15px; color: #4a5568;">
            تم إرسال هذه الرسالة التجريبية بنجاح من المنصة الوطنية للابتكار وريادة الأعمال عبر خادم:
            <strong>{cfg['server']}:{cfg['port']}</strong>
        </p>
        <p style="font-size: 14px; color: #718096;">
            حساب المرسل المعتمد: <strong>{cfg['username']}</strong>
        </p>
        <div style="background: #e8f8f0; color: #0d6e3f; padding: 12px; border-radius: 6px; font-weight: bold;">
            إعدادات البريد جاهزة تماماً، وستصل رسائل تأكيد اعتماد العضوية للمستخدمين بنجاح.
        </div>
    </div>
    """
    text_content = f"رسالة تجريبية - اتصال البريد الإلكتروني عبر {cfg['server']} ({cfg['username']}) يعمل بنجاح."
    return send_email(to_email, subject, html_content, text_content)
