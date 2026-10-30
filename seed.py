import os
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import (
    User, Role, UserProfile, SiteSetting, NavigationItem,
    StrategicObjective, OrganizationalValue, Page, Partner,
    Opportunity, TrainingCourse, Event, Article
)

app = create_app('development')

def seed_database():
    with app.app_context():
        # إنشاء الجداول إن لم تكن موجودة
        db.create_all()
        print("Database tables verified.")

        # 1. تهيئة الأدوار الأساسية (Roles)
        roles_data = [
            ('admin', 'مدير النظام (Admin)', 'صلاحيات إدارية كاملة للمنصة وإعداداتها ومستخدميها', True),
            ('editor', 'محرر محتوى (Editor)', 'إدارة الأخبار، المقالات، الفعاليات، والصفحات التعريفية', True),
            ('reviewer', 'مراجع ومقيم مشاريع (Reviewer)', 'مراجعة الأفكار والمشاريع وتقييمها وإبداء التوصيات الفنية', True),
            ('member', 'عضو الجمعية (Member)', 'عضوية معتمدة ومسجلة في الجمعية العلمية', True),
            ('innovator', 'مبتكر / صاحب فكرة', 'أصحاب الحلول الإبداعية والأفكار القابلة للتطبيق', False),
            ('startup', 'شركة ناشئة / رائد أعمال', 'الشركات الناشئة في مراحل التأسيس والنمو', False),
            ('investor', 'مستثمر / جهة تمويل', 'المستثمرون الأفراد وصناديق رأس المال الجريء', False),
            ('expert', 'خبير / موجه / مدرب', 'الخبراء والاستشاريون في مجالات التوجيه والتدريب', False),
            ('partner_org', 'مؤسسة داعمة / جامعة', 'الجامعات وحاضنات الأعمال ومراكز البحوث', False)
        ]

        created_roles = {}
        for name, title_ar, desc, is_sys in roles_data:
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name, title_ar=title_ar, description=desc, is_system=is_sys)
                db.session.add(role)
            created_roles[name] = role
        db.session.commit()
        print("Roles initialized.")

        # 2. إنشاء حساب المدير الأساسي (Admin Account)
        admin_email = os.environ.get('INITIAL_ADMIN_EMAIL', 'admin@lsie.ly')
        admin_pass = os.environ.get('INITIAL_ADMIN_PASSWORD', 'Admin@LSIE2026!')
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                full_name='المدير العام للمنصة',
                phone='0910000000',
                city='غريان',
                account_type='admin',
                headline='مدير المنصة الوطنية للابتكار وريادة الأعمال',
                is_active=True,
                is_verified=True,
                is_approved_member=True
            )
            admin_user.set_password(admin_pass)
            admin_user.roles.append(created_roles['admin'])
            admin_user.roles.append(created_roles['reviewer'])
            admin_user.roles.append(created_roles['editor'])
            
            profile = UserProfile(
                user=admin_user,
                specialization='إدارة منظومات الابتكار والتحول الرقمي',
                is_public_in_directory=False
            )
            db.session.add(admin_user)
            db.session.add(profile)
            db.session.commit()
            print(f"Admin created: {admin_email} / {admin_pass}")
        else:
            print("Admin user already exists.")

        # 3. إعدادات الموقع الرسمية (Site Settings)
        settings_data = [
            ('site_name', 'الجمعية الليبية للابتكار وريادة الأعمال', 'general', 'اسم الجمعية بالعربية', 'text'),
            ('site_name_en', 'Libyan Society for Innovation & Entrepreneurship', 'general', 'اسم الجمعية بالإنجليزية', 'text'),
            ('site_acronym', 'L.S.I.E', 'general', 'المختصر الرسمي', 'text'),
            ('hero_title', 'من الفكرة إلى مشروع يصنع المستقبل', 'general', 'عنوان الهيرو الرئيسي', 'text'),
            ('hero_subtitle', 'المنصة الوطنية الموحدة لتمكين المبتكرين ورواد الأعمال وأصحاب الشركات الناشئة في ليبيا، وبناء جسور التعاون بين البحث العلمي والسوق الاقتصادي.', 'general', 'نص الهيرو الفرعي', 'textarea'),
            
            ('about_intro', 'الجمعية الليبية للابتكار وريادة الأعمال هي جمعية تُعنى بدعم الابتكار وتعزيز ثقافة ريادة الأعمال في ليبيا، والعمل على إيجاد بيئة حاضنة تساعد المبتكرين ورواد الأعمال على تطوير أفكارهم وتحويلها إلى مشاريع قابلة للتطبيق والنمو. أُنشئت الجمعية بموجب قرار صادر عن رئيس الهيئة الليبية للبحث العلمي، وتسعى إلى بناء جسور التعاون بين المبتكرين والشركات والجامعات والمستثمرين والخبراء والجهات الداعمة، بما يسهم في تنمية الاقتصاد الوطني وتعزيز دور المعرفة والتكنولوجيا في معالجة التحديات المحلية.', 'about', 'المقدمة التعريفية الرسمية', 'textarea'),
            ('official_mission', 'تمكين المبتكرين ورواد الأعمال الليبيين عبر توفير بيئة حاضنة ومتكاملة تجمع بين التدريب، التوجيه، والتشبيك. نحن نسعى لجس الفجوة بين الأفكار الإبداعية والواقع السوقي، من خلال بناء شراكات استراتيجية تضمن تحويل التحديات المحلية إلى فرص اقتصادية ناجحة.', 'about', 'الرسالة الرسمية للجمعية', 'textarea'),
            ('official_vision', 'أن تكون الجمعية المنصة الوطنية الرائدة المحفزة لبيئة الابتكار واقتصاد المعرفة في ليبيا، وتمكين رواد الأعمال والمبتكرين من قيادة التنمية المستدامة والمنافسة إقليمياً ودولياً.', 'about', 'الرؤية الرسمية للجمعية', 'textarea'),
            
            ('establishment_decree', 'قرار إشهار رقم (525) لسنة 2026م صادر عن الهيئة الليبية للبحث العلمي، استناداً إلى القرار رقم (1714) لسنة 2025م.', 'official', 'قرار الإشهار والتأسيس', 'text'),
            ('headquarters', 'المقر الرئيسي: جامعة غريان، غريان، ليبيا', 'official', 'المقر الرسمي', 'text'),
            ('certificate_number', 'LARS-SCS-2026-042', 'official', 'رقم شهادة مزاولة النشاط العلمي', 'text'),
            ('authority_name', 'الهيئة الليبية للبحث العلمي - وزارة التعليم العالي والبحث العلمي', 'official', 'الجهة المشرفة والمرخصة', 'text'),
            
            ('primary_color', '#0d6e3f', 'appearance', 'اللون الأساسي (أخضر الجمعية)', 'color'),
            ('secondary_color', '#133b66', 'appearance', 'اللون الثانوي (أزرق بحري)', 'color'),
            ('accent_color', '#e5a93c', 'appearance', 'لون التمييز (ذهبي الابتكار)', 'color'),
            ('logo_path', 'images/logo.png', 'appearance', 'مسار الشعار الرسمي', 'image'),
            
            ('contact_email', 'info@lsie.ly', 'contact', 'البريد الإلكتروني الرسمي', 'text'),
            ('contact_phone', '+218 21 000 0000', 'contact', 'هاتف الجمعية', 'text'),
            ('contact_address', 'جامعة غريان، غريان، دولة ليبيا', 'contact', 'العنوان الرسمي', 'text'),
            
            ('facebook_url', 'https://facebook.com/lsie.libya', 'social', 'صفحة Facebook', 'text'),
            ('instagram_url', 'https://instagram.com/lsie.libya', 'social', 'حساب Instagram', 'text'),
            ('twitter_x_url', 'https://x.com/lsie_libya', 'social', 'حساب X (تويتر)', 'text'),
            ('linkedin_url', 'https://linkedin.com/company/lsie-libya', 'social', 'صفحة LinkedIn', 'text'),
            ('youtube_url', '', 'social', 'قناة YouTube', 'text')
        ]

        for key, val, grp, lbl, stype in settings_data:
            SiteSetting.set_value(key, val, group=grp, label=lbl, setting_type=stype)
        print("Site settings seeded.")

        # 4. الأهداف الاستراتيجية (Strategic Objectives)
        objectives_data = [
            ("نشر ثقافة الابتكار وريادة الأعمال", "تعزيز الفكر الإبداعي لدى الشباب والباحثين وطلاب الجامعات وتشجيع المبادرة الاقتصادية الحرة.", "bi-lightbulb", 1),
            ("احتضان الأفكار والمشاريع الناشئة", "توفير بيئة متكاملة تجمع بين الدعم التوجيهي، الاستشارات المتخصصة، والمرافق التقنية لنقل الأفكار إلى منتجات حقيقية.", "bi-box-seam", 2),
            ("بناء جسور التمويل والاستثمار", "تسهيل وصول المبتكرين والشركات الواعدة إلى المستثمرين الملائكيين، صناديق رأس المال الجريء، والمؤسسات التمويلية.", "bi-cash-coin", 3),
            ("التشبيك والشراكات الاستراتيجية", "الربط الفعال بين الجامعات والمراكز البحثية والقطاع الصناعي والتجاري لتحويل البحوث إلى حلول سوقية ملموسة.", "bi-diagram-3", 4),
            ("تطوير القدرات وتأهيل الكفاءات", "تقديم برامج تدريبية احترافية ومخيمات ابتكار تواكب أفضل الممارسات والمعايير العالمية في ريادة الأعمال.", "bi-mortarboard", 5)
        ]
        if StrategicObjective.query.count() == 0:
            for title, desc, icon, ord_idx in objectives_data:
                db.session.add(StrategicObjective(title=title, description=desc, icon=icon, order_index=ord_idx))
            db.session.commit()
            print("Strategic objectives seeded.")

        # 5. القيم المؤسسية (Organizational Values)
        values_data = [
            ("الأصالة والابتكار", "نشجع الأفكار الخلاقة ونؤمن بأن الحلول غير التقليدية هي السبيل لمواجهة التحديات التنموية الوطنية.", "bi-gem", 1),
            ("النزاهة والشفافية", "نلتزم بأعلى معايير الحوكمة العادلة وحماية حقوق الملكية الفكرية وسرية بيانات المبتكرين والمستثمرين.", "bi-shield-check", 2),
            ("الشراكة والتكامل", "نؤمن بأن النجاح المستدام يتحقق بتضافر جهود المجتمع الريادي والأكاديمي والجهات الحكومية والخاصة.", "bi-people", 3),
            ("الأثر والاستدامة", "نركز على المشاريع والمبادرات التي تحقق أثراً اقتصادياً ومجتمعياً ملموساً يساهم في بناء مستقبل ليبيا.", "bi-graph-up-arrow", 4)
        ]
        if OrganizationalValue.query.count() == 0:
            for title, desc, icon, ord_idx in values_data:
                db.session.add(OrganizationalValue(title=title, description=desc, icon=icon, order_index=ord_idx))
            db.session.commit()
            print("Organizational values seeded.")

        # 6. القائمة الرئيسية (Navigation Items)
        nav_data = [
            ("الرئيسية", "Home", "/", "bi-house", 1),
            ("عن الجمعية", "About", "/about", "bi-info-circle", 2),
            ("خدماتنا", "Services", "/services", "bi-grid", 3),
            ("البرامج والمبادرات", "Programs", "/programs", "bi-trophy", 4),
            ("الفرص والمنح", "Opportunities", "/opportunities", "bi-gift", 5),
            ("التدريب والأكاديمية", "Training", "/training", "bi-mortarboard", 6),
            ("الأخبار والفعاليات", "News & Events", "/news", "bi-newspaper", 7),
            ("تواصل معنا", "Contact", "/contact", "bi-envelope", 8)
        ]
        if NavigationItem.query.count() == 0:
            for t_ar, t_en, url, icon, ord_idx in nav_data:
                db.session.add(NavigationItem(title_ar=t_ar, title_en=t_en, url=url, icon=icon, order_index=ord_idx, is_active=True))
            db.session.commit()
            print("Navigation items seeded.")

        # 7. الشركاء الرسميون (Partners)
        if Partner.query.count() == 0:
            p1 = Partner(name='الهيئة الليبية للبحث العلمي', partner_type='governmental', website_url='https://research.gov.ly', description='الجهة الراعية والمشرفة على إشهار الجمعية العلمية', order_index=1)
            p2 = Partner(name='جامعة غريان', partner_type='academic', website_url='https://gharyan.edu.ly', description='المقر الرئيسي الرسمي الحاضن للجمعية', order_index=2)
            p3 = Partner(name='وزارة التعليم العالي والبحث العلمي', partner_type='governmental', description='المظلة الوزارية لقطاع البحث والابتكار الوطني', order_index=3)
            db.session.add_all([p1, p2, p3])
            db.session.commit()
            print("Partners seeded.")

        # 8. الصفحات الثابتة (CMS Pages)
        if Page.query.count() == 0:
            page_privacy = Page(
                title='سياسة الخصوصية وحماية البيانات',
                slug='privacy-policy',
                summary='التزام الجمعية الصارم بحماية خصوصية المبتكرين وسرية الأفكار والبيانات المدخلة في المنصة.',
                content_html='''
                <h3>1. حماية الملكية الفكرية وسرية الأفكار</h3>
                <p>تدرك الجمعية الليبية للابتكار وريادة الأعمال حساسية الأفكار والمشاريع الريادية المقدمة عبر المنصة. وعليه، فإن كافة التفاصيل الفنية ونماذج الأعمال المودعة تظل سرية ومحمية بموجب اتفاقيات سرية صارمة يلتزم بها المقيمون وأعضاء اللجان الفنية.</p>
                <h3>2. البيانات الشخصية</h3>
                <p>لا يتم مشاركة بيانات الاتصال الشخصية مع أطراف ثالثة إلا بعد الموافقة الصريحة للمستخدم أو عند قبوله المتبادل لطلب تشبيك أو إرشاد.</p>
                <h3>3. ملفات تعريف الارتباط والأمان</h3>
                <p>تستخدم المنصة بروتوكولات حماية مشفرة وتقنيات التحقق الآمن لمنع أي اختراق أو وصول غير مصرح به للمعلومات.</p>
                ''',
                order_index=1
            )
            page_terms = Page(
                title='شروط وأحكام الاستخدام',
                slug='terms-of-service',
                summary='القواعد والضوابط المنظمة لاستخدام المنصة الوطنية للابتكار.',
                content_html='''
                <h3>1. شروط الأهلية والتقديم</h3>
                <p>يحق لجميع المواطنين والمقيمين من أصحاب الأفكار والشركات الناشئة في ليبيا التقديم والاستفادة من خدمات الجمعية وفق المعايير الفنية المعتمدة في النظام الأساسي.</p>
                <h3>2. صحة البيانات</h3>
                <p>يتعهد مقدم الطلب بصحة كافة المعلومات المقدمة وأصالة الفكرة أو المشروع المبتكر، وتحمل المسؤولية القانونية والأخلاقية إزاء أي انتهاك لحقوق ملكية فكرية تخص أطرافاً أخرى.</p>
                ''',
                order_index=2
            )
            db.session.add_all([page_privacy, page_terms])
            db.session.commit()
            print("Pages seeded.")

        # 9. فرصة رسمية نموذجية (Opportunity)
        if Opportunity.query.count() == 0:
            opp = Opportunity(
                title='المبادرة الوطنية لتمويل النماذج الأولية الابتكارية 2026',
                slug='national-prototype-fund-2026',
                opportunity_type='grant',
                provider_name='الجمعية الليبية للابتكار بالتعاون مع الهيئة الليبية للبحث العلمي',
                summary='برنامج دعم ومنح تنافسية موجه لتحويل الأفكار الإبداعية إلى نماذج أولية قابلة للاختبار في السوق الليبي.',
                description='يهدف البرنامج إلى تقديم الدعم الفني والمادي المباشر للفرق الريادية والمبتكرين في مجالات التكنولوجيا، الزراعة، الصحة، والطاقة المتجددة.',
                eligibility_criteria='- أن يكون المشروع مبتكراً ويعالج تحدياً حقيقياً في البيئة الليبية.\n- توفر فريق عمل يمتلك المهارات الأساسية للتنفيذ.\n- التقديم عبر المنصة الرسمية قبل موعد الإغلاق.',
                target_audience='المبتكرون، خريجو الجامعات، والشركات الناشئة في مراحلها المبكرة',
                award_or_funding='دعم مالي مخصص للنموذج الأولي + احتضان وإرشاد فني متخصص لمدة 6 أشهر',
                sector='تقنية المعلومات، الطاقة، الصحة، الزراعة',
                city='كافة المدن الليبية',
                deadline=datetime.utcnow() + timedelta(days=45),
                status='open',
                is_featured=True
            )
            db.session.add(opp)
            db.session.commit()
            print("Initial opportunity seeded.")

        # 10. برنامج تدريبي نموذجي (Training Course)
        if TrainingCourse.query.count() == 0:
            course = TrainingCourse(
                title='معسكر بناء نموذج العمل التجاري للشركات الناشئة (Lean Startup Workshop)',
                slug='lean-startup-workshop-2026',
                trainer_name='نخبة من خبراء وموجهي الجمعية',
                trainer_title='مستشارو تطوير الأعمال ونماذج الابتكار',
                course_type='workshop',
                delivery_mode='hybrid',
                location_or_link='مقر الجمعية بجامعة غريان وبث مباشر عبر المنصة',
                summary='ورشة عمل تطبيقية مكثفة تركز على اختبار الفرضيات، بناء لوحة نموذج العمل التجاري (Business Model Canvas)، والوصول السريع إلى ملاءمة المنتج للسوق.',
                description='ستتعلم خلال هذه الورشة كيفية تحديد القيمة المضافة لابتكارك، تحليل سلوك العملاء، وبناء نموذج مالي أولي يضمن استدامة المشروع وجاذبيته للمستثمرين.',
                learning_objectives='- صياغة وتصميم لوحة نموذج العمل التجاري.\n- آليات التحقق من حاجة السوق (Customer Discovery).\n- مهارات العرض والإقناع أمام المستثمرين (Pitching).',
                prerequisites='وجود فكرة مشروع ابتكاري أو شركة ناشئة قيد التأسيس.',
                start_date=datetime.utcnow() + timedelta(days=15),
                end_date=datetime.utcnow() + timedelta(days=18),
                duration_hours=16,
                max_seats=35,
                certificate_included=True,
                is_free=True,
                registration_status='open',
                is_featured=True
            )
            db.session.add(course)
            db.session.commit()
            print("Initial training course seeded.")

        # 11. خبر افتتاحي رسمي (Article)
        if Article.query.count() == 0:
            art = Article(
                title='إشهار الجمعية الليبية للابتكار وريادة الأعمال بموجب قرار الهيئة الليبية للبحث العلمي',
                slug='official-establishment-lsie-announcement',
                category='announcement',
                summary='في خطوة وطنية استراتيجية لتعزيز اقتصاد المعرفة، أُعلن رسمياً عن إشهار الجمعية بقرار رقم 525 لسنة 2026م واتخاذ جامعة غريان مقراً رئيسياً لها.',
                content_html='''
                <p>أُعلن رسمياً عن صدور شهادة مزاولة نشاط جمعية علمية رقم <strong>(LARS-SCS-2026-042)</strong> الصادرة عن قسم الجمعيات العلمية بإدارة العلاقات العلمية والثقافية بالهيئة الليبية للبحث العلمي، معلنة تأسيس وإشهار <strong>الجمعية الليبية للابتكار وريادة الأعمال</strong> استناداً للقرار رقم (1714) لسنة 2025م وقرار الإشهار رقم (525) لسنة 2026م.</p>
                <p>واتخذت الجمعية من رحاب <strong>جامعة غريان</strong> مقراً رئيسياً لها، لتبدأ مسيرتها في ربط الأوساط البحثية والأكاديمية بالسوق المحلي، وتمكين المبتكرين ورواد الأعمال من مختلف ربوع ليبيا عبر توفير بيئة حاضنة متكاملة تواكب التحولات الرقمية الحديثة.</p>
                ''',
                author_name='إدارة العلاقات والإعلام',
                status='published',
                is_featured=True,
                published_at=datetime.utcnow()
            )
            db.session.add(art)
            db.session.commit()
            print("Initial news article seeded.")

        print("=== Database Seeding Completed Successfully! ===")

if __name__ == '__main__':
    seed_database()
