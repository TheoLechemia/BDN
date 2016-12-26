import os, sys

# Activate your virtual env
activate_env=os.path.expanduser(os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py'))
execfile(activate_env, dict(__file__=activate_env))


APP_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, APP_DIR)

from werkzeug.debug import DebuggedApplication

from Apps.initApp import app

from Apps.synthese.syntheseViews import synthese

from Apps.main.mainViews import main

from Apps.importCSV.importCSVViews import importCSV

from Apps.validation.validationViews import validation

app.register_blueprint(main)

app.register_blueprint(synthese)

app.register_blueprint(importCSV, url_prefix='/importCSV')

app.register_blueprint(validation, url_prefix='/validation')

application = DebuggedApplication(app, evalex=True)