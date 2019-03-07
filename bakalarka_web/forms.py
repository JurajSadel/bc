from flask_wtf import FlaskForm
from bakalarka_web.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError #StringField meno uzivatela, email Password heslo
from wtforms.validators import DataRequired, Length, Email, EqualTo  #kvoli validatorom, DataRequired->nemoze ostat nevyplnene,Length povolena dlzka mena
                                                            #Email kvoli validnemu emailu, na potvrdenie emailu EqualTo

#registration form class
class RegistrationForm(FlaskForm):       #classa RegistrationForm dedi z FlaskForm
    #vnutri=within budeme mat viacere rozdielne formfields
    #user name bude stringField -> nie je importovane z FlaskWDF package ale z FlaskWTF package tiez naisntalovane s pip install flask-wtf
    username=StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=5,max = 20)])  #prvy parameter Username bude pouzity ako label v HTML, musime doplnit aby museli nieco zapisat,
                                        # dlzka mena (validators dalsi argument)-> list toho, co chceme kontrolovat, tiez budu importovane classy
    VUT_id=StringField('VUT ID', validators=[DataRequired(), Length(min=4,max = 6)])
    email=StringField('Email',
                      validators=[DataRequired(), Email(), Length(max=50)])
    password=PasswordField('Password',
                           validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',
                                   validators=[DataRequired(), EqualTo('password')]) #password confirmation
    #Vytvorenie submitu
    submit=SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:  #potrebujem skontorlovat, ci novozadane meno uz nie je v DB, najprv import db
            raise ValidationError('Username already exists!') #musim importovat

    def validate_VUT_id(self, VUT_id):
        user = User.query.filter_by(VUT_id=VUT_id.data).first()
        if user:  #potrebujem skontorlovat, ci novozadane meno uz nie je v DB, najprv import db
            raise ValidationError('VUT_id already exists!') #musim importovat

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:  #potrebujem skontorlovat, ci novozadane meno uz nie je v DB, najprv import db
            raise ValidationError('Email already exists!') #musim importovat

    #________KONIEC RegistratinFormy

#LoginForm
class LoginForm(FlaskForm):
    VUT_id = StringField('VUT ID', validators=[DataRequired(), Length(min=4, max=6)])
    #email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')