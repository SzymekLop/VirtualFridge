import json
from wtforms.fields import DateField
from wtforms import validators, SubmitField
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from.modules import *

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/delete-product', methods=['POST'])
def delete_product():
    product = json.loads(request.data)
    product_id = product['productId']
    product = Product.query.get(product_id)
    if product:
        if Fridge.query.get(product.fridge_id).user_id == current_user.id:
            db.session.delete(product)
            db.session.commit()
    return jsonify({})


@views.route('/shopping-list/delete-product', methods=['POST'])
def delete_list_product():
    product = json.loads(request.data)
    product_id = product['productId']
    product = Product.query.get(product_id)
    if product:
        if ShoppingList.query.get(product.list_id).user_id == current_user.id:
            db.session.delete(product)
            db.session.commit()
    return jsonify({})


@views.route('/delete-list', methods=['POST'])
def delete_list():
    shopping = json.loads(request.data)
    list_id = shopping['listId']
    shopping = ShoppingList.query.get(list_id)
    if shopping:
        if shopping.user_id == current_user.id:
            db.session.delete(shopping)
            db.session.commit()
    return jsonify({})


@views.route('/fridge', methods=['GET', 'POST'])
def fridge():
    form = DateForm()
    if request.method == 'POST':
        if "date" in request.form:
            name = request.form['date_product_name']
            if len(name) < 1 or name is None:
                flash('Name of product is too short!', category='error')
            else:
                amount = request.form['date_amount']
                if int(amount) <= 0:
                    flash('Amount of product must be positive!', category='error')
                else:
                    unit = request.form['date_unit']
                    date = form.exp_date.data
                    notify = request.form['date_notify']
                    new_product = DateProduct(name=name, amount=int(amount), unit=unit,
                                              fridge_id=current_user.fridge.id, type="DateProduct",
                                              notify=int(notify), exp_date=date)
                    db.session.add(new_product)
                    db.session.commit()
                    flash('Product added!', category='success')
        elif "fresh" in request.form:
            name = request.form['fresh_name']
            if len(name) < 1 or name is None:
                flash('Name of product is too short!', category='error')
            else:
                amount = request.form['fresh_amount']
                if int(amount) <= 0:
                    flash('Amount of product must be positive!', category='error')
                else:
                    unit = request.form['fresh_unit']
                    notify = request.form['fresh_notify']
                    new_product = FreshProduct(name=name, amount=int(amount), unit=unit,
                                               fridge_id=current_user.fridge.id, type="FreshProduct",
                                               notify=int(notify), bought=datetime.date.today())
                    db.session.add(new_product)
                    db.session.commit()
                    flash('Product added!', category='success')
        elif "non_exp" in request.form:
            name = request.form['non_name']
            if len(name) < 1 or name is None:
                flash('Name of product is too short!', category='error')
            else:
                amount = request.form['non_amount']
                if int(amount) <= 0:
                    flash('Amount of product must be positive!', category='error')
                else:
                    unit = request.form['non_unit']
                    notify = request.form['non_notify']
                    new_product = NonExpProduct(name=name, amount=int(amount), unit=unit,
                                                fridge_id=current_user.fridge.id,
                                                type="NonExpProduct", notify=int(notify))
                    db.session.add(new_product)
                    db.session.commit()
                    flash('Product added!', category='success')
    return render_template("fridge.html", user=current_user, form=form)


@views.route('/shopping-lists', methods=['GET', 'POST'])
def shopping_lists():
    if request.method == 'POST':
        new_list = ShoppingList(user_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        flash('Shopping list added!', category='success')
    return render_template("shopping-lists.html", user=current_user)


@views.route('/shopping-lists/list/<list_id>', methods=['GET', 'POST'])
def shopping_list(list_id):
    my_list = ShoppingList.query.get(list_id)
    place = 'list.html'
    if request.method == 'POST':
        if 'add_product' in request.form:
            name = request.form['name']
            if len(name) < 1 or name is None:
                flash('Name of product is too short!', category='error')
            else:
                amount = int(request.form['amount'])
                unit = request.form['unit']
                product_type = request.form['type']
                if product_type == 'dateProduct':
                    new_product = DateProduct(name=name, amount=amount, unit=unit)
                    my_list.products.append(new_product)
                    db.session.add(new_product)
                elif product_type == 'freshProduct':
                    new_product = FreshProduct(name=name, amount=amount, unit=unit)
                    my_list.products.append(new_product)
                    db.session.add(new_product)
                elif product_type == 'nonExpProduct':
                    new_product = NonExpProduct(name=name, amount=amount, unit=unit)
                    my_list.products.append(new_product)
                    db.session.add(new_product)
        elif 'update' in request.form:
            place = 'shopping-lists.html'
            print('dziala')

        db.session.commit()
    return render_template(place, user=current_user, list=my_list)


class DateForm(FlaskForm):
    exp_date = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')
