from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.payment import Payment, PaymentStatus, PaymentType
from models.lease import Lease
from models.property import Property
from models.user import User, UserRole
from extensions import db
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/tenant')
@login_required
def tenant_payments():
    # 租客查看自己的支付记录
    if current_user.role != UserRole.TENANT:
        flash('只有租客可以访问此页面', 'warning')
        return redirect(url_for('main.index'))
    
    payments = Payment.query.filter_by(payer_id=current_user.id).order_by(Payment.due_date.desc()).all()
    
    # 获取每个支付记录对应的租约和房源信息
    payment_data = []
    for payment in payments:
        lease = Lease.query.get(payment.lease_id)
        property_item = Property.query.get(lease.property_id)
        landlord = User.query.get(lease.landlord_id)
        payment_data.append({
            'payment': payment,
            'lease': lease,
            'property': property_item,
            'landlord': landlord
        })
    
    return render_template('payment/tenant_payments.html', payment_data=payment_data)

@payment_bp.route('/landlord')
@login_required
def landlord_payments():
    # 房东查看自己房源的支付记录
    if current_user.role != UserRole.LANDLORD:
        flash('只有房东可以访问此页面', 'warning')
        return redirect(url_for('main.index'))
    
    # 获取房东的所有租约ID
    lease_ids = [l.id for l in Lease.query.filter_by(landlord_id=current_user.id).all()]
    
    # 获取这些租约的所有支付记录
    payments = Payment.query.filter(Payment.lease_id.in_(lease_ids)).order_by(Payment.due_date.desc()).all()
    
    # 获取每个支付记录对应的租约和租客信息
    payment_data = []
    for payment in payments:
        lease = Lease.query.get(payment.lease_id)
        property_item = Property.query.get(lease.property_id)
        tenant = User.query.get(payment.payer_id)
        payment_data.append({
            'payment': payment,
            'lease': lease,
            'property': property_item,
            'tenant': tenant
        })
    
    return render_template('payment/landlord_payments.html', payment_data=payment_data)

@payment_bp.route('/pay/<int:payment_id>', methods=['POST'])
@login_required
def pay(payment_id):
    # 租客支付租金或押金
    payment = Payment.query.get_or_404(payment_id)
    
    # 验证是否为支付人
    if payment.payer_id != current_user.id:
        flash('您无权进行此支付', 'danger')
        return redirect(url_for('payment.tenant_payments'))
    
    # 验证支付状态
    if payment.status != PaymentStatus.PENDING and payment.status != PaymentStatus.OVERDUE:
        flash('此支付已处理，无需重复支付', 'warning')
        return redirect(url_for('payment.tenant_payments'))
    
    # 模拟支付过程（实际应用中应集成支付网关）
    payment.status = PaymentStatus.PAID
    payment.payment_date = datetime.utcnow()
    payment.payment_method = '在线支付'  # 可根据实际支付方式修改
    payment.transaction_id = f'TX{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
    
    db.session.commit()
    
    # 如果是押金支付，检查是否需要更新租约状态
    if payment.payment_type == PaymentType.DEPOSIT:
        lease = Lease.query.get(payment.lease_id)
        # 检查是否所有初始支付（押金和首月租金）都已支付
        initial_payments = Payment.query.filter_by(
            lease_id=lease.id,
            due_date=lease.start_date
        ).all()
        
        all_paid = all(p.status == PaymentStatus.PAID for p in initial_payments)
        if all_paid and lease.status == 'active':
            # 可以在这里添加额外的租约激活逻辑
            pass
    
    flash('支付成功！', 'success')
    return redirect(url_for('payment.tenant_payments'))

@payment_bp.route('/mark-paid/<int:payment_id>', methods=['POST'])
@login_required
def mark_paid(payment_id):
    # 房东标记支付为已收到（线下支付情况）
    payment = Payment.query.get_or_404(payment_id)
    lease = Lease.query.get(payment.lease_id)
    
    # 验证是否为房东
    if lease.landlord_id != current_user.id:
        flash('您无权操作此支付记录', 'danger')
        return redirect(url_for('payment.landlord_payments'))
    
    # 验证支付状态
    if payment.status == PaymentStatus.PAID:
        flash('此支付已标记为已支付', 'warning')
        return redirect(url_for('payment.landlord_payments'))
    
    # 更新支付状态
    payment.status = PaymentStatus.PAID
    payment.payment_date = datetime.utcnow()
    payment.payment_method = '线下支付'  # 标记为线下支付
    payment.transaction_id = f'OFFLINE-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'
    
    db.session.commit()
    
    flash('支付已标记为已收到', 'success')
    return redirect(url_for('payment.landlord_payments'))

@payment_bp.route('/refund/<int:payment_id>', methods=['POST'])
@login_required
def refund_payment(payment_id):
    # 房东退款
    payment = Payment.query.get_or_404(payment_id)
    lease = Lease.query.get(payment.lease_id)
    
    # 验证是否为房东
    if lease.landlord_id != current_user.id:
        flash('您无权操作此支付记录', 'danger')
        return redirect(url_for('payment.landlord_payments'))
    
    # 验证支付状态
    if payment.status != PaymentStatus.PAID:
        flash('只能退还已支付的款项', 'warning')
        return redirect(url_for('payment.landlord_payments'))
    
    # 更新支付状态
    payment.status = PaymentStatus.REFUNDED
    
    db.session.commit()
    
    flash('退款已处理', 'success')
    return redirect(url_for('payment.landlord_payments'))

@payment_bp.route('/mark-overdue')
@login_required
def mark_overdue_payments():
    # 系统功能：标记逾期支付（实际应用中应由定时任务执行）
    if current_user.role != UserRole.LANDLORD:
        flash('只有房东可以执行此操作', 'warning')
        return redirect(url_for('main.index'))
    
    # 获取所有逾期但未支付的记录
    overdue_payments = Payment.query.filter_by(status=PaymentStatus.PENDING)\
        .filter(Payment.due_date < datetime.utcnow().date()).all()
    
    # 更新状态为逾期
    for payment in overdue_payments:
        payment.status = PaymentStatus.OVERDUE
    
    db.session.commit()
    
    flash(f'已标记 {len(overdue_payments)} 笔逾期支付', 'success')
    return redirect(url_for('payment.landlord_payments'))

@payment_bp.route('/receipt/<int:payment_id>')
@login_required
def view_receipt(payment_id):
    # 查看支付凭证
    payment = Payment.query.get_or_404(payment_id)
    lease = Lease.query.get(payment.lease_id)
    
    # 验证是否为支付相关方
    if payment.payer_id != current_user.id and lease.landlord_id != current_user.id:
        flash('您无权查看此支付凭证', 'danger')
        return redirect(url_for('main.index'))
    
    # 验证支付状态
    if payment.status != PaymentStatus.PAID and payment.status != PaymentStatus.REFUNDED:
        flash('只能查看已支付或已退款的凭证', 'warning')
        if current_user.role == UserRole.TENANT:
            return redirect(url_for('payment.tenant_payments'))
        else:
            return redirect(url_for('payment.landlord_payments'))
    
    property_item = Property.query.get(lease.property_id)
    tenant = User.query.get(payment.payer_id)
    landlord = User.query.get(lease.landlord_id)
    
    return render_template('payment/receipt.html', 
                          payment=payment, 
                          lease=lease, 
                          property=property_item, 
                          tenant=tenant, 
                          landlord=landlord)