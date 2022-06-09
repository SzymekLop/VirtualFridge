from . import db
from flask_login import UserMixin
import datetime
from abc import abstractmethod
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    fridge = db.relationship('Fridge', back_populates='User', uselist=False)
    lists = db.relationship('ShoppingList')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    amount = db.Column(db.Integer)
    unit = db.Column(db.String(30))
    fridge_id = db.Column(db.Integer, db.ForeignKey('fridge.id'), nullable=True)
    list_id = db.Column(db.Integer, db.ForeignKey('shopping_list.list_id'), nullable=True)
    type = db.Column(db.String(50))
    notify = db.Column(db.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "Product",
        "polymorphic_on": type,
    }

    def __str__(self):
        return "%d %s of %s" % (self.amount, self.unit, self.name)

    # decrease amount of product by one
    def use(self):
        self.amount = self.amount - 1
        if self.amount == 0:
            db.session.delete(self)
        db.session.commit()

    # will return number deciding what notification to give
    @abstractmethod
    def check(self):
        pass

    # will return notification
    @abstractmethod
    def notification(self):
        pass


class DateProduct(Product):
    # date of expire
    exp_date = db.Column(db.Date)

    __mapper_args__ = {
        "polymorphic_identity": "DateProduct",
    }

    def check(self):
        if self.exp_date is None:
            return None
        else:
            days = (self.exp_date - datetime.date.today()).days
            if days < 0:
                return -1
            elif days <= self.notify:
                return 0
            else:
                return 1

    def notification(self):
        days = (self.exp_date - datetime.date.today()).days
        if days < -1:
            return "Your %s expired %d days ago" % (self.__str__(), abs(days))
        elif days < 0:
            return "Your %s expired yesterday" % self.__str__()
        elif days == 0:
            return "Your %s expires today" % self.__str__()
        elif days == 1:
            return "Your %s expires tomorrow" % self.__str__()
        else:
            return "Your %s expires in %d days" % (self.__str__(), days)


class FreshProduct(Product):
    # date of bought
    bought = db.Column(db.Date)

    __mapper_args__ = {
        "polymorphic_identity": "FreshProduct",
    }

    def check(self):
        if self.bought is None:
            return None
        else:
            return 1 if (datetime.date.today() - self.bought).days <= self.notify else -1

    def notification(self):
        days = self.notify - (datetime.date.today() - self.bought).days
        if days < 0:
            return "You should check your %s before eating it" % self.__str__()
        elif days == 0:
            return "Your %s should be fresh" % self.__str__()
        elif days == 1:
            return "Your %s should be fresh for 1 more day" % self.__str__()
        else:
            return "Your %s should be fresh for %d more days" % (self.__str__(), days)


class NonExpProduct(Product):

    __mapper_args__ = {
        "polymorphic_identity": "NonExpProduct",
    }

    def check(self):
        return self.amount - self.notify

    def notification(self):
        amount = self.check()
        if amount > 0:
            return "You have %s" % self.__str__()
        else:
            return "You're running out of %s. You only have %d %s" % (self.name, self.amount, self.unit)


class Fridge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    User = db.relationship("User", back_populates="fridge")
    products = db.relationship("Product")

    def add_product(self, new_product):
        if isinstance(new_product, Product):
            self.products.append(new_product)
        else:
            raise TypeError("You can only put products in a fridge")

    def remove_product(self, index):
        self.products[index].use()
        if self.products[index].amount < 1:
            self.products.pop(index)
            return 0
        else:
            return self.products[index].amount

    # return list of notification for products that need attention
    def check_products(self):
        res = list()
        for idp, product in enumerate(self.products):
            if product.check() <= 0:
                res.append((product.notification(), idp))
        return res


class ShoppingList(db.Model):

    list_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    products = db.relationship('Product')
    name = db.Column(db.String)

    # add product to list
    def add_position(self, product):
        if isinstance(product, Product):
            self.products.append((product, 0))
        else:
            raise TypeError("You can only buy products")

    # check if all planed pieces are bought
    def bought(self, index, amount=0):
        if self.products[index].amount != 0:
            if amount >= self.products[index].amount:
                self.products[index] = (self.products[index], 1)
            else:
                self.products[index] = (self.products[index][0], amount - self.products[index][0].amount)
                self.products[index].amount(amount)
        else:
            self.products[index] = (self.products[index], 1)

    # return list of information rather all planed products are bought on not
    def check(self):
        res = list()
        for idp, position in enumerate(self._products):
            if position[1] == 0:
                res.append(("You haven't bought %s" % position[0].name, idp))
            elif position[1] < 0:
                res.append(("You haven't bought %d %s of %s" %
                            (abs(position[1]), position[0].unit, position[0].name), idp))
            return res
