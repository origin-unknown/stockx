from .. import db
from .models import User
from flask_login import (
	AnonymousUserMixin, 
	LoginManager
) 


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'users.login'

def create_module(app, **kwargs):
	login_manager.init_app(app)

	from .routes import bp
	app.register_blueprint(bp)

@login_manager.user_loader
def load_user(userid):
	return db.session.get(User, int(userid))
