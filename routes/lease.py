from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models.lease import Lease, LeaseStatus
from models.property import Property, PropertyStatus
from models.user import User, UserRole
from models.payment import Payment, PaymentType, PaymentStatus
from extensions import db
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from forms.lease import LeaseForm
import calendar

lease_bp = Blueprint('lease', __name__)

@lease_bp.route('/create/<int:property_id>', methods=['GET', 'POST'])
@login_required
def create_lease(property_id):
    # 房东创建租赁合同
    property_item = Property.query.get_or_404(property_id)
    
    # 验证是否为房源所有者
    if property_item.owner_id != current_user.id:
        flash('您无权为此房源创建合同', 'danger')
        return redirect(url_for('property.property_list'))
    
    # 检查房源是否已有活跃的租约
    active_lease = Lease.query.filter_by(
        property_id=property_id,
        status=LeaseStatus.ACTIVE
    ).first()
    
    if active_lease:
        flash('此房源已有活跃的租约，无法创建新合同', 'warning')
        return redirect(url_for('lease.landlord_leases'))
    
    form = LeaseForm()
    
    # 获取所有租客用户列表供选择
    tenants = User.query.filter_by(role=UserRole.TENANT).all()
    form.tenant_id.choices = [(t.id, t.username) for t in tenants]
    
    if form.validate_on_submit():
        # 创建新租约
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # 验证租期
        if start_date >= end_date:
            flash('租期结束日期必须晚于开始日期', 'danger')
            return render_template('lease/create.html', form=form, property=property_item)
        
        # 计算租期月数
        lease_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
        if lease_months < property_item.min_lease_months:
            flash(f'租期不能少于{property_item.min_lease_months}个月', 'danger')
            return render_template('lease/create.html', form=form, property=property_item)
        
        # 创建租约
        new_lease = Lease(
            property_id=property_id,
            tenant_id=form.tenant_id.data,
            landlord_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            monthly_rent=form.monthly_rent.data,
            deposit_amount=form.deposit_amount.data,
            payment_day=form.payment_day.data,
            terms=form.terms.data,
            status=LeaseStatus.DRAFT
        )
        
        db.session.add(new_lease)
        db.session.commit()
        
        # 创建押金支付记录
        deposit_payment = Payment(
            lease_id=new_lease.id,
            payer_id=form.tenant_id.data,
            amount=form.deposit_amount.data,
            payment_type=PaymentType.DEPOSIT,
            description='租赁押金',
            due_date=start_date,
            status=PaymentStatus.PENDING
        )
        
        db.session.add(deposit_payment)
        
        # 创建首月租金支付记录
        first_rent_payment = Payment(
            lease_id=new_lease.id,
            payer_id=form.tenant_id.data,
            amount=form.monthly_rent.data,
            payment_type=PaymentType.RENT,
            description=f'{start_date.year}年{start_date.month}月租金',
            due_date=start_date,
            status=PaymentStatus.PENDING
        )
        
        db.session.add(first_rent_payment)
        db.session.commit()
        
        flash('租赁合同已创建，等待租客签署', 'success')
        return redirect(url_for('lease.landlord_leases'))
    
    # 默认值
    form.monthly_rent.data = property_item.price
    form.deposit_amount.data = property_item.deposit or property_item.price * 2  # 默认押金为两个月租金
    form.payment_day.data = 5  # 默认每月5号付款
    
    return render_template('lease/create.html', form=form, property=property_item)

@lease_bp.route('/tenant')
@login_required
def tenant_leases():
    # 租客查看自己的租约
    if current_user.role != UserRole.TENANT:
        flash('只有租客可以访问此页面', 'warning')
        return redirect(url_for('main.index'))
    
    leases = Lease.query.filter_by(tenant_id=current_user.id).all()
    
    # 获取每个租约对应的房源和房东信息
    lease_data = []
    for lease in leases:
        property_item = Property.query.get(lease.property_id)
        landlord = User.query.get(lease.landlord_id)
        lease_data.append({
            'lease': lease,
            'property': property_item,
            'landlord': landlord
        })
    
    return render_template('lease/tenant_leases.html', lease_data=lease_data)

