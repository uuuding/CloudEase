import os
from flask import Flask, render_template, redirect, url_for, flash, g
from flask_login import current_user
from dotenv import load_dotenv
from extensions import db, migrate, bcrypt, login_manager

# 加载环境变量
load_dotenv()

# 初始化应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///rental_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化扩展
db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
login_manager.init_app(app)

# 导入并注册蓝图
from routes.main import main_bp
from routes.auth import auth_bp
from routes.property import property_bp
from routes.booking import booking_bp
from routes.lease import lease_bp
from routes.payment import payment_bp
from routes.notification import notification_bp
from routes.review import review_bp
from routes.attractions import attractions_bp
from routes.guides import guides_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(property_bp, url_prefix='/property')
app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(lease_bp, url_prefix='/lease')
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(notification_bp, url_prefix='/notification')
app.register_blueprint(review_bp, url_prefix='/review')
app.register_blueprint(attractions_bp, url_prefix='/attractions')
app.register_blueprint(guides_bp, url_prefix='/guides')

# 上下文处理器 - 添加通知信息到所有模板
@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        from models.notification import Notification
        # 获取未读通知数量
        unread_notifications_count = Notification.query.filter_by(
            user_id=current_user.id, is_read=False).count()
        
        # 获取最近5条通知
        recent_notifications = Notification.query.filter_by(
            user_id=current_user.id).order_by(
            Notification.created_at.desc()).limit(5).all()
        
        return {
            'unread_notifications_count': unread_notifications_count,
            'recent_notifications': recent_notifications
        }
    return {}

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)