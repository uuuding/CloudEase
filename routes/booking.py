from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.booking import Booking, BookingStatus
from models.property import Property, PropertyStatus
from models.user import User, UserRole
from extensions import db
from datetime import datetime, date, time
from forms.booking import BookingForm

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/create/<int:property_id>', methods=['GET', 'POST'])
@login_required
def create_booking(property_id):
    # 租客创建预约看房
    if current_user.role != UserRole.TENANT:
        flash('只有租客可以预约看房', 'warning')
        return redirect(url_for('property.view_property', property_id=property_id))
    
    property_item = Property.query.get_or_404(property_id)
    
    # 检查房源是否可用
    if property_item.status != PropertyStatus.AVAILABLE:
        flash('该房源当前不可预约', 'warning')
        return redirect(url_for('property.view_property', property_id=property_id))
    
    form = BookingForm()
    if form.validate_on_submit():
        # 检查是否已有相同日期和时间的预约
        existing_booking = Booking.query.filter_by(
            property_id=property_id,
            booking_date=form.booking_date.data,
            booking_time=form.booking_time.data,
            status=BookingStatus.CONFIRMED
        ).first()
        
        if existing_booking:
            flash('该时间段已被预约，请选择其他时间', 'warning')
            return render_template('booking/create.html', form=form, property=property_item)
        
        # 创建新预约
        new_booking = Booking(
            property_id=property_id,
            tenant_id=current_user.id,
            booking_date=form.booking_date.data,
            booking_time=form.booking_time.data,
            message=form.message.data,
            status=BookingStatus.PENDING
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        flash('预约申请已提交，等待房东确认', 'success')
        return redirect(url_for('booking.tenant_bookings'))
    
    return render_template('booking/create.html', form=form, property=property_item)

@booking_bp.route('/tenant')
@login_required
def tenant_bookings():
    # 租客查看自己的预约
    if current_user.role != UserRole.TENANT:
        flash('只有租客可以访问此页面', 'warning')
        return redirect(url_for('main.index'))
    
    bookings = Booking.query.filter_by(tenant_id=current_user.id).order_by(Booking.created_at.desc()).all()
    
    # 获取每个预约对应的房源信息
    booking_data = []
    for booking in bookings:
        property_item = Property.query.get(booking.property_id)
        landlord = User.query.get(property_item.owner_id)
        booking_data.append({
            'booking': booking,
            'property': property_item,
            'landlord': landlord
        })
    
    return render_template('booking/tenant_bookings.html', booking_data=booking_data)

@booking_bp.route('/landlord')
@login_required
def landlord_bookings():
    # 房东查看自己房源的预约
    if current_user.role != UserRole.LANDLORD:
        flash('只有房东可以访问此页面', 'warning')
        return redirect(url_for('main.index'))
    
    # 获取房东的所有房源ID
    property_ids = [p.id for p in Property.query.filter_by(owner_id=current_user.id).all()]
    
    # 获取这些房源的所有预约
    bookings = Booking.query.filter(Booking.property_id.in_(property_ids)).order_by(Booking.created_at.desc()).all()
    
    # 获取每个预约对应的房源和租客信息
    booking_data = []
    for booking in bookings:
        property_item = Property.query.get(booking.property_id)
        tenant = User.query.get(booking.tenant_id)
        booking_data.append({
            'booking': booking,
            'property': property_item,
            'tenant': tenant
        })
    
    return render_template('booking/landlord_bookings.html', booking_data=booking_data)

@booking_bp.route('/confirm/<int:booking_id>', methods=['POST'])
@login_required
def confirm_booking(booking_id):
    # 房东确认预约
    booking = Booking.query.get_or_404(booking_id)
    property_item = Property.query.get(booking.property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权确认此预约', 'danger')
        return redirect(url_for('booking.landlord_bookings'))
    
    # 更新预约状态
    booking.status = BookingStatus.CONFIRMED
    db.session.commit()
    
    flash('预约已确认', 'success')
    return redirect(url_for('booking.landlord_bookings'))

@booking_bp.route('/reject/<int:booking_id>', methods=['POST'])
@login_required
def reject_booking(booking_id):
    # 房东拒绝预约
    booking = Booking.query.get_or_404(booking_id)
    property_item = Property.query.get(booking.property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权拒绝此预约', 'danger')
        return redirect(url_for('booking.landlord_bookings'))
    
    # 更新预约状态
    booking.status = BookingStatus.REJECTED
    db.session.commit()
    
    flash('预约已拒绝', 'success')
    return redirect(url_for('booking.landlord_bookings'))

@booking_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    # 租客取消预约
    booking = Booking.query.get_or_404(booking_id)
    
    # 验证是否为预约人
    if booking.tenant_id != current_user.id:
        flash('您无权取消此预约', 'danger')
        return redirect(url_for('booking.tenant_bookings'))
    
    # 更新预约状态
    booking.status = BookingStatus.CANCELLED
    db.session.commit()
    
    flash('预约已取消', 'success')
    return redirect(url_for('booking.tenant_bookings'))

@booking_bp.route('/complete/<int:booking_id>', methods=['POST'])
@login_required
def complete_booking(booking_id):
    # 房东标记预约为已完成
    booking = Booking.query.get_or_404(booking_id)
    property_item = Property.query.get(booking.property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权操作此预约', 'danger')
        return redirect(url_for('booking.landlord_bookings'))
    
    # 更新预约状态
    booking.status = BookingStatus.COMPLETED
    db.session.commit()
    
    flash('预约已标记为已完成', 'success')
    return redirect(url_for('booking.landlord_bookings'))

@booking_bp.route('/feedback/<int:booking_id>', methods=['POST'])
@login_required
def add_feedback(booking_id):
    # 租客添加看房反馈
    booking = Booking.query.get_or_404(booking_id)
    
    # 验证是否为预约人
    if booking.tenant_id != current_user.id:
        flash('您无权为此预约添加反馈', 'danger')
        return redirect(url_for('booking.tenant_bookings'))
    
    # 更新反馈
    feedback = request.form.get('feedback')
    if feedback:
        booking.feedback = feedback
        db.session.commit()
        flash('反馈已提交', 'success')
    else:
        flash('反馈内容不能为空', 'warning')
    
    return redirect(url_for('booking.tenant_bookings'))

@booking_bp.route('/available-times/<int:property_id>/<string:date_str>')
def available_times(property_id, date_str):
    # 获取指定日期可用的预约时间
    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式无效'}), 400
    
    # 获取该日期已确认的预约时间
    booked_times = [b.booking_time.strftime('%H:%M') for b in 
                   Booking.query.filter_by(
                       property_id=property_id,
                       booking_date=booking_date,
                       status=BookingStatus.CONFIRMED
                   ).all()]
    
    # 可用时间段（上午9点到下午6点，每小时一个时间段）
    all_times = [f"{h:02d}:00" for h in range(9, 19)]
    available_times = [t for t in all_times if t not in booked_times]
    
    return jsonify({'available_times': available_times})