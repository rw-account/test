from flask import (
    Blueprint,render_template
)
from werkzeug.exceptions import abort
from inventory_management.auth import login_required
from inventory_management.db import get_db

bp = Blueprint('homepage', __name__,)

@bp.route("/")
def index():
    return render_template("homepage/index.html")