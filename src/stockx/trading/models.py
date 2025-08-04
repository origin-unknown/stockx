from .. import db
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy import Enum
from sqlalchemy.sql import func 
import enum


@dataclass
class PortfolioItem:
	symbol: str
	shares: int
	cost: float
	price: float

	@property
	def value(self) -> float:
		return self.shares * self.price

	@property
	def gain(self) -> float:
		return self.value - self.cost

class TransactionType(enum.Enum):
	BUY = 1
	SELL = 2


class Transaction(db.Model):
	__tablename__ = 'transactions'
	id: db.Mapped[int] = db.mapped_column(db.Integer, primary_key=True)
	date_created: db.Mapped[datetime] = db.mapped_column(
		db.DateTime(timezone=True), 
		nullable=False, 
		server_default=func.now()
	)
	symbol: db.Mapped[str] = db.mapped_column(db.String(10), nullable=False)
	shares: db.Mapped[int] = db.mapped_column(db.Integer, nullable=False, default=0)
	price: db.Mapped[float] = db.mapped_column(db.Float, nullable=False, default=0.0)
	type: db.Mapped[TransactionType] = db.mapped_column(Enum(TransactionType), nullable=False)

	user_id: db.Mapped[int]= db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	user: db.Mapped['User'] = db.relationship(back_populates='transactions')

	@property
	def cost(self):
		return abs(self.shares * self.price)

