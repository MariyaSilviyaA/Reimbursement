from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),nullable=False, unique=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150),nullable=False)
    companies = db.relationship('Company', backref='owner', lazy=True)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=True, unique=True)
    location = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    employees = db.relationship('Employee', backref='company', lazy=True)



class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    salary = db.Column(db.Float, nullable=True)
    hire_date = db.Column(db.Date, nullable=False)
    employee_number=db.Column(db.Integer,nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    
class Reimbursement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)    
    date_of_expense = db.Column(db.DateTime(timezone=True), server_default=func.now())
    product = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

    employee = db.relationship('Employee', backref=db.backref('reimbursement_records', lazy=True))
    company = db.relationship('Company', backref=db.backref('reimbursements', lazy=True))