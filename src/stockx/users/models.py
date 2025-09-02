from .. import db
from flask_bcrypt import (
	generate_password_hash, 
	check_password_hash
)
from flask_login import UserMixin
from hashlib import md5, sha256 
from typing import List


class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
	username: db.Mapped[str] = db.mapped_column(db.String(15), nullable=False)
	email: db.Mapped[str] = db.mapped_column(db.String(320), unique=True)
	password_hash: db.Mapped[str] = db.mapped_column(db.String(60), nullable=False)

	transactions: db.Mapped[List['Transaction']] = db.relationship(
		back_populates='user', 
		cascade='all, delete-orphan' 
	)

	@property
	def password(self):
		raise AttributeError('writeonly attr: password')

	@password.setter
	def password(self, value):
		self.password_hash = generate_password_hash(value)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size):
		digest = sha256(self.email.lower().encode('utf-8')).hexdigest()
		return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
