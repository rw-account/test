import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from hashlib import sha256

from inventory_management.forms import LoginForm, RegistrationForm
from inventory_management.db import get_db
from .extensions import limiter

bp = Blueprint('auth', __name__, url_prefix='/auth')

from time import sleep
from random import uniform




def get_user_by_username(username):
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    return user

def login_user(user):
    session.clear()
    session['user_id'] = user['id']
    session.permanent = True # جعل جلسة المستخدم تدوم حسب الكونفج ولا تنحذف بعد اغلاق المتصفح


def limit_key():
    # نحظر محاولات التسجيل/تسجيل الدخول الكثيره بناءً على الاي بي والقيمة اللي دخلها في حقل اسم المستخدم
    username = request.form.get("username", "").strip()
    return f"{request.remote_addr}:{username}"

@bp.route('/register', methods=['POST', 'GET'])
@limiter.limit("5 per minute", key_func= limit_key, error_message="لقد تجاوزت الحد. حاول مرة أخرى بعد دقيقة واحدة.", methods=['POST'])
def register():
    form = RegistrationForm() 
    if form.validate_on_submit(): # علشان الحماية من CSRF 
        username = form.username.data.strip()
        password = form.password.data.strip()
        db = get_db()

        user_in_database = get_user_by_username(username)
        if user_in_database:
            form.username.errors.append("تعذر إنشاء الحساب. حاول مرة أخرى.")
            return render_template('auth/register.html', form=form)

        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            db.commit()
            flash('تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'حدث خطأ."{e}"')
            return redirect(url_for('auth.register')) 

    return render_template('auth/register.html', form=form)




@bp.route('/login', methods=['POST', 'GET'])
@limiter.limit("5 per minute", key_func= limit_key, error_message="لقد تجاوزت الحد. حاول مرة أخرى بعد دقيقة واحدة.", methods=['POST'])
def login():
        form = LoginForm() 
        if form.validate_on_submit(): # علشان الحماية من CSRF 
            username = form.username.data.strip()
            password = form.password.data.strip()
            
            user = get_user_by_username(username)
            
            #استخدم رسالة عامة "اسم المستخدم أو كلمة المرور غير صحيحة"
            #لكي لا نكشف أي تفاصيل عن أي منهما (User Enumeration)
            if not user or not check_password_hash(user['password'], password):

                flash('اسم المستخدم أو كلمة المرور غير صحيحة')
                return render_template('auth/login.html', form=form)
        
            else:
                login_user(user)
                return redirect(url_for('index'))

        return render_template('auth/login.html', form=form)




@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view