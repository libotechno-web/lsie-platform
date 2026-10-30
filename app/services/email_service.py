import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from flask import current_app, url_for


def get_mail_config():
    """الحصول على إعدادات خادم البريد من البيئة أو ملف الإعدادات"""
    return {
        'server': os.environ.get('MAIL_SERVER'),
        'port': int(os.environ.get('MAIL_PORT', 587)),
        'use_tls': os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes'),
        'use_ssl': os.environ.get('MAIL_USE_SSL', 'false').lower() in ('true', '1', 'yes'),
        'username': os.environ.get('MAIL_USERNAME', ''),
        'password': os.environ.get('MAIL_PASSWORD', ''),
        'default_sender': os.environ.get('MAIL_DEFAULT_SENDER', '')
    }


def send_email(to_email, subject, html_content, text_content=None):
    """
    إرسال رسالة بريد إلكتروني مع دعم RTL والقوالب الجميلة.
    في بيئة التطوير والاختبار، إذا لم يكن هناك خادم SMTP حقيقي مُهيّأ، يتم توثيق الرسالة بأمان بدون تعطيل الطلب.
    """
    try:
        from app.models.settings import SiteSetting
        site_name = SiteSetting.get_value('site_name', 'الجمعية الليبية للابتكار وريادة الأعمال')
        contact_email = SiteSetting.get_value('contact_email', 'info@lsie.ly')
    except Exception:
        site_name = 'الجمعية الليبية للابتكار وريادة الأعمال'
        contact_email = 'info@lsie.ly'

    cfg = get_mail_config()
    sender_email = cfg['default_sender'] or contact_email or 'noreply@lsie.ly'
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = f"{Header(site_name, 'utf-8').encode()} <{sender_email}>"
    msg['To'] = to_email

    if text_content:
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
    if html_content:
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    # التحقق من بيئة الاختبار أو عدم وجود خادم SMTP مضبوط
    if current_app.config.get('TESTING') or not cfg['server']:
        current_app.logger.info(f"[EmailService] المحاكاة: تم تسجيل بريد إلى '{to_email}' بعنوان: '{subject}'.")
        return True, "تم تسجيل وإرسال البريد بنجاح (نمط بيئة التطوير)."

    try:
        if cfg['use_ssl']:
            server = smtplib.SMTP_SSL(cfg['server'], cfg['port'], timeout=10)
        else:
            server = smtplib.SMTP(cfg['server'], cfg['port'], timeout=10)
            if cfg['use_tls']:
                server.starttls()

        if cfg['username'] and cfg['password']:
            server.login(cfg['username'], cfg['password'])

        server.send_message(msg)
        server.quit()
        current_app.logger.info(f"[EmailService] تم إرسال البريد بنجاح إلى '{to_email}'.")
        return True, "تم إرسال البريد الإلكتروني بنجاح."
    except Exception as e:
        current_app.logger.error(f"[EmailService] تعذر الإرسال عبر SMTP ({e}). تم التدوين في سجلات المنصة.")
        return False, str(e)


def send_registration_confirmation_email(user):
    """
    إرسال رسالة تأكيد رسمية للمستخدم فور اعتماد وتسجيل انضمامه لمجتمع الابتكار
    """
    try:
        from app.models.settings import SiteSetting
        site_name = SiteSetting.get_value('site_name', 'الجمعية الليبية للابتكار وريادة الأعمال')
        contact_email = SiteSetting.get_value('contact_email', 'info@lsie.ly')
        contact_phone = SiteSetting.get_value('contact_phone', '+218 21 000 0000')
    except Exception:
        site_name = 'الجمعية الليبية للابتكار وريادة الأعمال'
        contact_email = 'info@lsie.ly'
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
                    يسرنا إبلاغك بأنه قد تمت مراجعة واعتماد طلب انضمامك إلى <strong>مجتمع الابتكار الليبي</strong> بنجاح من قبل إدارة الجمعية. حسابك الآن نشط ومفعل بالكامل للاستفادة من كافة الفرص والبرامج الوطنية.
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
                        الدخول إلى المنصة وحسابك
                    </a>
                </div>

                <p style="font-size: 13px; color: #718096; text-align: center; margin-top: 25px;">
                    إذا واجهتك أي صعوبة في الدخول، يمكنك التواصل مباشرة مع فريق الدعم الفني للجمعية عبر: <a href="mailto:{contact_email}" style="color: #0d6e3f;">{contact_email}</a>
                </p>
            </div>

            <!-- التذييل -->
            <div style="background-color: #f1f5f9; padding: 20px 25px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0 0 5px 0; font-weight: bold; color: #334155;">{site_name}</p>
                <p style="margin: 0 0 8px 0;">بموجب قرار إشهار رسمي رقم (525) لسنة 2026م</p>
                <p style="margin: 0; color: #94a3b8;">هذه رسالة تلقائية لتأكيد اعتماد الحساب، يرجى عدم الرد المباشر على هذا البريد إلا عبر قنوات التواصل الرسمية.</p>
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
    أصبح حسابك مفعلاً بالكامل للاستفادة من كافة الفرص، مسرعات الأعمال، والتشبيك مع المبتكرين والخبراء.

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
