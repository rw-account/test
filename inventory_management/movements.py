from flask import (
    Blueprint, flash, g, redirect, render_template, url_for
)
from werkzeug.exceptions import abort
from inventory_management.auth import login_required
from inventory_management.db import get_db

from inventory_management.forms import MovementForm

bp = Blueprint('movements', __name__, url_prefix='/movements')

@bp.route("/")
@login_required
def index():
    form = MovementForm()
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    return render_template("movements/index.html", products=products, form=form)

@bp.route("/in/<int:product_id>",  methods=['POST',])
@login_required
def stock_in(product_id):
    form = MovementForm()
    if form.validate_on_submit(): # علشان الحماية من CSRF 
        quantity =form.quantity.data
        db = get_db()
        # تسجيل حركة زيادة الكمية
        db.execute(
            "INSERT INTO movements (user_id, product_id, type, quantity) VALUES (?, ?, ?, ?)",
            (g.user['id'], product_id, 'in', quantity)
        )
        db.execute("UPDATE products SET quantity = quantity + ? WHERE product_id = ?", (quantity, product_id))
        db.commit()
        flash('تم اضافة الكمية بنجاح', 'success')
        return redirect(url_for("movements.index", form=form))
    return redirect(url_for("movements.index", form=form))
    


@bp.route("/out/<int:product_id>",  methods=['POST',])
@login_required
def stock_out(product_id):
    form = MovementForm()

    if form.validate_on_submit(): # علشان الحماية من CSRF 
        quantity = form.quantity.data
        db = get_db()
        # تسجيل حركة تنقيص الكمية
        db.execute(
            "INSERT INTO movements (user_id, product_id, type, quantity) VALUES (?, ?, ?, ?)",
            (g.user['id'], product_id, 'out', quantity)
        )
        db.execute("UPDATE products SET quantity = quantity - ? WHERE product_id = ?", (quantity, product_id))
        db.commit()
        flash('تم تنقيص الكمية بنجاح', 'success')
        return redirect(url_for("movements.index", form=form))
    return redirect(url_for("movements.index", form=form))


@bp.route("/history")
@login_required
def history():
    db = get_db()
    history_of_movements = db.execute("""
        SELECT m.*, p.name as product_name, u.username as user_name
        FROM movements m
        JOIN products p ON m.product_id = p.product_id
        JOIN users u ON m.user_id = u.id
        ORDER BY m.added_at DESC
        """).fetchall()
    users = db.execute(
        'SELECT username FROM users'
        ).fetchall()
    # تحويل UTC إلى توقيتنا المحلي (+3) لكي تظهر الساعه في وقت الاضافه بشكل صحيح
    from datetime import timedelta
    return render_template("movements/history.html", timedelta=timedelta ,history_of_movements=history_of_movements, users=users)


