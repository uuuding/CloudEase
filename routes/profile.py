from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.user import User
from extensions import db, bcrypt
import os
import uuid

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/edit')
@login_required
def edit_profile():
    # 编辑个人资料页面
    return render_template('profile/edit.html')

@profile_bp.route('/update', methods=['POST'])
@login_required
def update_profile():
    # 更新个人资料
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    # 验证用户名和邮箱是否已存在
    if username != current_user.username and User.query.filter_by(username=username).first():
        flash('用户名已被使用', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    if email != current_user.email and User.query.filter_by(email=email).first():
        flash('邮箱已被使用', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    # 更新用户信息
    current_user.username = username
    current_user.email = email
    current_user.phone = phone
    
    # 处理头像上传
    if 'avatar' in request.files and request.files['avatar'].filename:
        avatar_file = request.files['avatar']
        if avatar_file.filename:
            # 生成唯一文件名
            file_ext = os.path.splitext(secure_filename(avatar_file.filename))[1]
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            
            # 确保上传目录存在
            avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(avatar_dir, unique_filename)
            avatar_file.save(file_path)
            
            # 更新用户头像
            current_user.avatar = f"avatars/{unique_filename}"
    
    db.session.commit()
    flash('个人资料已更新', 'success')
    return redirect(url_for('profile.edit_profile'))

@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    # 修改密码
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # 验证当前密码
    if not current_user.check_password(current_password):
        flash('当前密码不正确', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    # 验证新密码
    if new_password != confirm_password:
        flash('两次输入的新密码不一致', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    if len(new_password) < 6:
        flash('新密码长度不能少于6个字符', 'danger')
        return redirect(url_for('profile.edit_profile'))
    
    # 更新密码
    current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    
    flash('密码已成功更改', 'success')
    return redirect(url_for('profile.edit_profile'))