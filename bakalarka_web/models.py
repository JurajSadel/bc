from datetime import datetime
from bakalarka_web import db, login_manager
from flask_login import UserMixin as UserMixin

@login_manager.user_loader #TOTO JE EXTENSON, ocakava 4 atributy/metody (is_authentuicated(True ak je), is_active, is_annonymus, get_id)  decorator(@), aby  extension vedela, ze toto je TA funkcia, ktora am vratit usera cez jeho ID, importujeme UserMixin
def load_user(user_id):
    return User.query.get(int(user_id)) #vratime usera, ktoremu odpoveda dane ID

#DB models
file_category = db.Table('file_category',
                        db.Column('categoty_id', db.Integer, db.ForeignKey('category.category_id'), primary_key=True),
                        db.Column('file_id', db.Integer, db.ForeignKey('file.file_id'), primary_key=True))

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    VUT_id = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(50), unique = True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    files = db.relationship('File', backref='owner') #user moze mat 0,1,N files -> 1.param je meno childu, backref je "fake" column v Files tabulke, suvisi s prvym param.!!!
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_type.user_type_id'), default=2) #default=2 aby user po registracii nebol admin

    def get_id(self):   #treba pretazit kvoli Login route
        return self.user_id

    def __repr__(self):
       return self.username

    def is_admin(self): #pomocna metoda na urcenie, ci USER je ADMIN
        if self.user_type_id == 1:
            return True
        else:
            return False

    def can_view_category(self):   #pomocna metoda na pravo pre zobrazenie suborov
        if self.user_type_id > 1: #admin zacina od ID=1
            return True
        else:
            return False

class File(db.Model):
    file_id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(20), unique=True, nullable=False)
    path = db.Column(db.String(100), nullable=False)
    beg_display_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_display_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_user = db.Column(db.Integer, db.ForeignKey('user.user_id'))#foreign key suvisi s primarykey v nadradenej tabulke
    category = db.relationship('Category', secondary=file_category, backref=db.backref('files'), lazy='dynamic')

    def __repr__(self):
       return self.filename

class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key= True)
    type = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self):
        return self.type


class User_type(db.Model):
    user_type_id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(20), nullable=False)
    types = db.relationship('User', backref='type')

    def __repr__(self):
        return self.type


"""""""""

db.create_all()

admin = User_type(type='Admin')
uzivatel = User_type(type='Uzivatel')
db.session.add(admin)
db.session.add(uzivatel)


juraj = User(username='Juraj', VUT_id='197640', email='blabla', password='1234', user_type_id=1)
peter = User(username='Peter', VUT_id ='175548', email='jklkf', password='5678', user_type_id=2)
subor = File(filename='subor', path='C:/Lenovoo', beg_display_time='2008-11-11 13:23:44', end_display_time='2018-11-11 13:23:44', owner=juraj)
subor1 = File(filename='subor1', path='C:/Lenovoo/Users/PycharmProjects', beg_display_time='2008-11-11 13:23:44', end_display_time='2018-11-11 13:23:44', owner=peter)
db.session.add(juraj)
db.session.add(peter)
db.session.add(subor)
db.session.add(subor1)
db.session.commit()

skuska = Category(type='Skuska')
oznam = Category(type='Oznam')
db.session.add(skuska)
db.session.add(oznam)



skuska.categories.append(subor)
oznam.categories.append(subor)
oznam.categories.append(subor1)
db.session.commit()

for file in skuska.categories:
    print(file.file_id)

"""""
print(User.query.get(1))

for skuska in Category.query.get(2).files:
    print(skuska)