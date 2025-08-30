from .. import db
from .models import User
from .forms import (
	LoginForm, 
	RegisterForm
)
from flask import (
	Blueprint, 
	flash, 
	redirect, 
	render_template, 
	request, 
	session, 
	url_for
)
from flask_login import (
	current_user, 
	login_required, 
	login_user, 
	logout_user
)
from sqlalchemy import or_

bp = Blueprint(
	'users', 
	__name__, 
	template_folder='../templates/users',
	url_prefix='/'
)

@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		flash('You are already logged in.', 'warning')
		return redirect(url_for('main.index'))
	
	form = LoginForm(request.form)
	if form.validate_on_submit():
		user = db.session.scalar(db.select(User).where(or_(
			User.username==form.username.data,
			User.email==form.username.data))
		)
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			flash('You have been logged in.', category='success')
			return redirect(request.args.get('next', url_for('main.index')))
		flash('Invalid username or password.', 'danger')
	return render_template('login.html', **locals())

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if form.validate_on_submit():
		user = User()
		form.populate_obj(user)
		db.session.add(user)
		db.session.commit()
		flash('Your user has been created, please login.', category='success')
		return redirect(url_for('.login'))
	return render_template('register.html', **locals())

# delete account
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	if request.method == 'POST':
		user_id = current_user.id
		logout_user()
		session.clear()

		user = db.session.scalar(db.select(User).where(User.id == user_id))
		db.session.delete(user)
		db.session.commit()

		flash('Your account has been removed.', category='success')
		return redirect(url_for('main.index'))

	return render_template('profile.html', **locals())
