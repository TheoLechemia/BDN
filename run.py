from Apps.initApp import app

from Apps.synthese.syntheseViews import synthese

from Apps.main.mainViews import main

from Apps.importCSV.importCSVViews import importCSV

from Apps.validation.validationViews import validation

app.register_blueprint(main)

app.register_blueprint(synthese, url_prefix='/synthese')

app.register_blueprint(importCSV, url_prefix='/importCSV')

app.register_blueprint(validation, url_prefix='/validation')


if __name__ == "__main__":
    app.run(debug=True)
