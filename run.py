from Apps.initApp import app

from Apps.synthese.syntheseViews import synthese

from Apps.main.mainViews import main

from Apps.importCSV.importCSVViews import importCSV

from Apps.validation.validationViews import validation

from Apps.addObs.addObsViews import addObs

from Apps.download.downloadViews import download

from Apps.meta.metaViews import meta

from flask.ext.compress import Compress


compress = Compress()
compress.init_app(app)

app.register_blueprint(main)

app.register_blueprint(synthese,url_prefix='/synthese')

app.register_blueprint(importCSV, url_prefix='/importCSV')

app.register_blueprint(validation, url_prefix='/validation')

app.register_blueprint(addObs, url_prefix='/addObs')

app.register_blueprint(download, url_prefix='/download')

app.register_blueprint(meta	, url_prefix='/meta')


if __name__ == "__main__":
    app.run(debug=True)
