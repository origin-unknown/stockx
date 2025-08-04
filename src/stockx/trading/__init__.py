def create_module(app, **kwargs):
	from .routes import bp
	app.register_blueprint(bp)
