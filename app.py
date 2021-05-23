from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import UserMixin, RoleMixin
from flask_security import SQLAlchemyUserDatastore, Security
from flask_security import login_required, current_user

myapp = Flask(__name__)
myapp.secret_key = "super secret key"
myapp.config['SECURITY_PASSWORD_SALT'] = 'MY_SALT'
myapp.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'

myapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
myapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(myapp)


# home page url
@myapp.route('/')
def index():
    return render_template('home.html')


# models Items and Addresses
class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    address = db.relationship('Address', backref='item', lazy='dynamic')

    def __repr__(self):
        return self.name


class Address(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    street = db.Column(db.String(55), nullable=False, unique=True)
    house = db.Column(db.Integer)
    front_door = db.Column(db.Integer)
    apartment = db.Column(db.String(5))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    def __repr__(self):
        return '<Street: {}, House: {}>'.format(self.street, self.house)


# models for Flask-Security
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(35), unique=True)
    password = db.Column(db.String(20))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(35), unique=True)
    description = db.Column(db.String(150))


# for Admin
class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


admin = Admin(myapp, 'FlaskApp', url='/', index_view=HomeAdminView(name='Home'))
admin.add_view(AdminView(Item, db.session))
admin.add_view(AdminView(Address, db.session))

# for Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(myapp, user_datastore)

if __name__ == "__main__":
    myapp.run(debug=True)
