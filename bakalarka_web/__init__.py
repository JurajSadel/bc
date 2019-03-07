from flask import Flask, abort, redirect, url_for, request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import  SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers, form
from flask_login import current_user


app = Flask(__name__) #placeholder for current module (v ytomto pripade app.py)

app.config['SECRET_KEY'] = '28d2c0f9d752001875ef12e9ebf68c93'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/bakalarka' #specifikujem cestu k databaze
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) #mam instanciu SQLAlchemy databaze a mozem pracovat s DB, mozem reprezentovat DB pomocou class (modelov), akzda classa jedna tabulka
migrate = Migrate(app,db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  #aby extension vedela, kde je login route, 'login' je funkcny nazov routu (ten co davam do url_for()
login_manager.login_message_category='info' #nameisto flash messages -> class z BOOTSTRAPU

#admin = flask_admin.Admin(app,'Elektronická informačná tabuľa')


from bakalarka_web.models import User, File, Category, User_type


class AdminView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.is_admin():
            CategoryView.can_delete = True
            CategoryView.can_edit = True
            CategoryView.can_create = True
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('login', next=request.url))



    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class CategoryView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.is_admin() or current_user.can_view_category():
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('login', next=request.url))
        if not current_user.is_admin():
            CategoryView.can_delete = False
            CategoryView.can_edit = False
            CategoryView.can_create = True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))



admin = flask_admin.Admin(
        app, 'Electronic notice board'
       )

admin.add_view(AdminView(User, db.session))
admin.add_view(CategoryView(Category, db.session))
#admin.add_view(AdminView(User_type, db.session))
#admin.add_view(AdminView(File, db.session))



from bakalarka_web import routes