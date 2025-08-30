from .. import db
from ..users.models import User
from .forms import BuyForm, SellForm
from .models import PortfolioItem, Transaction, TransactionType
from .utils import get_stock_price
from collections import defaultdict, deque
from datetime import date, timedelta
from decimal import Decimal
from flask import (
	Blueprint, 
	abort, 
	flash, 
	redirect, 
	render_template, 
	request, 
	url_for
)
from flask_login import current_user, login_required 
from sqlalchemy.sql import func 
import plotly
import plotly.graph_objects as go
import yfinance as yf


bp = Blueprint(
	'trading', 
	__name__, 
	template_folder='../templates/trading',
	url_prefix='/portfolio'
)

@bp.route('/')
@login_required
def index():
	data = defaultdict(lambda: defaultdict(int))
	for tx in current_user.transactions:
		data[tx.symbol]['shares'] += tx.shares
		data[tx.symbol]['cost'] += tx.shares * tx.price

	total = 0
	items = []
	for k,v in data.items():
		if v['shares'] == 0:
			continue
		entry = PortfolioItem(k, v['shares'], v['cost'], get_stock_price(k))
		total += entry.value
		items.append(entry)

	return render_template('portfolio.html', **locals())

@bp.route('/transactions')
@login_required
def transactions():
	items = db.session.scalars(db.select(Transaction)\
		.where(Transaction.user_id == current_user.id)\
		.order_by(Transaction.date_created.desc())).all()
	return render_template('transactions.html', **locals())


@bp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
	form = BuyForm(request.form)
	if form.validate_on_submit():
		tx = Transaction(
			price=form.price.data, 
			shares=form.shares.data, 
			symbol=form.symbol.data.upper(), 
			type=TransactionType.BUY, 
			user_id=current_user.id
		)
		db.session.add(tx)
		db.session.commit()
		flash(f'Bought {form.shares.data} shares of {form.symbol.data.upper()}', 'success')
		return redirect(url_for('.index'))

	return render_template('buy.html', **locals())

@bp.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
	symbol = request.args.get('symbol')
	form = SellForm(request.form, data={
		'symbol': symbol, 
		'price': get_stock_price(symbol.upper(), False)
	})
	if form.validate_on_submit():
		tx = Transaction(
			price=form.price.data, 
			shares=-form.shares.data, 
			symbol=form.symbol.data.upper(), 
			type=TransactionType.SELL, 
			user_id=current_user.id
		)
		db.session.add(tx)
		db.session.commit()
		flash(f'Successfully sold {form.shares.data} shares of {form.symbol.data.upper()}', 'success')
		return redirect(url_for('.index'))

	return render_template('sell.html', **locals())

@bp.route('/sales')
@login_required
def sales():
	with db.session.begin_nested():
		sales, total_profit = calculate_fifo_profits(current_user.id)

	return render_template('sales.html', **locals())

def calculate_fifo_profits(user_id):
	txs = (
		db.session.execute(
			db.select(Transaction)
			.where(Transaction.user_id == user_id)
			.order_by(Transaction.symbol, Transaction.date_created.asc())
 		)
		.scalars()
		.all()
	)

	results = []
	total_profit = Decimal('0.0')

	queues: dict[str, deque] = {}

	for tx in txs:
		symbol_queue = queues.setdefault(tx.symbol, deque())

		if tx.type == TransactionType.BUY:
			symbol_queue.append([tx.shares, tx.price])
		elif tx.type == TransactionType.SELL:
			remaining = abs(tx.shares)
			profit = Decimal('0.0')
			while remaining > 0 and symbol_queue:
				buy_shares, buy_price = symbol_queue[0]
				used = min(remaining, buy_shares)
				profit += used * (tx.price - buy_price)
				remaining -= used
				if used == buy_shares:
					symbol_queue.popleft()
				else:
					symbol_queue[0][0] -= used

			results.append((tx, profit if remaining == 0 else None))
			if remaining == 0:
				total_profit += profit

	return results, total_profit

@bp.route('/retrieve-price/<symbol>')
@login_required
def retrieve_price(symbol):
	print(symbol)
	try:
		price = get_stock_price(symbol.upper(), True)
	except Exception as exc:
		print(exc)
		abort(404)
	return { 'data': price }

@bp.route('/charts')
@login_required
def charts():
	symbol = request.args.get('symbol', '')
	bgn_dt = request.args.get('bgn', date.today() - timedelta(weeks=52), type=lambda x: date.fromisoformat(x))
	end_dt = request.args.get('end', date.today(), type=lambda x: date.fromisoformat(x))
	return render_template('charts.html', **locals())

@bp.get('/chart-data')
def chart_data():
	symbol = request.args.get('symbol', 'AAPL')
	bgn_dt = request.args.get('bgn', date.today() - timedelta(weeks=52), type=lambda x: date.fromisoformat(x))
	end_dt = request.args.get('end', date.today(), type=lambda x: date.fromisoformat(x))

	try:
		ticker = yf.Ticker(symbol)
		currency = ticker.history_metadata['currency']
		df = ticker.history(start=bgn_dt.isoformat(), end=end_dt.isoformat(), raise_errors=True)
	except Exception as exc:
		abort(404)

	fig = go.Figure()
	fig.add_trace(go.Candlestick(
			x=df.index,
			open=df['Open'],
			high=df['High'],
			low=df['Low'],
			close=df['Close'], 
			name='Candlestick', 
		)
	)
	fig.add_trace(go.Scatter(
			x=df.index, 
			y=df['Close'], 
			mode='lines', 
			name='Close', 
			line=dict(color="#444")
		)
	)
	fig.update_layout(
		autotypenumbers='convert types', 
		title=f'{symbol.upper()} Chart',
		yaxis_title=f'Price ({currency})',
		xaxis_title='Date', 
		xaxis_rangeslider_visible=False, 
		autosize=True, 
		# paper_bgcolor='rgba(0,0,0,0)',
		# plot_bgcolor='rgba(0,0,0,0)'
	)
	# fig.update_yaxes(tickprefix="$")
	fig.update_xaxes(
		# dtick='D1',
		tickformat="%d.%m.%Y"
	)
	fig.update_xaxes(type='date')

	return fig.to_json()
