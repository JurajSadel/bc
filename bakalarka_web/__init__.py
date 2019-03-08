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
from sqlalchemy import event
from flask_login import current_user
import os
import shutil
from wand.image import Image
import os.path as op
import flask_admin.form.upload

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

#creating directory for files
file_path = os.path.join(os.path.dirname(__file__), 'data_files')
try:
    os.mkdir(file_path)
except OSError:
    pass

from bakalarka_web.models import User, File, Category, User_type


@event.listens_for(File, 'after_insert')
def insert_file(mapper, connection, target):
    if target.name:
        try:
            os.makedirs(op.join(file_path, os.path.splitext(target.filename)[0]))
            shutil.move(op.join(file_path, target.filename), op.join(file_path, target.filename))
            with Image(filename=op.join(file_path, target.filename), resolution=200) as img:
                img.save(filename=op.join(file_path,  os.path.splitext(target.filename)[0],
                                          '{}.jpg'.format(os.path.splitext(target.filename)[0])))
        except OSError:
            pass


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
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('login', next=request.url))

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class CategoryView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if not current_user.is_admin():
            CategoryView.can_delete = False
            CategoryView.can_edit = False
            CategoryView.can_create = True

        if current_user.is_admin() or current_user.can_view_category():
            return True
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('login', next=request.url))

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

'''''''''
    def get_query(self): #ukaze len MyFiles
        return self.session.query(self.model).filter(self.model.owner == current_user)

    def get_count_query(self): #ukaze len MyFiles
        return self.session.query(sqla.view.func.count('*')).filter(self.model.owner == current_user)
'''''''''



'''''''''
class FileModelView(ModelView):
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.user = current_user
    column_filters = ('filename', 'beg_display_time', 'end_display_time', 'category', 'owner') #prida moznost 'add filter'
    form_create_rules = ('name', 'defined_name', 'expiration_date', 'category')
    form_edit_rules = ('filename', 'end_display_time', 'category')

    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'name': form.FileUploadField,
        'user': current_user
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'name': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False,
            'allowed_extensions': set(['pdf'])
        }
    }
'''''

class FileModelViewAll(CategoryView):
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.user = current_user

    form_create_rules = ('filename', 'end_display_time', 'category', 'path') #upravim moznost, ktore vyplnim pri vytvoreni suboru
    form_edit_rules = ('filename', 'end_display_time', 'category') #upravim moznosti, ktore vyplnim pri edite
    column_filters = ('filename', 'end_display_time', 'category', 'owner') #pridam filtre

    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'filename': form.FileUploadField,
        #'user': current_user
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'filename': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False,
            'allowed_extensions': set(['jpg'])
        }
    }


admin =Admin(app, name='Electronic notice board'
       )



#admin.add_view(AdminView(User, db.session))
#admin.add_view(CategoryView(Category, db.session))
#admin.add_view(AdminView(User_type, db.session))
#admin.add_view(AdminView(File, db.session))
admin.add_view(FileModelViewAll(File, db.session))



from bakalarka_web import routes