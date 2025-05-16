from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models.user import User, UserRole
from extensions import db, bcrypt
import os
from forms.auth import LoginForm, ChangePasswordForm, RegisterForm, ProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('登录成功！', 'success')
            return redirect(next_page if next_page else url_for('main.index'))
        else:
            flash('登录失败，请检查邮箱和密码', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已被使用', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('邮箱已被注册', 'danger')
            return render_template('auth/register.html', form=form)
        
        # 创建新用户
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=form.role.data,
            phone=form.phone.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    
    if form.validate_on_submit():
        # 检查用户名是否已被其他用户使用
        user_check = User.query.filter_by(username=form.username.data).first()
        if user_check and user_check.id != current_user.id:
            flash('用户名已被使用', 'danger')
            return render_template('auth/profile.html', form=form)
        
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        
        # 处理头像上传
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            # 生成唯一文件名
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"user_{current_user.id}{file_ext}"
            
            # 保存文件
            avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
            os.makedirs(avatar_path, exist_ok=True)
            file_path = os.path.join(avatar_path, unique_filename)
            form.avatar.data.save(file_path)
            
            # 更新用户头像路径
            current_user.avatar = f"uploads/avatars/{unique_filename}"
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 验证密码长度
        if len(form.new_password.data) < 6:
            flash('新密码长度不能少于6个字符', 'danger')
            return render_template('auth/change_password.html', form=form)
        
        # 验证确认密码
        if form.new_password.data != form.confirm_password.data:
            flash('两次输入的密码不一致', 'danger')
            return render_template('auth/change_password.html', form=form)

        current_user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        
        db.session.commit()
        flash('密码已成功更改', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html', form=form)