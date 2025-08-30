from .. import db
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Enum, Float, func
from sqlalchemy.ext.hybrid import hybrid_property
import enum


@dataclass
class PortfolioItem:
	symbol: str
	shares: int
	cost: Decimal
	price: float

	@property
	def value(self) -> float:
		return self.shares * self.price

	@property
	def gain(self) -> Decimal:
		return Decimal(str(self.value)) - self.cost

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
	price: db.Mapped[Decimal] = db.mapped_column(db.Numeric(15,2), nullable=False, default=0)
	type: db.Mapped[TransactionType] = db.mapped_column(Enum(TransactionType), nullable=False)

	user_id: db.Mapped[int]= db.mapped_column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	user: db.Mapped['User'] = db.relationship(back_populates='transactions')

	@hybrid_property
	def cost(self):
		return abs(self.shares * self.price)

