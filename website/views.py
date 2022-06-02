import json
from wtforms.fields import DateField
from wtforms.validators import DataRequired
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
    product_id = product['id']
    product = Product.query.get(product_id)
    if product:
        if product.user_id == current_user.id:
            db.session.delete(product)
            db.session.commit()

    return jsonify({})


@views.route('/fridge', method=['GET', 'POST'])
def fridge():
    form = DateForm()

    return render_template("fridge.html", user=current_user, form=form)


class DateForm(FlaskForm):
    exp_date = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')
