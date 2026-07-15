import os
from flask import (
    Blueprint, flash, g, redirect, render_template, url_for
)
from werkzeug.exceptions import abort

from inventory_management.forms import ProductForm
from inventory_management.auth import login_required
from inventory_management.db import get_db

bp = Blueprint('products_management', __name__, url_prefix='/products_management')

@bp.route('/')
@login_required
def index():
    form = ProductForm() 
    db = get_db()
    products = db.execute(
        'SELECT * FROM products'
    ).fetchall()
    return render_template('products_management/index.html',products=products, form=form)

def get_product(id):
    db = get_db()
    product = db.execute(
        'SELECT * '
        ' FROM products'
        ' WHERE product_id = ?',
        (id,)
    ).fetchone()

    if product is None:
        abort(404, f"product id {id} doesn't exist.")
    
    if product['created_by'] != g.user['id']:
        abort(403)

    return product

@bp.route('/add_product', methods=['GET','POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit(): # علشان الحماية من CSRF 
        db = get_db()
        name = form.name.data.strip()
        price = str(form.price.data)
        quantity = form.quantity.data
        description = form.description.data.strip()

        db.execute("""INSERT INTO products (name, price, quantity, description, created_by)
                                VALUES (?, ?, ?, ?, ?)""",
                                (name, price, quantity, description, g.user['id']))
        db.commit()
        flash('تم اضافة المنتج بنجاح', 'success')
        return redirect(url_for('products_management.index')) 
    
    return render_template('products_management/add_product.html', form=form)


@bp.route('/edit_product/<int:id>/', methods=['GET','POST'])
@login_required
def edit_product(id):
    form = ProductForm()
    product = get_product(id)
    if form.validate_on_submit(): # علشان الحماية من CSRF
        # قراءة البيانات من النموذج
        name = form.name.data.strip()
        price = str(form.price.data)
        quantity = form.quantity.data
        description = form.description.data.strip()


        # تحديث بيانات المنتج في قاعدة البيانات
        db = get_db()
        db.execute(
            'UPDATE products SET name = ?, price = ?, quantity = ?, description = ? '
            'WHERE product_id = ?',
            (name, price, quantity, description, id)
        )
        db.commit()

        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('products_management.index'))
    
    return render_template('products_management/edit_product.html', product=product, form=form)

@bp.route("/delete_product/<int:id>", methods=['POST',])
@login_required
def delete_product(id):
    get_product(id) # هدفها التحقق فقط (وجود المنتج وصلاحية المستخدم)
    db = get_db()
    db.execute('DELETE FROM products WHERE product_id = ?', (id,))
    db.commit()
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('products_management.index'))
