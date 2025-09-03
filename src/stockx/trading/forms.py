from .. import db
from .models import Transaction
from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy import func
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Regexp, ValidationError


class BuyForm(FlaskForm):
	symbol = StringField('Symbol', 
		validators=[
			DataRequired(), 
			Regexp(
				r'^[A-Z0-9]{1,5}(?:[.:][A-Z]{1,3})?$', 
				message='Invalid symbol'
			)
		]
	)
	# Allow fractional numbers
	# shares = DecimalField('Number of Shares', places=3, validators=[NumberRange(min=0)])
	shares = IntegerField('Number of Shares', validators=[DataRequired(), NumberRange(min=1)])
	price = DecimalField('Price (USD)', validators=[NumberRange(min=0)])
	submit = SubmitField('Buy')

class SellForm(FlaskForm):
	symbol = StringField('Symbol', 
		validators=[
			DataRequired(), 
			Regexp(
				r'^[A-Z0-9]{1,5}(?:[.:][A-Z]{1,3})?$', 
				message='Invalid symbol'
			)
		]
	)
	# Allow fractional numbers
	# shares = DecimalField('Number of Shares', places=3, validators=[NumberRange(min=0)])
	shares = IntegerField('Number of Shares', validators=[DataRequired(), NumberRange(min=1)])
	price = DecimalField('Price (USD)', validators=[NumberRange(min=0)])
	submit = SubmitField('Sell')

	def validate_shares(self, field):
		cnt, *_ = db.session.execute(
			db.select(func.sum(Transaction.shares))
				.where(Transaction.symbol == self.symbol.data, Transaction.user_id == current_user.id)).first()
		if cnt is None or cnt < field.data:
			raise ValidationError('Too few shares.')

	def validate_symbol(self, field):
		cnt, *_ = db.session.execute(
			db.select(func.sum(Transaction.shares))
				.where(Transaction.symbol == field.data, Transaction.user_id == current_user.id)).first()
		if cnt is None:
			raise ValidationError('Symbol not found.')
