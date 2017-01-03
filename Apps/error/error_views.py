from flask import Blueprint
from flask import render_template
from werkzeug.exceptions import HTTPException, NotFound, BadRequest

errorsbp = Blueprint('errorsbp', __name__)

@errorsbp.app_errorhandler(404)
def handle_404(err):
    return render_template('404.html', error=err), 404


@errorsbp.app_errorhandler(500)
def handle_500(err):
    err = str(err)
    return render_template('500.html', err=err), 500


# @errorsbp.errorhandler
# def handle_not_found(error):
#     return render_template('404.html')
