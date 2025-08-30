from flask import Flask, current_app, request, session
from flask_babel import Babel
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import (
	DeclarativeBase, 
)


class Base(DeclarativeBase):
	pass


babel = Babel()
csrf = CSRFProtect()
db = SQLAlchemy(model_class=Base)
moment = Moment()

def get_locale():
    return session.get('lang', request.accept_languages.best_match(current_app.config['BABEL_SUPPORTED_LOCALES']))

def create_app():
	app = Flask(__name__)
	#  later use Config class
	app.config.from_mapping(
		SECRET_KEY='your secret here', 
		SQLALCHEMY_DATABASE_URI='sqlite:///stockx.db', 
		BABEL_DEFAULT_LOCALE='en', 
		BABEL_SUPPORTED_LOCALES=['en', 'de'] 
	)

	babel.init_app(app, locale_selector=get_locale)
	csrf.init_app(app)
	db.init_app(app)
	moment.init_app(app)

	with app.app_context():
		from .users.models import User
		from .trading.models import Transaction, TransactionType
		db.drop_all()
		db.create_all()

		user = User(
			email='user@home.org', 
			username='user', 
			password='pass'
		)
		db.session.add(user)
		db.session.commit()


		from datetime import datetime, timedelta, timezone
		txs = [
			Transaction(
				date_created=datetime.now(timezone.utc) - timedelta(days=1), 
				user=user, 
				symbol='AAPL', 
				shares=20, 
				price=202.40, 
				type=TransactionType.BUY
			), 
			Transaction(
				user=user, 
				symbol='AAPL', 
				shares=-10, 
				price=202.40, 
				type=TransactionType.SELL
			), 
			Transaction(
				date_created=datetime.now(timezone.utc) - timedelta(hours=2), 
				user=user, 
				symbol='MSFT', 
				shares=20, 
				price=540.80, 
				type=TransactionType.BUY
			), 
			Transaction(
				date_created=datetime.now(timezone.utc) - timedelta(hours=2), 
				user=user, 
				symbol='TSLA', 
				shares=10, 
				price=302.63, 
				type=TransactionType.BUY
			), 
			Transaction(
				date_created=datetime.now(timezone.utc) - timedelta(hours=2), 
				user=user, 
				symbol='GOOGL', 
				shares=10, 
				price=189.13, 
				type=TransactionType.BUY
			), 
			Transaction(
				date_created=datetime.now(timezone.utc) - timedelta(hours=2), 
				user=user, 
				symbol='AMZN', 
				shares=10, 
				price=214.75, 
				type=TransactionType.BUY
			)
		]
		db.session.add_all(txs)
		db.session.commit()

	register_blueprints(app)

	return app

def register_blueprints(app):
	from importlib import import_module
	mods = (
		('.main', {}), 
		('.users', {}), 
		('.trading', {}), 
	)
	for ident,kwargs in mods:
		module = import_module(ident, __name__)
		module.create_module(app, **kwargs)