@lease_bp.route('/landlord')
@login_required
def landlord_leases():
    # 房东查看自己的租约
    if current_user.role != UserRole.LANDLORD:
        flash('只有房东可以访问此页面', 'warning')
        return redirect(url_for('main.index'))
    
    leases = Lease.query.filter_by(landlord_id=current_user.id).all()
    
    # 获取每个租约对应的房源和租客信息
    lease_data = []
    for lease in leases:
        property_item = Property.query.get(lease.property_id)
        tenant = User.query.get(lease.tenant_id)
        lease_data.append({
            'lease': lease,
            'property': property_item,
            'tenant': tenant
        })
    
    return render_template('lease/landlord_leases.html', lease_data=lease_data)

@lease_bp.route('/view/<int:lease_id>')
@login_required
def view_lease(lease_id):
    # 查看租约详情
    lease = Lease.query.get_or_404(lease_id)
    
    # 验证是否为租约相关方
    if lease.tenant_id != current_user.id and lease.landlord_id != current_user.id:
        flash('您无权查看此租约', 'danger')
        return redirect(url_for('main.index'))
    
    property_item = Property.query.get(lease.property_id)
    tenant = User.query.get(lease.tenant_id)
    landlord = User.query.get(lease.landlord_id)
    
    # 获取租约相关的支付记录
    payments = Payment.query.filter_by(lease_id=lease_id).order_by(Payment.due_date).all()
    
    return render_template('lease/view.html', 
                          lease=lease, 
                          property=property_item, 
                          tenant=tenant, 
                          landlord=landlord,
                          payments=payments)

@lease_bp.route('/sign/<int:lease_id>', methods=['POST'])
@login_required
def sign_lease(lease_id):
    # 签署租约
    lease = Lease.query.get_or_404(lease_id)
    
    # 验证是否为租约相关方
    if lease.tenant_id != current_user.id and lease.landlord_id != current_user.id:
        flash('您无权签署此租约', 'danger')
        return redirect(url_for('main.index'))
    
    # 根据用户角色更新签署状态
    if current_user.id == lease.tenant_id and not lease.tenant_signed:
        lease.tenant_signed = True
        lease.tenant_signed_at = datetime.utcnow()
        flash('您已成功签署租约', 'success')
    elif current_user.id == lease.landlord_id and not lease.landlord_signed:
        lease.landlord_signed = True
        lease.landlord_signed_at = datetime.utcnow()
        flash('您已成功签署租约', 'success')
    else:
        flash('您已经签署过此租约', 'info')
        return redirect(url_for('lease.view_lease', lease_id=lease_id))
    
    # 检查是否双方都已签署
    if lease.tenant_signed and lease.landlord_signed:
        lease.status = LeaseStatus.ACTIVE
        
        # 更新房源状态为已租
        property_item = Property.query.get(lease.property_id)
        property_item.status = PropertyStatus.RENTED
        
        # 生成租期内的所有月租支付记录
        start_date = lease.start_date
        end_date = lease.end_date
        current_date = start_date
        
        # 跳过第一个月（已在创建租约时生成）
        current_date = current_date + relativedelta(months=1)
        
        while current_date < end_date:
            # 确定每月的付款日期
            payment_date = date(current_date.year, current_date.month, lease.payment_day)
            
            # 如果付款日大于当月天数，则使用当月最后一天
            month_days = calendar.monthrange(current_date.year, current_date.month)[1]
            if lease.payment_day > month_days:
                payment_date = date(current_date.year, current_date.month, month_days)
            
            # 创建租金支付记录
            rent_payment = Payment(
                lease_id=lease.id,
                payer_id=lease.tenant_id,
                amount=lease.monthly_rent,
                payment_type=PaymentType.RENT,
                description=f'{current_date.year}年{current_date.month}月租金',
                due_date=payment_date,
                status=PaymentStatus.PENDING
            )
            
            db.session.add(rent_payment)
            
            # 移到下一个月
            current_date = current_date + relativedelta(months=1)
    
    db.session.commit()
    
    return redirect(url_for('lease.view_lease', lease_id=lease_id))

