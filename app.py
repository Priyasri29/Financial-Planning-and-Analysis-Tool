from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_pymongo import PyMongo
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

# Flask-PyMongo configuration
app.config['MONGO_URI'] = 'mongodb+srv://2033034mdcs:<2NGTJDWh7Gf5CTVI>@clusterminorproject.pjrqx.mongodb.net/?retryWrites=true&w=majority&appName=ClusterMinorProject'
mongo = PyMongo(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        company_name = request.form['company_name']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if the company already exists
        existing_company = mongo.db.companies.find_one({'company_name': company_name})
        if existing_company:
            flash('Company already exists.')
            return redirect(url_for('signup'))

        mongo.db.companies.insert_one({'company_name': company_name, 'password': hashed_password})
        flash('Company registered successfully!')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        company_name = request.form['company_name']
        password = request.form['password']

        # Verify company
        company = mongo.db.companies.find_one({'company_name': company_name})
        if company and bcrypt.check_password_hash(company['password'], password):
            user = User(company_name)
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.')

    return render_template('login.html')

@app.route('/company_info', methods=['GET', 'POST'])
@login_required
def company_info():
    if request.method == 'POST':
        location = request.form['location']
        address = request.form['address']
        num_people = int(request.form['num_people'])
        people_details = []

        for i in range(num_people):
            person = {
                'name': request.form.getlist('name[]')[i],
                'designation': request.form.getlist('designation[]')[i],
                'phone': request.form.getlist('phone[]')[i],
                'email': request.form.getlist('email[]')[i]
            }
            people_details.append(person)

        mongo.db.companies.update_one(
            {'company_name': current_user.id},
            {'$set': {'location': location, 'address': address, 'num_people': num_people, 'people_details': people_details}}
        )

        flash('Company details updated successfully!')
        return redirect(url_for('home'))

    return render_template('company_info.html')

@app.route('/home')
@login_required
def home():
    company = mongo.db.companies.find_one({'company_name': current_user.id})
    return render_template('home.html', company=company)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        location = request.form['location']
        address = request.form['address']
        num_people = int(request.form['num_people'])
        people_details = []

        for i in range(num_people):
            person = {
                'name': request.form.getlist('name[]')[i],
                'designation': request.form.getlist('designation[]')[i],
                'phone': request.form.getlist('phone[]')[i],
                'email': request.form.getlist('email[]')[i]
            }
            people_details.append(person)

        mongo.db.companies.update_one(
            {'company_name': current_user.id},
            {'$set': {'location': location, 'address': address, 'num_people': num_people, 'people_details': people_details}}
        )

        flash('Profile updated successfully!')
        return redirect(url_for('home'))

    company = mongo.db.companies.find_one({'company_name': current_user.id})
    return render_template('profile.html', company=company)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
