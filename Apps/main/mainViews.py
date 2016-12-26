from flask import Blueprint, render_template

main = Blueprint('main', __name__, static_url_path="/main", static_folder="static", template_folder="templates")


@main.route('/')
def index():
	return render_template('index.html')