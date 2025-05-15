from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# 初始化扩展，但不绑定到应用
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# 配置登录管理器
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'info'