@lease_bp.route('/terminate/<int:lease_id>', methods=['POST'])
@login_required
def terminate_lease(lease_id):
    # 终止租约
    lease = Lease.query.get_or_404(lease_id)
    
    # 验证是否为房东
    if lease.landlord_id != current_user.id:
        flash('只有房东可以终止租约', 'danger')
        return redirect(url_for('lease.view_lease', lease_id=lease_id))
    
    # 更新租约状态
    lease.status = LeaseStatus.TERMINATED
    
    # 更新房源状态为可用
    property_item = Property.query.get(lease.property_id)
    property_item.status = PropertyStatus.AVAILABLE
    
    # 取消未支付的租金
    future_payments = Payment.query.filter_by(
        lease_id=lease_id,
        status=PaymentStatus.PENDING,
        payment_type=PaymentType.RENT
    ).filter(Payment.due_date > date.today()).all()
    
    for payment in future_payments:
        payment.status = PaymentStatus.CANCELLED
    
    db.session.commit()
    
    flash('租约已终止', 'success')
    return redirect(url_for('lease.landlord_leases'))

@lease_bp.route('/renew/<int:lease_id>', methods=['GET', 'POST'])
@login_required
def renew_lease(lease_id):
    # 续签租约
    lease = Lease.query.get_or_404(lease_id)
    
    # 验证是否为房东
    if lease.landlord_id != current_user.id:
        flash('只有房东可以续签租约', 'danger')
        return redirect(url_for('lease.view_lease', lease_id=lease_id))
    
    # 验证租约是否处于活跃状态
    if lease.status != LeaseStatus.ACTIVE:
        flash('只能续签活跃状态的租约', 'warning')
        return redirect(url_for('lease.view_lease', lease_id=lease_id))
    
    property_item = Property.query.get(lease.property_id)
    
    form = LeaseForm()
    
    # 隐藏租客选择字段，续约使用相同租客
    form.tenant_id.choices = [(lease.tenant_id, User.query.get(lease.tenant_id).username)]
    
    if request.method == 'GET':
        # 填充表单默认值
        form.tenant_id.data = lease.tenant_id
        form.monthly_rent.data = lease.monthly_rent
        form.deposit_amount.data = lease.deposit_amount
        form.payment_day.data = lease.payment_day
        form.terms.data = lease.terms
        
        # 默认新租期从旧租期结束后开始
        form.start_date.data = lease.end_date + timedelta(days=1)
        form.end_date.data = form.start_date.data + relativedelta(months=12)  # 默认续签12个月
    
    if form.validate_on_submit():
        # 创建新租约
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # 验证租期
        if start_date >= end_date:
            flash('租期结束日期必须晚于开始日期', 'danger')
            return render_template('lease/renew.html', form=form, lease=lease, property=property_item)
        
        # 计算租期月数
        lease_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
        if lease_months < property_item.min_lease_months:
            flash(f'租期不能少于{property_item.min_lease_months}个月', 'danger')
            return render_template('lease/renew.html', form=form, lease=lease, property=property_item)
        
        # 标记旧租约为已续签
        lease.status = LeaseStatus.RENEWED
        
        # 创建新租约
        new_lease = Lease(
            property_id=lease.property_id,
            tenant_id=lease.tenant_id,
            landlord_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            monthly_rent=form.monthly_rent.data,
            deposit_amount=form.deposit_amount.data,
            payment_day=form.payment_day.data,
            terms=form.terms.data,
            status=LeaseStatus.DRAFT
        )
        
        db.session.add(new_lease)
        db.session.commit()
        
        # 创建首月租金支付记录
        first_rent_payment = Payment(
            lease_id=new_lease.id,
            payer_id=lease.tenant_id,
            amount=form.monthly_rent.data,
            payment_type=PaymentType.RENT,
            description=f'{start_date.year}年{start_date.month}月租金',
            due_date=start_date,
            status=PaymentStatus.PENDING
        )
        
        db.session.add(first_rent_payment)
        db.session.commit()
        
        flash('租约续签已创建，等待双方签署', 'success')
        return redirect(url_for('lease.landlord_leases'))
    
    return render_template('lease/renew.html', form=form, lease=lease, property=property_item)