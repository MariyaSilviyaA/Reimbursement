from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Company, User, Employee,Reimbursement
from . import db
from datetime import datetime
from sqlalchemy.sql import func


views = Blueprint("views", __name__)


# @views.route('/')
# @views.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template('dashboard.html',user=current_user)



@views.route('/')
@views.route('/home')
@login_required
def home():
    companies = Company.query.all()
    return render_template('home.html',companies=companies,user=current_user)

@views.route('/add_company', methods=['GET','POST'])
@login_required
def add_company():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        location= request.form.get('location')
        website = request.form.get('website')

        if not name:
            flash("Please enter Company's name",category='error')
        elif not email:
            flash("Please enter Company's email.",category='error')
        elif not location:
            flash("Please enter Company's location.",category='error')
        else:
            existing_company = Company.query.filter_by(name=name).first()
            if existing_company:
                flash('A Company is with this name is already registered',category='error')
                return redirect(url_for('views.add_company'))
            
            if email:
                existing_company_email=Company.query.filter_by(email=email).first()
                if existing_company_email:
                        flash('A Company with this email already exists.', category='error')
                        return redirect(url_for('views.add_company'))
                else:            
                    new_company = Company(
                        name=name,email=email,location=location,website=website,user_id=current_user.id)
                    db.session.add(new_company)
                    db.session.commit()
                    flash('Company added successfully!', category='success')

                    return redirect(url_for('views.home'))
    return render_template('add_company.html',user=current_user)        


@views.route('/company/<int:company_id>')
@login_required
def company_details(company_id):
    company=Company.query.get(company_id)
    if not company:
        flash('Company doesnot exist',category='error')
        print(f"Company ID: {company_id}")
        return redirect(url_for('views.home'))
    return render_template('company_details.html',company=company,user=current_user,company_id=company_id)


@views.route('/edit_company/<int:company_id>',methods=('GET','POST'))
@login_required
def edit_company(company_id):
   company = Company.query.get_or_404(company_id)
    
   if company.user_id != current_user.id:
        flash('You are not authorized to edit this company.', 'danger')
        return redirect(url_for('views.home'))

   if request.method == 'POST':
        company.name = request.form['name']
        company.email = request.form.get('email')
        company.location = request.form['location']
        company.website = request.form.get('website')
        
        try:
            db.session.commit()
            flash('Company updated successfully!', 'success')
            return redirect(url_for('views.company_details', company_id=company.id))
        except:
            db.session.rollback()
            flash('Error updating the company. Please try again.', 'danger')

   return render_template('edit_company.html', company=company,user=current_user)
        


@views.route('/company/<int:company_id>/delete', methods=['POST'])
@login_required
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    if company.user_id != current_user.id:
        flash('You are not authorized to delete this company.', 'danger')
        return redirect(url_for('views.home'))

    try:
        Employee.query.filter_by(company_id=company_id).delete()
        db.session.delete(company)
        db.session.commit()
        flash('Company and its employees deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting the company. Please try again.', 'danger')
    
    return redirect(url_for('views.home'))


@views.route('/add_employee/<int:company_id>',methods=['GET','POST'])
@login_required
def add_employee(company_id):
    hire_date = None
    if request.method=='POST':

        last_employee = Employee.query.filter_by(company_id=company_id).order_by(Employee.employee_number.desc()).first()
        next_employee_number = 1 if not last_employee else last_employee.employee_number + 1
        first_name= request.form.get('first_name')
        last_name= request.form.get('last_name')
        email=request.form.get('email')
        salary=request.form.get('salary')
        hire_date=datetime.strptime(request.form.get('hire_date'), '%Y-%m-%d').date()
        if not first_name:
            flash("Please enter your first name",category='error')
        elif not last_name:
            flash("Please enter your last name",category='error')
        elif not email:
            flash("Please enter your Mail Id",category='error')
        elif not hire_date:
            flash("Please enter your hire date",category='error')
        else:
            existing_email=Employee.query.filter_by(email=email).first()
            if existing_email:
                flash('An Employee with this email already exists.', category='error')
            else:
                               
                new_employee=Employee(employee_number=next_employee_number, first_name=first_name,last_name=last_name,email=email,salary=float(salary),hire_date=hire_date,company_id=company_id)
                db.session.add(new_employee)
                db.session.commit()
                flash('Employee added successfully!',category='success')
                return redirect(url_for('views.company_details',company_id=company_id))
    return render_template('add_employee.html',user=current_user,company_id=company_id)

@views.route('/company_list',methods=['GET'])
@login_required
def company_list():
    companies=Company.query.all()
    for company in companies:
        total_reimbursement = db.session.query(func.sum(Reimbursement.amount)).filter(Reimbursement.company_id == company.id).scalar()
        company.total_reimbursement = total_reimbursement if total_reimbursement else 0
    return render_template('company_list.html',companies=companies,user=current_user)


