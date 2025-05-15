from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.notification import Notification
from extensions import db

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/list')
@login_required
def notification_list():
    """显示用户的所有通知"""
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()
    
    # 计算未读通知数量
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('notification/list.html', 
                          notifications=notifications,
                          unread_count=unread_count)

@notification_bp.route('/mark_read/<int:notification_id>')
@login_required
def mark_read(notification_id):
    """标记单个通知为已读"""
    notification = Notification.query.get_or_404(notification_id)
    
    # 验证通知所属用户
    if notification.user_id != current_user.id:
        flash('您无权访问此通知', 'danger')
        return redirect(url_for('notification.notification_list'))
    
    notification.is_read = True
    db.session.commit()
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    # 否则重定向回通知列表
    return redirect(url_for('notification.notification_list'))

@notification_bp.route('/mark_all_read')
@login_required
def mark_all_read():
    """标记所有通知为已读"""
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    flash('所有通知已标记为已读', 'success')
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    return redirect(url_for('notification.notification_list'))

@notification_bp.route('/delete/<int:notification_id>')
@login_required
def delete_notification(notification_id):
    """删除单个通知"""
    notification = Notification.query.get_or_404(notification_id)
    
    # 验证通知所属用户
    if notification.user_id != current_user.id:
        flash('您无权删除此通知', 'danger')
        return redirect(url_for('notification.notification_list'))
    
    db.session.delete(notification)
    db.session.commit()
    
    flash('通知已删除', 'success')
    return redirect(url_for('notification.notification_list'))

@notification_bp.route('/count')
@login_required
def notification_count():
    """获取未读通知数量（用于AJAX请求）"""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})