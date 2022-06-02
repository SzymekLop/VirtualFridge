from . import db
from flask_login import UserMixin
import datetime
from abc import abstractmethod


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

    __mapper_args__ = {
        "polymorphic_identity": "Product",
        "polymorphic_on": type,
    }

    # def __init__(self, name, amount=1, unit="pcs"):
    #     self._name = name
    #     self._amount = amount
    #     self._unit = unit
    #
    # @property
    # def name(self):
    #     return self._name
    #
    # @name.setter
    # def name(self, new_name):
    #     if len(new_name) > 0:
    #         self._name = new_name
    #     else:
    #         raise ValueError("Name cannot be empty")
    #
    # @property
    # def amount(self):
    #     return self._amount
    #
    # @amount.setter
    # def amount(self, new_amount):
    #     if isinstance(new_amount, int):
    #         if new_amount >= 0:
    #             self._amount = new_amount
    #         else:
    #             raise ValueError("Amount must be positive")
    #     else:
    #         raise TypeError("Amount must be a integer")
    #
    # @property
    # def unit(self):
    #     return self._unit
    #
    # @unit.setter
    # def unit(self, new_unit):
    #     self._unit = new_unit
    #

    def __str__(self):
        return "%d %s of %s" % (self.amount, self.unit, self.name)

    def use(self):
        self.amount = self.amount - 1

    @abstractmethod
    def check(self):
        pass

    @abstractmethod
    def notification(self):
        pass


class DateProduct(Product):
    exp_date = db.Column(db.Date)

    __mapper_args__ = {
        "polymorphic_identity": "DateProduct",
    }

    # def __init__(self, name, exp_date, amount=1):
    #     super().__init__(name, amount)
    #     self._exp_date = exp_date
    #
    # @property
    # def exp_date(self):
    #     return self._exp_date
    #
    # @exp_date.setter
    # def exp_date(self, new_date):
    #     self._exp_date = new_date

    def check(self):
        return (self.exp_date - datetime.date.today()).days

    def notification(self):
        days = self.check()
        if days < -1:
            return "Your %s expired %d days ago :(" % (self.__str__(), days)
        elif days < 0:
            return "Your %s expired yesterday :(" % self.__str__()
        elif days == 0:
            return "Your %s expires today" % self.__str__()
        elif days == 1:
            return "Your %s expires tomorrow" % self.__str__()
        else:
            return "Your %s expires in %d days" % (self.__str__(), days)


class FreshProduct(Product):
    exp_days = db.Column(db.Integer)
    start = db.Column(db.Date)

    __mapper_args__ = {
        "polymorphic_identity": "DateProduct",
    }

    # def __init__(self, name, amount=1, exp_days=3):
    #     super().__init__(name, amount, "")
    #     self._exp_days = exp_days
    #     self._start = datetime.date.today()
    #
    # @property
    # def exp_days(self):
    #     return self._exp_days
    #
    # @exp_days.setter
    # def exp_days(self, new_days):
    #     if isinstance(new_days, int):
    #         if new_days > 0:
    #             self._exp_days = new_days
    #         else:
    #             raise ValueError("Amount of days till expire must be grater than 0")
    #     else:
    #         raise TypeError("Amount of days till expire must be an integer")
    #
    # @property
    # def start(self):
    #     return self._start
    #
    # @start.setter
    # def start(self, date):
    #     self._start = date

    def check(self):
        return (self._start - datetime.date.today()).days + self.exp_days

    def notification(self):
        days = self.check()
        if days < 0:
            return "You should check your %s before eating it" % self.__str__()
        else:
            return "Your %s should be fresh" % self.__str__()


class NonExpProduct(Product):
    notify = db.Column(db.Integer)

    __mapper_args__ = {
        "polymorphic_identity": "NonExpProduct",
    }

    # def __init__(self, name, amount=1, notify=1):
    #     super().__init__(name, amount)
    #     self._notify = notify
    #
    # @property
    # def notify(self):
    #     return self._notify
    #
    # @notify.setter
    # def notify(self, new_notify):
    #     if isinstance(new_notify, int):
    #         self._notify = new_notify
    #     else:
    #         raise TypeError("Amount of pieces to notify must be an integer")

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

    # def __init__(self):
    #     self._products = list()
    #
    # @property
    # def products(self):
    #     return self._products
    #
    # @products.setter
    # def products(self, new_products):
    #     if isinstance(new_products, list):
    #         self._products = new_products
    #     else:
    #         raise TypeError

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

    def check_products(self):
        res = list()
        for idp, product in enumerate(self.products):
            if product.check() <= 0:
                res.append((product.notification(), idp))
        return res


class ShoppingList(db.Model):

    list_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    products = db.relationship('Product')

    # def __init__(self):
    #     self._products = list()
    #
    # @property
    # def products(self):
    #     return self._products
    #
    # @products.setter
    # def products(self, new_list):
    #     if isinstance(new_list, list):
    #         self._products = new_list
    #     else:
    #         raise TypeError("Must be list")

    def add_position(self, product):
        if isinstance(product, Product):
            self.products.append((product, 0))
        else:
            raise TypeError("You can only buy products")

    def bought(self, index, amount=0):
        if self.products[index].amount != 0:
            if amount >= self.products[index].amount:
                self.products[index] = (self.products[index], 1)
            else:
                self.products[index] = (self.products[index][0], amount - self.products[index][0].amount)
                self.products[index].amount(amount)
        else:
            self.products[index] = (self.products[index], 1)

    def check(self):
        res = list()
        for idp, position in enumerate(self._products):
            if position[1] == 0:
                res.append(("You haven't bought %s" % position[0].name, idp))
            elif position[1] < 0:
                res.append(("You haven't bought %d %s of %s" %
                            (abs(position[1]), position[0].unit, position[0].name), idp))
            return res
    #
    # def fill_fridge(self, fridge):
    #     if isinstance(fridge, fridge.Fridge):
    #         for position in self._products:
    #             if position[1] >= 0:
