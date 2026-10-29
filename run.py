import os
import sys
from app import create_app
from app.extensions import db
from app.models import User, Role, UserProfile
from seed import seed_database

env_mode = os.environ.get('FLASK_ENV', 'development')
app = create_app(env_mode)


@app.cli.command("seed-db")
def seed():
    """تهيئة قاعدة البيانات بالبيانات الأولية والإعدادات الرسمية"""
    seed_database()
    print("Database seeding completed.")


@app.cli.command("create-admin")
def create_admin():
    """إنشاء حساب مدير بصورة آمنة وتفاعلية عبر الطرفية"""
    import getpass
    print("\n=== إنشاء حساب مدير نظام جديد (Admin) ===")
    email = input("البريد الإلكتروني: ").strip()
    full_name = input("الاسم الكامل: ").strip()
    password = getpass.getpass("كلمة المرور: ")
    confirm_password = getpass.getpass("تأكيد كلمة المرور: ")
    
    if password != confirm_password:
        print("خطأ: كلمتا المرور غير متطابقتين!")
        sys.exit(1)
        
    with app.app_context():
        if User.query.filter_by(email=email).first():
            print("خطأ: هذا البريد مسجل بالفعل!")
            sys.exit(1)
            
        admin_role = Role.query.filter_by(name='admin').first()
        reviewer_role = Role.query.filter_by(name='reviewer').first()
        editor_role = Role.query.filter_by(name='editor').first()
        
        user = User(
            email=email,
            full_name=full_name,
            account_type='admin',
            is_active=True,
            is_verified=True,
            is_approved_member=True
        )
        user.set_password(password)
        if admin_role:
            user.roles.append(admin_role)
        if reviewer_role:
            user.roles.append(reviewer_role)
        if editor_role:
            user.roles.append(editor_role)
            
        profile = UserProfile(user=user, is_public_in_directory=False)
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        print(f"تم إنشاء حساب المدير '{email}' بنجاح ومنحه كافة الصلاحيات.\n")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
