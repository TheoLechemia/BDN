import os, sys

# Activate your virtual env
activate_env=os.path.expanduser(os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py'))
execfile(activate_env, dict(__file__=activate_env))


APP_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, APP_DIR)

from werkzeug.debug import DebuggedApplication

from Apps.initApp import app as application
from flask.ext.compress import Compress
compress = Compress()
compress.init_app(application)

from Apps.synthese.syntheseViews import synthese

from Apps.main.mainViews import main

from Apps.importCSV.importCSVViews import importCSV

from Apps.validation.validationViews import validation

from Apps.error.error_views import errorsbp

application.register_blueprint(main)

application.register_blueprint(synthese, url_prefix='/synthese')

application.register_blueprint(importCSV, url_prefix='/importCSV')

application.register_blueprint(validation, url_prefix='/validation')

application.register_blueprint(errorsbp)


