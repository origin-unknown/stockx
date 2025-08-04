from .. import db
from .models import User
from flask_wtf import FlaskForm
from wtforms import (
	BooleanField, 
	StringField, 
	SubmitField, 
	PasswordField
)
from wtforms.validators import (
	DataRequired, 
	Email, 
	EqualTo, 
	Length, 
	Regexp, 
	ValidationError
)


class LoginForm(FlaskForm):
	username = StringField(
		'Username',
		description='E-Mail or Username',
		validators=[
			DataRequired(),
		],
		render_kw={
			'placeholder': 'E-Mail or Username',
			'aria-discribedby': 'Username',
		}
	)
	password = PasswordField(
		'Password',
		description='Password',
		validators=[
			DataRequired()
		],
		render_kw={
			'placeholder': 'Password',
			'aria-discribedby': 'Password',
		}
	)
	remember_me = BooleanField(
		'Remember me',
		description='Remember me', 
		validators=[],
	)
	submit = SubmitField('Sign in')

class RegisterForm(FlaskForm):
	email = StringField(
		'Email',
		# description='Email',
		validators=[
			DataRequired(),
			Email()
		])
	username = StringField(
		'Username',
		validators=[
			DataRequired(),
			Length(1,15),
			Regexp(
				r'^[A-Za-z][A-Za-z0-9_\.]*$', 
				message='Username must have only letters, numbers, dots or underscores.'
			)
		])
	password = PasswordField(
		'Password',
		validators=[
			DataRequired(),
			Length(3,64),
		])
	password_confirm = PasswordField(
		'Confirm Password',
		validators=[
			DataRequired(), 
			EqualTo('password')
		])
	submit = SubmitField('Create account')

	def validate_email(self, field):
		if db.session.scalar(db.select(User).where(User.email == field.data)):
			raise ValidationError('Email already in use.')

	def validate_username(self, field):
		if db.session.scalar(db.select(User).where(User.username == field.data)):
			raise ValidationError('Username already in use.')
