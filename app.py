from flask import Flask,render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date,datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
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
    expenses=Expense.query.all()
    total=sum(e.amount for e in expenses)
    return render_template("index.html",expenses=expenses, total=total, today=today)

@app.route("/add",methods=["POST"])
def add():
    desc=request.form["desc"]
    amount=request.form["amount"]
    category=request.form["category"]
    expense_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()   
    new_expense=Expense(description=desc, amount=amount, category=category, date=expense_date)
    db.session.add(new_expense)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    expense=Expense.query.get(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
   app.run(debug=True,port=4848) 