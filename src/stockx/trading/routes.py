from .. import db
from ..users.models import User
from .forms import BuyForm, SellForm
from .models import PortfolioItem, Transaction, TransactionType
from .utils import get_stock_price
from collections import defaultdict
from datetime import date, timedelta
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
	items = db.session.scalars(db.select(Transaction).order_by(Transaction.date_created.desc())).all()
	return render_template('transactions.html', **locals())


@bp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
	form = BuyForm(request.form)
	if form.validate_on_submit():
		try:
			price = get_stock_price(form.symbol.data.upper(), True)
		except Exception as exc:
			flash(r'No price available at the moment.', 'danger')
			return redirect(request.url)
		tx = Transaction(
			price=price, 
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
	form = SellForm(request.form, data={'symbol': symbol})
	if form.validate_on_submit():
		try:
			price = get_stock_price(form.symbol.data.upper(), True)
		except Exception as exc:
			flash(r'No price available at the moment.', 'danger')
			return redirect(request.url)
		tx = Transaction(
			price=price,  
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
		yaxis_title='Price (USD)',
		xaxis_title='Date', 
		xaxis_rangeslider_visible=False, 
		autosize=True
	)
	fig.update_yaxes(tickprefix="$")
	fig.update_xaxes(
#		dtick='D1',
		tickformat="%d.%m.%Y"
	)
	fig.update_xaxes(type='date')

	return fig.to_json()
