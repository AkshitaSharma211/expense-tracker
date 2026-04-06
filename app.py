from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import date,datetime
from flask import Flask, render_template, request, redirect, flash
from flask_login import UserMixin


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'your-secret-key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db=SQLAlchemy(app)



class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(UserMixin, db.Model):    
    id = db.Column(db.Integer, primary_key=True )
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(256), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.')
            return redirect('/register')

        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.')
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.')
            return redirect('/login')

        login_user(user)
        return redirect('/')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

with app.app_context():
    db.create_all()

@app.route("/")
@login_required
def index():
    today = date.today().strftime("%Y-%m-%d")
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = Expense.query.filter_by(user_id=current_user.id)
    if start_date and end_date:
        query = query.filter(Expense.date.between(start_date, end_date))

    expenses = query.order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)
    category_totals = {}
    for expense in expenses:
        if expense.category not in category_totals:
            category_totals[expense.category] = expense.amount
        else:
            category_totals[expense.category] += expense.amount
    
    return render_template("index.html", expenses=expenses, total=total, today=today, category_totals=category_totals, start_date=start_date,
                           end_date=end_date)

@app.route("/add",methods=["POST"])
@login_required
def add():
    desc=request.form["desc"]
    amount=request.form["amount"]
    category=request.form["category"]
    expense_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()   
    if not desc:
        flash("Add a Description about the expense")
        return redirect("/")
    
    try:
        amount = float(amount)
    except ValueError:
         flash("Amount should be a valid numeric ")
         return redirect("/")
    if amount<=0:
        flash("Amount should be positive")
        return redirect("/")
       
    new_expense = Expense(description=desc, amount=amount, category=category, date=expense_date, user_id=current_user.id)  
    db.session.add(new_expense)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    expense=Expense.query.get(id)
    if expense==None:
        return redirect("/")
    db.session.delete(expense)
    db.session.commit()
    return redirect("/")

@app.route("/edit/<int:id>")
@login_required
def edit(id):
    expense = Expense.query.get(id)
    return render_template("edit.html", expense=expense)

@app.route("/update/<int:id>", methods=["POST"])
@login_required
def update(id):
    expense = Expense.query.get(id)
    if expense is None:
        return redirect("/")
    
    expense.description = request.form["desc"]
    expense.amount = float(request.form["amount"])
    expense.date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
    expense.category = request.form["category"]
    
    db.session.commit()
    return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
       return render_template("404.html"), 404

if __name__ == "__main__":
   app.run(debug=True,port=3000) 