import unittest
import os
import io
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import (
    User, Role, UserProfile, InnovationProject, ProjectReview,
    Opportunity, TrainingCourse, CourseEnrollment, NetworkingRequest,
    SiteSetting, StrategicObjective
)


class PlatformTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # إنشاء الأدوار الأساسية
        self.admin_role = Role(name='admin', title_ar='مدير النظام')
        self.member_role = Role(name='member', title_ar='عضو')
        self.reviewer_role = Role(name='reviewer', title_ar='مقيم فني')
        self.innovator_role = Role(name='innovator', title_ar='مبتكر')
        db.session.add_all([self.admin_role, self.member_role, self.reviewer_role, self.innovator_role])

        # إنشاء مستخدم عادي
        self.user = User(
            email='innovator@test.ly',
            full_name='مبتكر ليبي',
            phone='0911111111',
            city='غريان',
            account_type='innovator',
            is_active=True
        )
        self.user.set_password('Secret123!')
        self.user.roles.append(self.innovator_role)

        # إنشاء حساب مدير
        self.admin = User(
            email='admin@test.ly',
            full_name='مدير النظام',
            phone='0922222222',
            city='غريان',
            account_type='admin',
            is_active=True
        )
        self.admin.set_password('AdminSecret123!')
        self.admin.roles.extend([self.admin_role, self.reviewer_role])
        
        self.admin_profile = UserProfile(user=self.admin, is_public_in_directory=True)
        self.user_profile = UserProfile(user=self.user, is_public_in_directory=True)

        db.session.add_all([self.user, self.admin, self.admin_profile, self.user_profile])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_user(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def test_user_registration_and_login(self):
        """1. اختبار تسجيل مستخدم جديد وتسجيل الدخول والخروج"""
        res = self.client.post('/auth/register', data={
            'full_name': 'رائد أعمال جديد',
            'email': 'new_entrepreneur@test.ly',
            'phone': '0933333333',
            'city': 'طرابلس',
            'account_type': 'startup',
            'current_job': 'مؤسس شركة تقنية ناشئة',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'terms': True
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        created_user = User.query.filter_by(email='new_entrepreneur@test.ly').first()
        self.assertIsNotNone(created_user)
        self.assertTrue(created_user.check_password('Password123!'))
        self.assertFalse(created_user.is_approved_member) # بانتظار تأكيد الأدمن
        self.assertEqual(created_user.current_job, 'مؤسس شركة تقنية ناشئة')

        # تسجيل الخروج
        logout_res = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(logout_res.status_code, 200)

    def test_rbac_security_protection(self):
        """2. اختبار الأمان ومنع المستخدم العادي من دخول لوحة الإدارة (Server-Side RBAC)"""
        # محاولة دخول زائر غير مسجل
        res_guest = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(res_guest.status_code, 302) # توجيه لصفحة تسجيل الدخول

        # دخول مستخدم عادي بدون صلاحية admin
        self.login_user('innovator@test.ly', 'Secret123!')
        res_forbidden = self.client.get('/admin/users', follow_redirects=False)
        self.assertEqual(res_forbidden.status_code, 403) # ممنوع 403

        # خروج
        self.client.get('/auth/logout')

        # دخول بحساب المدير
        self.login_user('admin@test.ly', 'AdminSecret123!')
        res_admin = self.client.get('/admin/users', follow_redirects=False)
        self.assertEqual(res_admin.status_code, 200) # مسموح 200

    def test_project_submission_and_lifecycle(self):
        """3. اختبار تقديم فكرة مشروع ودورة حياة التقييم"""
        self.login_user('innovator@test.ly', 'Secret123!')
        
        # تقديم فكرة
        res = self.client.post('/dashboard/submit-project', data={
            'title': 'نظام الطاقة الشمسية الذكي',
            'tagline': 'طاقة مستدامة للمنازل والمزارع',
            'sector': 'الطاقة المتجددة والاستدامة',
            'city': 'غريان',
            'stage': 'prototype',
            'summary': 'مشروع لتوليد الطاقة الشمسية بتكلفة اقتصادية وتخزين ذكي.',
            'problem_statement': 'انقطاع التيار الكهربائي المتكرر في المناطق الزراعية.',
            'proposed_solution': 'ألواح شمسية ومحولات ذكية تعمل بنظام إنترنت الأشياء IoT.',
            'target_market': 'المزارع والمنشآت الصناعية والمنازل',
            'business_model': 'بيع الأجهزة مع خدمات الصيانة الدورية واشتراكات المراقبة',
            'is_public_in_directory': True,
            'terms': True
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        project = InnovationProject.query.filter_by(title='نظام الطاقة الشمسية الذكي').first()
        self.assertIsNotNone(project)
        self.assertEqual(project.status, 'submitted')
        self.assertEqual(project.user_id, self.user.id)

        # خروج والدخول كمدير/مراجع لتقييم المشروع
        self.client.get('/auth/logout')
        self.login_user('admin@test.ly', 'AdminSecret123!')

        review_res = self.client.post(f'/admin/projects/{project.id}/review', data={
            'score_innovation': 24,
            'score_feasibility': 22,
            'score_market_impact': 23,
            'score_team': 21,
            'recommendation': 'accept',
            'status': 'accepted',
            'internal_notes': 'مشروع واعد جداً ولديه نموذج أولي جاهز للاختبار الميداني.',
            'applicant_feedback': 'تهانينا! تم قبول مشروعك وسيتواصل معك منسق الحاضنة لتحديد موعد توقيع اتفاقية الاحتضان.'
        }, follow_redirects=True)
        self.assertEqual(review_res.status_code, 200)

        # التحقق من تحديث حالة المشروع في قاعدة البيانات
        db.session.refresh(project)
        self.assertEqual(project.status, 'accepted')
        self.assertEqual(project.reviews[0].total_score, 90)

    def test_data_driven_settings(self):
        """4. اختبار معمارية البيانات وقابلية تعديل الإعدادات والشعار من لوحة الإدارة"""
        self.login_user('admin@test.ly', 'AdminSecret123!')
        
        # تعيين إعداد
        SiteSetting.set_value('site_name', 'الجمعية الليبية للابتكار والتكنولوجيا')
        self.assertEqual(SiteSetting.get_value('site_name'), 'الجمعية الليبية للابتكار والتكنولوجيا')

        # اختبار ظهور الاسم المحدث في الصفحة الرئيسية
        res = self.client.get('/')
        self.assertIn('الجمعية الليبية للابتكار والتكنولوجيا'.encode('utf-8'), res.data)

    def test_directory_removed_and_redirects(self):
        """5. اختبار إزالة دليل الابتكار وإعادة توجيه مساراته إلى الرئيسية"""
        res = self.client.get('/directory')
        self.assertEqual(res.status_code, 302)
        res_followed = self.client.get('/directory', follow_redirects=True)
        self.assertEqual(res_followed.status_code, 200)

    def test_networking_matchmaking(self):
        """6. اختبار طلبات التشبيك والتوجيه والإرشاد"""
        self.login_user('innovator@test.ly', 'Secret123!')

        req_res = self.client.post(f'/networking/connect/{self.admin.id}', data={
            'request_type': 'mentorship',
            'subject': 'طلب جلسة إرشاد بخصوص نموذج العمل',
            'message': 'أرغب في الحصول على توجيه بخصوص استراتيجية التسعير.',
            'sender_contact_email': 'innovator@test.ly',
            'sender_contact_phone': '0911111111'
        }, follow_redirects=True)
        self.assertEqual(req_res.status_code, 200)

        req = NetworkingRequest.query.filter_by(sender_id=self.user.id, recipient_id=self.admin.id).first()
        self.assertIsNotNone(req)
        self.assertEqual(req.status, 'pending')

        # الطرف الآخر يقبل الطلب
        self.client.get('/auth/logout')
        self.login_user('admin@test.ly', 'AdminSecret123!')

        accept_res = self.client.post(f'/dashboard/networking/{req.id}/respond', data={
            'action': 'accept',
            'response_note': 'موافق، يسعدني التوجيه. نلتقي يوم الأربعاء القادم.'
        }, follow_redirects=True)
        self.assertEqual(accept_res.status_code, 200)

        db.session.refresh(req)
        self.assertEqual(req.status, 'accepted')
        self.assertEqual(req.response_note, 'موافق، يسعدني التوجيه. نلتقي يوم الأربعاء القادم.')

    def test_course_and_opportunity_workflows(self):
        """7. اختبار الالتحاق بالدورات التدريبية والتقديم على المنح"""
        # إنشاء دورة تدريبية
        course = TrainingCourse(
            title='معسكر ريادة الأعمال الشامل',
            slug='comprehensive-entrepreneurship-bootcamp',
            trainer_name='د. خبير تدريب',
            summary='معسكر تدريبي مكثف',
            description='شرح تفصيلي للمعسكر',
            start_date=datetime.utcnow() + timedelta(days=5),
            duration_hours=20,
            max_seats=2,
            enrolled_count=0
        )
        # إنشاء فرصة منحة
        opp = Opportunity(
            title='منحة الابتكار التقني',
            slug='tech-innovation-grant',
            provider_name='الجمعية الليبية للابتكار',
            summary='منحة لدعم الحلول التقنية',
            description='تفاصيل المنحة وشروطها',
            deadline=datetime.utcnow() + timedelta(days=30),
            status='open',
            allow_internal_apply=True
        )
        db.session.add_all([course, opp])
        db.session.commit()

        # تسجيل المستخدم في الدورة
        self.login_user('innovator@test.ly', 'Secret123!')
        res_course = self.client.post(f'/training/{course.slug}', data={
            'full_name': 'مبتكر ليبي',
            'email': 'innovator@test.ly',
            'phone': '0911111111',
            'motivation': 'تطوير مشروعي واكتساب مهارات الإدارة والتسويق'
        }, follow_redirects=True)
        self.assertEqual(res_course.status_code, 200)

        enrollment = CourseEnrollment.query.filter_by(course_id=course.id, user_id=self.user.id).first()
        self.assertIsNotNone(enrollment)
        self.assertEqual(enrollment.status, 'confirmed')

        # التقديم على المنحة
        res_opp = self.client.post(f'/opportunities/{opp.slug}', data={
            'applicant_name': 'مبتكر ليبي',
            'applicant_email': 'innovator@test.ly',
            'applicant_phone': '0911111111',
            'proposal_summary': 'مقترح شامل لتطوير حل برمجيات وطني للقطاع الصحي'
        }, follow_redirects=True)
        self.assertEqual(res_opp.status_code, 200)

    def test_public_pages_and_accessibility(self):
        """8. اختبار الوصول إلى الصفحات العامة وسرعة الاستجابة"""
        routes_to_test = [
            '/',
            '/about',
            '/services',
            '/programs',
            '/opportunities',
            '/training',
            '/news',
            '/events',
            '/contact'
        ]
        for route in routes_to_test:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")

    def test_capacity_limit_course_and_event(self):
        """9. اختبار الربط الدقيق للطاقة الاستيعابية ورسالة اكتمال العدد في البرامج والفعاليات"""
        # 1. إنشاء دورة بسعة مقعد واحد فقط
        course = TrainingCourse(
            title='دورة نمذجة الأعمال المحدودة',
            slug='limited-business-course',
            trainer_name='المدرب الأول',
            summary='دورة تدريبية مخصصة لعدد محدود',
            description='تفاصيل دورة النمذجة',
            start_date=datetime.utcnow() + timedelta(days=3),
            max_seats=1,
            enrolled_count=0,
            registration_status='open',
            is_active=True
        )
        db.session.add(course)
        db.session.commit()

        # تسجيل المستخدم الأول (يجب أن ينجح)
        self.login_user('innovator@test.ly', 'Secret123!')
        res1 = self.client.post(f'/training/{course.slug}', data={
            'full_name': 'مبتكر ليبي',
            'email': 'innovator@test.ly',
            'phone': '0911111111',
            'motivation': 'الرغبة في التعلم'
        }, follow_redirects=True)
        self.assertEqual(res1.status_code, 200)

        # التحقق من أن المقعد حجز بنجاح وأن حالة التسجيل بالدورة أغلقت
        course = db.session.get(TrainingCourse, course.id)
        self.assertEqual(course.enrolled_count, 1)
        self.assertEqual(course.registration_status, 'closed')

        # إنشاء مستخدم ثانٍ ومحاولة التسجيل في نفس الدورة المكتملة
        user2 = User(
            email='second_user@test.ly',
            full_name='مستخدم ثانٍ',
            phone='0922222221',
            city='طرابلس',
            account_type='innovator',
            is_active=True
        )
        user2.set_password('Password123!')
        db.session.add(user2)
        db.session.commit()

        self.login_user('second_user@test.ly', 'Password123!')
        res2 = self.client.post(f'/training/{course.slug}', data={
            'full_name': 'مستخدم ثانٍ',
            'email': 'second_user@test.ly',
            'phone': '0922222221',
            'motivation': 'أرغب بالانضمام'
        }, follow_redirects=True)
        self.assertEqual(res2.status_code, 200)
        # التحقق من ظهور رسالة اكتمال العدد وعدم زيادة المسجلين
        self.assertIn('اكتمل العدد'.encode('utf-8'), res2.data)
        self.assertEqual(CourseEnrollment.query.filter_by(course_id=course.id).count(), 1)

    def test_admin_actions_and_csv_reports_export(self):
        """10. اختبار عمليات لوحة الإدارة (تعديل، تفعيل/تعطيل، حذف) وتصدير التقارير بـ UTF-8 BOM"""
        from app.models import Event, EventRegistration

        # إنشاء دورة وفعالية وفرصة للتجربة
        course = TrainingCourse(
            title='دورة إدارة المشاريع',
            slug='pm-course-test',
            trainer_name='المدرب التجريبي',
            summary='ملخص الدورة',
            description='وصف الدورة',
            start_date=datetime.utcnow() + timedelta(days=2),
            max_seats=20,
            enrolled_count=0,
            is_active=True
        )
        event = Event(
            title='مؤتمر الابتكار السنوي',
            slug='annual-innovation-conference',
            summary='مؤتمر وطني سنوي',
            description='تفاصيل المؤتمر وجلساته',
            start_time=datetime.utcnow() + timedelta(days=10),
            capacity=50,
            registered_count=0,
            is_published=True,
            is_registration_open=True
        )
        opp = Opportunity(
            title='جائزة المبتكر الليبي 2026',
            slug='libyan-innovator-award',
            provider_name='الجمعية الليبية للابتكار',
            summary='جائزة سنوية',
            description='تفاصيل الجائزة',
            deadline=datetime.utcnow() + timedelta(days=40),
            is_active=True
        )
        db.session.add_all([course, event, opp])
        db.session.commit()

        # تسجيل الدخول كمدير
        self.login_user('admin@test.ly', 'AdminSecret123!')

        # 1. اختبار تفعيل / تعطيل الدورة التدريبية
        res_toggle_course = self.client.post(f'/admin/training/{course.id}/toggle-active', follow_redirects=True)
        self.assertEqual(res_toggle_course.status_code, 200)
        course = db.session.get(TrainingCourse, course.id)
        self.assertFalse(course.is_active)

        # 2. اختبار تفعيل / تعطيل الفعالية
        res_toggle_event = self.client.post(f'/admin/events/{event.id}/toggle-active', follow_redirects=True)
        self.assertEqual(res_toggle_event.status_code, 200)
        event = db.session.get(Event, event.id)
        self.assertFalse(event.is_published)

        # 3. اختبار تفعيل / تعطيل الفرصة
        res_toggle_opp = self.client.post(f'/admin/opportunities/{opp.id}/toggle-active', follow_redirects=True)
        self.assertEqual(res_toggle_opp.status_code, 200)
        opp = db.session.get(Opportunity, opp.id)
        self.assertFalse(opp.is_active)

        # 4. اختبار صفحة مركز التقارير
        res_reports = self.client.get('/admin/reports')
        self.assertEqual(res_reports.status_code, 200)

        # 5. اختبار تصدير كافة التقارير السبعة بصيغة Microsoft Excel (.xlsx) الاحترافية
        report_types = ['enrollments', 'event_registrations', 'applications', 'projects', 'users', 'startups', 'audit_logs']
        for rtype in report_types:
            res_export = self.client.get(f'/admin/reports/export/{rtype}')
            self.assertEqual(res_export.status_code, 200, f"Report {rtype} failed with status {res_export.status_code}")
            self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', res_export.content_type)
            # التحقق من أن الملف يبدأ بـ PK\x03\x04 (توقيع ملفات Excel .xlsx الحقيقية)
            self.assertTrue(res_export.data.startswith(b'PK\x03\x04'))
            # التحقق من خلو اسم الملف في الترويسة من أي محارف غير متوافقة مع Latin-1
            disp = res_export.headers.get('Content-Disposition')
            self.assertIsNotNone(disp)
            disp.encode('latin-1') # يجب ألا يلقي خطأ UnicodeEncodeError

        # 6. اختبار تصدير مسجلي دورة محددة كملف Excel (.xlsx)
        res_course_excel = self.client.get(f'/admin/training/{course.id}/export-enrollments')
        self.assertEqual(res_course_excel.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', res_course_excel.content_type)
        self.assertTrue(res_course_excel.data.startswith(b'PK\x03\x04'))
        res_course_excel.headers.get('Content-Disposition').encode('latin-1')

        # 7. اختبار تصدير مسجلي فعالية محددة كملف Excel (.xlsx)
        res_event_excel = self.client.get(f'/admin/events/{event.id}/export-registrations')
        self.assertEqual(res_event_excel.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', res_event_excel.content_type)
        self.assertTrue(res_event_excel.data.startswith(b'PK\x03\x04'))
        res_event_excel.headers.get('Content-Disposition').encode('latin-1')

        # 8. اختبار تصدير متقدمي فرصة محددة كملف Excel (.xlsx)
        res_opp_excel = self.client.get(f'/admin/opportunities/{opp.id}/export-applications')
        self.assertEqual(res_opp_excel.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', res_opp_excel.content_type)
        self.assertTrue(res_opp_excel.data.startswith(b'PK\x03\x04'))
        res_opp_excel.headers.get('Content-Disposition').encode('latin-1')

    def test_community_registration_with_cv_and_admin_confirmation(self):
        """11. اختبار التسجيل بمجتمع الابتكار بالوظيفة الحالية ورفع السيرة الذاتية والنشاطات السابقة، وتأكيد التسجيل من قبل الأدمن وإرسال البريد"""
        # تسجيل عضو جديد مع رفع ملف السيرة الذاتية وإدخال الوظيفة الحالية والنشاطات السابقة
        cv_content = b"%PDF-1.4 Mock CV Content for Libyan Innovator"
        data = {
            'full_name': 'مبتكر ومخترع ليبي',
            'email': 'innovator_candidate@test.ly',
            'phone': '0944444444',
            'city': 'غريان',
            'account_type': 'innovator',
            'current_job': 'باحث في الذكاء الاصطناعي والطاقة المتجددة',
            'previous_activities': 'الفوز بالمركز الأول في مسابقة الابتكار الوطني لعام 2025 وتطوير براءة اختراع.',
            'cv_file': (io.BytesIO(cv_content), 'innovator_cv.pdf'),
            'password': 'SecureCandidate123!',
            'confirm_password': 'SecureCandidate123!',
            'terms': True
        }
        res = self.client.post('/auth/register', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # التحقق من إنشاء المستخدم وحفظ كافة الحقول
        candidate = User.query.filter_by(email='innovator_candidate@test.ly').first()
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.current_job, 'باحث في الذكاء الاصطناعي والطاقة المتجددة')
        self.assertEqual(candidate.headline, 'باحث في الذكاء الاصطناعي والطاقة المتجددة')
        self.assertFalse(candidate.is_approved_member) # لم يُعتمد بعد
        self.assertIsNotNone(candidate.profile)
        self.assertEqual(candidate.profile.previous_activities, 'الفوز بالمركز الأول في مسابقة الابتكار الوطني لعام 2025 وتطوير براءة اختراع.')
        self.assertIsNotNone(candidate.cv_file)
        self.assertTrue(candidate.cv_file.endswith('.pdf'))

        # محاولة تأكيد التسجيل من مستخدم عادي غير مصرح له (يجب أن يُرفض 403)
        self.login_user('innovator@test.ly', 'Secret123!')
        res_unauth = self.client.post(f'/admin/users/{candidate.id}/confirm-registration')
        self.assertEqual(res_unauth.status_code, 403)

        # تسجيل الخروج ثم تسجيل الدخول كأدمن رئيسي لتأكيد واعتماد التسجيل
        self.client.get('/auth/logout', follow_redirects=True)
        self.login_user('admin@test.ly', 'AdminSecret123!')
        
        # التأكد من إظهار المستخدم في قائمة بانتظار التأكيد
        res_pending_list = self.client.get('/admin/users?status=pending')
        self.assertEqual(res_pending_list.status_code, 200)
        self.assertIn('innovator_candidate@test.ly', res_pending_list.get_data(as_text=True))

        # تأكيد واعتماد التسجيل
        res_confirm = self.client.post(f'/admin/users/{candidate.id}/confirm-registration', follow_redirects=True)
        self.assertEqual(res_confirm.status_code, 200)

        # التحقق من تغيير حالة الحساب إلى معتمد
        db.session.refresh(candidate)
        self.assertTrue(candidate.is_approved_member)
        self.assertTrue(candidate.is_verified)
        self.assertTrue(candidate.is_active)


if __name__ == '__main__':
    unittest.main()
