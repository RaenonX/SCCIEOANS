import os
from multiprocessing.pool import ThreadPool

from flask import Flask
from flask_appconfig import HerokuConfig
from flask_bootstrap import Bootstrap
from flask_jsglue import JSGlue
from flask_mail import Mail

import blueprints

sleep_prevent = ThreadPool()


# noinspection PyShadowingNames
def create_app(with_error=True, configfile=None):
    app = Flask(__name__)

    # Apply frameworks
    Bootstrap(app)
    JSGlue(app)
    HerokuConfig(app, configfile)
    
    # Register blueprints
    if with_error:
        app.register_blueprint(blueprints.err)
    app.register_blueprint(blueprints.api)
    app.register_blueprint(blueprints.frontend)
    app.register_blueprint(blueprints.frontend_student)
    app.register_blueprint(blueprints.frontend_advisor)
    app.register_blueprint(blueprints.frontend_staff)
    app.register_blueprint(blueprints.frontend_user)
    
    # Configure app for flask-mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.environ["GM_EMAIL"]
    app.config['MAIL_PASSWORD'] = os.environ["GM_PASSWORD"]
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = os.environ["GM_EMAIL"]

    # Set jinja cache to unlimited 
    app.jinja_env.cache = {}

    # Generate secret key for forms
    app.secret_key = bytes(os.environ.get("SECRET_KEY"), encoding='utf-8')
    
    # Configure app to for bootstrap to not use CDN
    app.config["BOOTSTRAP_SERVE_LOCAL"] = True
    
    # Configure mail instance
    app.config["MAIL_INSTANCE"] = Mail(app)
    
    # Append nav bar to app
    blueprints.nav.init_app(app)

    return app


if __name__ == "__main__":
    if os.environ["APP_ROOT_URL"] is None:
        print("Specify environment variable 'APP_ROOT_URL', or some functions will malfunction.")
        
    if os.environ["PORT"] is None:
        port = 5000
    else:
        port = int(os.environ["PORT"])

    app = create_app()
    app.run(port=port, host="0.0.0.0")
