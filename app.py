from flask import Flask,render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date,datetime
from flask import Flask, render_template, request, redirect, flash


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'your-secret-key'
db=SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(120), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    today = date.today().strftime("%Y-%m-%d")
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = Expense.query
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
       
    new_expense=Expense(description=desc, amount=amount, category=category, date=expense_date)
    db.session.add(new_expense)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    expense=Expense.query.get(id)
    if expense==None:
        return redirect("/")
    db.session.delete(expense)
    db.session.commit()
    return redirect("/")

@app.route("/edit/<int:id>")
def edit(id):
    expense = Expense.query.get(id)
    return render_template("edit.html", expense=expense)

@app.route("/update/<int:id>", methods=["POST"])
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
   app.run(debug=True,port=4848) 