@views.route('/company/<int:company_id>/employee/<int:employee_id>', methods=['GET','POST'])
@login_required
def edit_employee(company_id,employee_id):
    company=Company.query.get_or_404(company_id)
    employee=Employee.query.get_or_404(employee_id)

    if company.user_id != current_user.id:
        flash('Permission Denied!','danger')
        return redirect(url_for('views.company_details',company_id=company_id))

    if request.method == 'POST':
        employee.first_name = request.form['first_name']
        employee.last_name = request.form['last_name']
        employee.email = request.form['email']

        try:
            hire_date_str = request.form.get('hire_date')
            salary = request.form.get('salary')

            employee.hire_date =datetime.strptime(hire_date_str,'%d-%m-%Y').date()
            employee.salary=salary

            db.session.commit()
            flash('Employee Updated Successfully.','success')
            return redirect(url_for('views.company_details',company_id=company_id))

        except ValueError as e:
            flash(f'Error processing date: {e}', 'error')




    return render_template('edit_employee.html',company_id=company_id,employee_id=employee_id,user=current_user,employee=employee,company=company)


@views.route('/company/<int:company_id>/employee/<int:employee_id>/delete', methods=['POST'])
@login_required
def delete_employee(company_id, employee_id):
    company = Company.query.get_or_404(company_id)
    employee = Employee.query.get_or_404(employee_id)

    if company.user_id != current_user.id:
        flash('You do not have permission to delete this employee.', 'danger')
        return redirect(url_for('views.company_details', company_id=company_id))

    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully.', 'success')
    return redirect(url_for('views.company_details', company_id=company_id,user=current_user))


@views.route('/employees')
@login_required
def employees():
    employees=Employee.query.all()
    return render_template('employees.html',employees=employees,user=current_user)


@views.route('/company/<int:company_id>/employee/<int:employee_id>/reimbursement', methods=['GET', 'POST'])
@login_required
def claim_reimbursement(company_id, employee_id):
    company = Company.query.get_or_404(company_id)
    employee = Employee.query.get_or_404(employee_id)

    if employee.company_id != company.id:
        flash('Invalid employee-company relationship.', 'danger')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        date_of_expense = datetime.strptime(request.form['date_of_expense'], '%Y-%m-%d').date()
        product = request.form['product']
        amount = request.form['amount']
        description = request.form.get('description', '')
        
        


        reimbursement = Reimbursement(
            employee_id=employee.id,
            company_id=company.id,
            date_of_expense=date_of_expense,
            product=product,
            amount=float(amount),
            description=description
        )
        db.session.add(reimbursement)
        db.session.commit()
        flash('Reimbursement claimed successfully!', 'success')
        return redirect(url_for('views.company_details',company_id=company.id))

    return render_template('employee_reimbursements.html',user=current_user, employee=employee, company=company,employee_id=employee_id)

# @views.route('/add-claim', methods=['POST'])
# @login_required
# def add_claim():
#         company_id = request.form.get('company_id')
#         employee_id = request.form.get('employee_id')
#         date_of_expense = request.form.get('date_of_expense')
#         product = request.form.get('product')
#         amount = float(request.form.get('amount'))
#         description = request.form.get('description')

#         # Validate and process the form data
#         company = Company.query.get(company_id)
#         employee = Employee.query.get(employee_id)
        
#         if not company or not employee:
#             flash('Invalid company or employee selected', 'danger')
#             return redirect(url_for('views.company_list'))

#         reimbursement = Reimbursement(
#                 company_id=company_id,
#                 employee_id=employee_id,
#                 date_of_expense=date_of_expense,
#                 product=product,
#                 amount=amount,
#                 description=description
#             )
            
#         db.session.add(reimbursement)
#         db.session.commit()

#         flash('Reimbursement claimed successfully', 'success')
#         return redirect(url_for('views.list_all_reimbursements'))

#     return render_template('add_claim.html',user=current_user,company=company,employee=employee)




@views.route('/reimbursements')
@login_required
def list_all_reimbursements():
    reimbursements = Reimbursement.query.all()
    companies = Company.query.all()
    employees = Employee.query.all()
    
    return render_template('reimbursements.html', reimbursements=reimbursements,user=current_user,employee=employees)

# @views.route('/add_claim', methods=['GET', 'POST'])
# def add_claim():
#     breakpoint()
#     if request.method == 'POST':
#         company_id = request.form.get('company_id')
#         employee_id = request.form.get('employee_id')
#         date_of_expense = request.form.get('date_of_expense')
#         product = request.form.get('product')
#         amount = request.form.get('amount')
#         description = request.form.get('description', '')

#         if not company_id or not employee_id or not amount:
#             flash('All fields are required.')
#             return redirect(url_for('add_claim'))

#         try:
#             company_id = int(company_id)
#             employee_id = int(employee_id)
#             amount = float(amount)
#             date_of_expense = datetime.strptime(date_of_expense, '%Y-%m-%d').date()
#         except ValueError:
#             flash('Invalid input. Please ensure all fields are filled out correctly.')
#             return redirect(url_for('add_claim'))

#         # Fetch the employee and company details
#         employee = Employee.query.filter_by(id=employee_id, company_id=company_id).first()
#         company = Company.query.get_or_404(company_id)

#         if not employee:
#             flash('Invalid employee or company ID.')
#             return redirect(url_for('add_claim'))

#         reimbursement = Reimbursement(
#             employee_id=employee_id,
#             company_id=company_id,
#             date_of_expense=date_of_expense,
#             product=product,
#             amount=amount,
#             description=description
#         )
#         db.session.add(reimbursement)
#         db.session.commit()
#         flash('Reimbursement claimed successfully!', 'success')
#         return redirect(url_for('list_all_reimbursements'))

#     # For GET request, pass only relevant context
#     return render_template('add_claim.html', user=current_user)