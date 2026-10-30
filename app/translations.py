"""
وحدة الترجمة المركزية للمنصة الوطنية للابتكار وريادة الأعمال
Centralized Translation Dictionary and Localization Utilities
"""

TRANSLATIONS = {
    # ------------------ عناصر عامة وأزرار ------------------
    'الرئيسية': 'Home',
    'عن الجمعية': 'About Us',
    'خدماتنا': 'Services',
    'البرامج والمبادرات': 'Programs & Initiatives',
    'الفرص والمنح': 'Opportunities & Grants',
    'التدريب': 'Training',
    'التدريب والأكاديمية': 'Academy & Training',
    'الأكاديمية والتدريب': 'Academy & Training',
    'الأكاديمية الرقمية': 'Digital Academy',
    'الفعاليات': 'Events',
    'الفعاليات والأنشطة': 'Events & Activities',
    'الفعاليات والملتقيات': 'Events & Gatherings',
    'الأخبار': 'News',
    'الأخبار والفعاليات': 'News & Events',
    'تواصل معنا': 'Contact Us',
    'اتصل بنا': 'Contact Us',
    'قدّم فكرتك': 'Submit Your Idea',
    'قدّم فكرتك الآن': 'Submit Your Idea Now',
    'تقديم فكرة مشروع': 'Submit a Project Idea',
    'تسجيل الدخول': 'Sign In',
    'انضم إلينا': 'Join Us',
    'تسجيل خروج': 'Log Out',
    'تسجيل الخروج': 'Log Out',
    'الملف الشخصي': 'My Profile',
    'لوحة التحكم': 'Dashboard',
    'لوحة التحكم الشخصية': 'My Dashboard',
    'لوحة الإدارة': 'Admin Panel',
    'مشاريعي وأفكاري': 'My Projects & Ideas',
    'فعالياتي': 'My Events',
    'فعالياتي ومناشطي': 'My Events & Activities',
    'دوراتي': 'My Courses',
    'دوراتي التدريبية': 'My Training Courses',
    'طلباتي': 'My Applications',
    'طلبات الدعم والمنح': 'My Grant Applications',
    'شبكة العلاقات': 'Networking & Mentorship',
    'الإشعارات': 'Notifications',
    'مركز الإشعارات': 'Notifications Center',
    'تعديل': 'Edit',
    'حذف': 'Delete',
    'حفظ': 'Save',
    'حفظ التعديلات': 'Save Changes',
    'إلغاء': 'Cancel',
    'إرسال': 'Submit',
    'إرسال الطلب': 'Submit Request',
    'تأكيد': 'Confirm',
    'عرض': 'View',
    'تفاصيل': 'Details',
    'المزيد': 'Read More',
    'رجوع': 'Back',
    'العودة': 'Go Back',
    'إغلاق': 'Close',
    'بحث': 'Search',
    'تصفية': 'Filter',
    'الكل': 'All',
    'تحميل': 'Download',
    'رفع': 'Upload',
    'اختياري': 'Optional',
    'إلزامي': 'Required',
    'موافق': 'Agree',
    'تصدير': 'Export',
    'طباعة': 'Print',
    'الحالة': 'Status',
    'التاريخ': 'Date',
    'المكان': 'Location',
    'المدينة': 'City',

    # ------------------ حقول النماذج المشتركة ------------------
    'الاسم الكامل': 'Full Name',
    'الاسم الثلاثي': 'Full Name',
    'البريد الإلكتروني': 'Email Address',
    'رقم الهاتف': 'Phone Number',
    'كلمة المرور': 'Password',
    'تأكيد كلمة المرور': 'Confirm Password',
    'تذكرني': 'Remember Me',
    'الوظيفة الحالية أو الصفة الأكاديمية': 'Current Occupation or Academic Title',
    'السيرة الذاتية (ملف PDF)': 'Curriculum Vitae (PDF file)',
    'أعمال ونشاطات سابقة في الابتكار وريادة الأعمال': 'Past Experience in Innovation & Entrepreneurship',
    'المسار أو صفة الحساب': 'Account Track / Role',
    'أوافق على الشروط وسياسة الخصوصية': 'I agree to the Terms of Service and Privacy Policy',
    'العنوان': 'Address',
    'الموضوع': 'Subject',
    'الرسالة': 'Message',
    'الملاحظات': 'Notes',
    'ملاحظات': 'Notes',
    'نبذة تعريفية': 'Brief Bio / Headline',
    'التخصص المهني / العلمي': 'Professional / Scientific Specialization',
    'الجامعة أو المؤسسة': 'University or Organization',
    'الشركة أو الجهة التابع لها': 'Company or Affiliation',
    'الجهة أو المنظمة': 'Organization or Entity',
    'رابط الموقع الإلكتروني': 'Website URL',
    'رابط LinkedIn': 'LinkedIn Profile URL',
    'رابط GitHub / Portfolio': 'GitHub / Portfolio URL',
    'إظهار الملف في الدليل الوطني العام': 'Display profile in the Public National Directory',

    # ------------------ نماذج المشاريع والابتكار ------------------
    'عنوان الفكرة أو المشروع': 'Project / Idea Title',
    'الموجز التنفيذي': 'Executive Summary',
    'وصف المشروع والمشكلة المعالجة': 'Project Description & Problem Solved',
    'الحل المبتكر المقترح': 'Proposed Innovative Solution',
    'القطاع المستهدف': 'Target Sector',
    'مرحلة النضج الحالية للمشروع': 'Current Project Maturity Stage',
    'النموذج التجاري ومصادر الإيرادات': 'Business Model & Revenue Streams',
    'التمويل المطلوب والدعم المستهدف': 'Required Funding & Support Needs',
    'الشريحة المستهدفة من السوق': 'Target Market Segment',
    'المنافسون والميزة التنافسية': 'Competitors & Competitive Edge',
    'ملف العرض التقديمي (Pitch Deck - PDF)': 'Pitch Deck Presentation (PDF)',
    'صورة أو شعار المشروع': 'Project Cover / Logo',
    'فيديو تعريفي أو رابط توضيحي': 'Demo Video / Link',

    # ------------------ خيارات القطاعات ------------------
    'تقنية المعلومات والذكاء الاصطناعي': 'IT & Artificial Intelligence',
    'الطاقة المتجددة والاستدامة': 'Renewable Energy & Sustainability',
    'الزراعة والتقنيات الحيوية': 'Agriculture & AgTech',
    'الرعاية الصحية والتقنية الطبية': 'HealthTech & Medical Innovation',
    'التعليم والتقنيات التعليمية': 'EdTech & Knowledge Systems',
    'التجارة الإلكترونية والتقنية المالية': 'E-Commerce & FinTech',
    'الصناعة والتحول الرقمي': 'Industrial & Digital Transformation',
    'خدمات وحلول مجتمعية': 'Social Solutions & Community Services',
    'قطاعات أخرى': 'Other Sectors',
    'كافة القطاعات': 'All Sectors',

    # ------------------ مراحل المشاريع ------------------
    'مجرد فكرة (Concept)': 'Idea / Concept Phase',
    'نموذج أولي تجريبي (Prototype)': 'Prototype / Proof of Concept',
    'منتج أولي قابل للإطلاق (MVP)': 'Minimum Viable Product (MVP)',
    'شركة ناشئة في مرحلة الإطلاق (Early Stage)': 'Early Stage Startup',
    'شركة ناشئة قيد النمو والتوسع (Growth)': 'Growth / Scaling Stage',

    # ------------------ أدوار ومسارات المستخدمين ------------------
    'مبتكر / صاحب فكرة': 'Innovator / Idea Creator',
    'شركة ناشئة / رائد أعمال': 'Startup Founder / Entrepreneur',
    'خبير / موجه / مدرب': 'Mentor / Expert / Trainer',
    'مستثمر / جهة تمويل': 'Investor / Funding Body',
    'مؤسسة داعمة / جامعة': 'Partner Organization / University',
    'مدير النظام (Admin)': 'System Administrator',
    'محرر محتوى (Editor)': 'Content Editor',
    'مراجع ومقيم مشاريع (Reviewer)': 'Project Reviewer & Evaluator',
    'عضو الجمعية (Member)': 'Society Member',

    # ------------------ حالات وحالات المشاريع والطلبات ------------------
    'قيد المراجعة والتقييم': 'Under Review & Evaluation',
    'معتمد ومقبول': 'Accepted & Approved',
    'مرفوض مع ملاحظات': 'Declined with Feedback',
    'مكتمل': 'Completed',
    'قيد الانتظار': 'Pending Approval',
    'مؤكد': 'Confirmed',
    'نشط': 'Active',
    'مغلق': 'Closed',
    'مفتوح': 'Open',
    'مؤرشف': 'Archived',
    'منشور': 'Published',
    'مسودة': 'Draft',

    # ------------------ تصنيفات الأخبار ------------------
    'أخبار الجمعية': 'Society News',
    'مقال تحليلي': 'Analytical Article',
    'قصة نجاح ريادية': 'Entrepreneurial Success Story',
    'إعلان رسمي': 'Official Announcement',
    'تقرير وإحصاء': 'Report & Statistics',

    # ------------------ أنواع الفعاليات ------------------
    'مؤتمر علمي / ريادي': 'Scientific / Entrepreneurial Conference',
    'منتدى حواري': 'Discussion Forum',
    'ورشة عمل تدريبية': 'Training Workshop',
    'هاكاثون ومنافسة برمجية': 'Hackathon & Tech Challenge',
    'يوم العروض (Demo Day)': 'Demo Day & Pitching',
    'لقاء تشبيك وتواصل': 'Networking Meetup',

    # ------------------ أنماط الحضور ------------------
    'حضوري بالمقر': 'In-Person at Venue',
    'حضوري': 'In-Person',
    'عبر الإنترنت (افتراضي)': 'Online / Virtual',
    'افتراضي عن بُعد': 'Virtual / Online',
    'عن بُعد (Online)': 'Online',
    'مدمج (حضوري وافتراضي)': 'Hybrid (In-Person & Online)',
    'مدمج': 'Hybrid',

    # ------------------ أنواع الفرص ------------------
    'منحة ابتكار وتمويل': 'Innovation Grant & Funding',
    'منحة ابتكارية': 'Innovation Grant',
    'مسابقة وجوائز': 'Competition & Awards',
    'مسابقة وجوائز تحفيزية': 'Competition & Incentive Awards',
    'برنامج احتضان': 'Incubation Program',
    'برنامج احتضان مشاريع': 'Project Incubation Program',
    'برنامج تسريع نمو': 'Acceleration Program',
    'برنامج تسريع أعمال': 'Business Acceleration',
    'فرصة استثمارية': 'Investment Opportunity',
    'فرصة استثمارية وتشبيك': 'Investment & Networking',
    'جائزة سنوية': 'Annual Award',
    'جائزة وطنية سنوية': 'National Annual Award',

    # ------------------ أنواع التدريب ------------------
    'دورة تدريبية متخصصة': 'Specialized Training Course',
    'دورة تدريبية': 'Training Course',
    'ورشة عمل تطبيقية': 'Applied Workshop',
    'مخيم تدريبي مكثف': 'Intensive Bootcamp',
    'ندوة معرفية افتراضية': 'Knowledge Webinar',

    # ------------------ أنواع الشراكات ------------------
    'جهة حكومية / هيئة رسمية': 'Governmental / Official Entity',
    'جامعة أو مركز بحث علمي': 'University / Research Center',
    'حاضنة / مسرعة أعمال': 'Incubator / Accelerator',
    'قطاع خاص وشركات رائدة': 'Private Sector / Leading Company',
    'منظمة دولية / جهة مانحة': 'International Organization / Donor',

    # ------------------ حالات إدارية وإضافات شائعة ------------------
    'مفعّل': 'Active',
    'معطل': 'Inactive',
    'معطّل': 'Disabled',
    'منشورة': 'Published',
    'غير موثقة': 'Unverified',
    'موثقة': 'Verified',
    'نعم': 'Yes',
    'لا': 'No',
    'مكتمل': 'Completed',
    'إلغاء والعودة': 'Cancel & Return',
    'حفظ التغييرات': 'Save Changes',
    'تنزيل الملف': 'Download File',
    'لا يوجد ملف': 'No file attached',
    'تصدير Excel': 'Export to Excel',
    'إدارة الفعاليات والأنشطة': 'Events & Activities Management',
    'إدارة البرامج التدريبية والأكاديمية': 'Training & Academy Management',
    'إدارة الفرص والمنح': 'Opportunities & Grants Management',
    'إدارة الأخبار والمقالات': 'News & Articles Management',
    'إدارة المشاريع الابتكارية': 'Innovation Projects Management',
    'إدارة المستخدمين والأعضاء': 'Users & Members Management',
    'إدارة الشركات الناشئة والمؤسسات': 'Startups & Organizations Management',
    'مركز التقارير الموحد وتصدير البيانات': 'Unified Reports Center & Data Export',
    'النسخ الاحتياطي والاستعادة': 'Backup & Disaster Recovery',
    'سجل التدقيق والأنشطة الإدارية': 'Audit Logs & Administrative Activity',
    'إدارة الإعدادات والهوية والشعار': 'Platform Settings & Identity',
    'الدليل الوطني للابتكار': 'National Innovation Directory'
}


def translate(text_or_key, en_text=None, lang='ar'):
    """
    دالة الترجمة الذكية:
    إذا كانت اللغة الإنجليزية:
      - تُرجع النص الإنجليزي المعطى صراحة إن وجد (en_text)
      - أو تبحث في قاموس الترجمات عن ترجمة النص العربي
      - أو تُرجع النص كما هو إن لم يتوفر بديل
    إذا كانت اللغة العربية:
      - تُرجع النص الأصلي
    """
    if not text_or_key:
        return ''
        
    if lang == 'en':
        if en_text is not None and en_text != '':
            return en_text
        str_key = str(text_or_key).strip()
        if str_key in TRANSLATIONS:
            return TRANSLATIONS[str_key]
        return str_key
        
    return text_or_key
