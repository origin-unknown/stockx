import yfinance as yf


def get_stock_price(symbol, raise_on_error=False):
	stock = yf.Ticker(symbol)
	try:
		price = stock.info.get('regularMarketPrice')
		if price is None: raise Exception('No price found.')
		return price
	except Exception as e:
		print(f'Error fetching stock info for {symbol}: {e}')
		if raise_on_error: raise e
		return 0

def ticker_exists(symbol):
	try:
		_ = get_stock_price(form.symbol.data.upper(), True)
		return True
	except Exception as exc:
		return False
