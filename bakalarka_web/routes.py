from flask import render_template, flash, redirect, url_for, session, request
from bakalarka_web import app, db, bcrypt
from bakalarka_web.models import file_category, User, File, Category, User_type
from bakalarka_web.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required #current potrebne na osetrenie routu po LOGINe


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/home")
def home1():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST']) #musim pridat list povolenych metod, daljem musim skontrolovat validnost dat a ci mam POST data
def register():
    if current_user.is_authenticated: #divne chovanie
        return redirect(url_for('home'))
    form=RegistrationForm(request.form)
    #if form.validate_on_submit():  #flash message umoznuje poslat one-time alert, musim importovat(flash a mozem pridat spravu ktora s avypise pri uspechu
    if request.method == 'POST' and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') #chcem to mat ako string a nie BYTES, ulozim si zakodovane heslo na vlozene heslo uzivatelom
        user = User (username=form.username.data, VUT_id=form.VUT_id.data, email=form.email.data, password=hashed_password) #vytvorim instanciu Usera a ulozim do nho zadane data
        db.session.add(user) #pridam usera do DB a commitnem
        db.session.commit()
        flash(f'Account was created for {form.username.data}', 'success') #f string(vypise meno uzivatela) nova metoda ako formatovat string v python 3.6+; rozlisovat rozne typy alertov v BOOTSTRAPE, druhy parameter success
        return redirect(url_for('login'))    #redirect po uspecnom zaregistrovani
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST']) # POST = pouzivane na posielanie dat an server na vytvorenie/update. GET = pouziva sa an vyziadanie dat
def login():
    if current_user.is_authenticated:   #ak prihlaseny
        return redirect(url_for('account'))

    form=LoginForm()
    #if form.validate_on_submit():
    if request.method == 'POST' and form.validate_on_submit():
          user = User.query.filter_by(VUT_id = form.VUT_id.data).first()  #kontrola ci dany user existuje ( VUT_id ktore zadal uzivatel )
          if user and bcrypt.check_password_hash(user.password, form.password.data):  #kontrola, ci user existuje a ci heslo sedi s heslom v DB, najskor kontrolujem HASH password a druhe heslo je heslo zadane uzivatelom
                login_user(user, remember = form.remember.data) #ked existuje user a hesla odpovedaju, chceme lognut usera. Pouzijeme flask_login extension(musim importovat login user function ), remember je True/False value
                #next_page = request.args.get('next') #args je dictionary a ja nehcem pristupovat k next pomocou [] a klucovych nazvov lebo to hodi error ked kluc neexistuje, nutne pouzit GET metodu lebo ak neexistuje tak vrati None ak next neexistuje
                #return redirect(next) if next_page else redirect(url_for('home')) #ternaty condition, redirect na  next page ak next page existuje ale ak je None alebo false  redirect na home
                return redirect('/admin')
          else:
            flash(f'Error in VUT_ID or PASSWORD. You cannot be logged in', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout') # POST = pouzivane na posielanie dat an server na vytvorenie/update. GET = pouziva sa an vyziadanie dat
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account') # POST = pouzivane na posielanie dat an server na vytvorenie/update. GET = pouziva sa an vyziadanie dat
@login_required #dalsi decorator, cize nasa extension vie, ze sa potrebujeme prihlasit aby sme mohli sit do accountu
def account():
    return render_template('account.html', title='Account')






