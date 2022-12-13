'''

main.py

This code is used by flask to open particular pages on the website. 

At localhost:5000, the homepage will be loaded. If the user is not logged in, the page will
not fully load and a link will be provided to enable the user to login.

At the login page (localhost:5000/login) the user can attempt to login. If their attempt fails,
it will be recorded in a text file called failed_loggins.txt and the user will be informed.
Once the user successfully logs in, they will be rerouted to the homepage.

If the user does not have an account, there is a link on the loggin page to the account
registration page (localhost:5000/register). There, the user can provide a username and
password for their new account. If the username is taken or the password provided is inadequate,
the user will be informed. Once the user successfully creates an account, they will be logged
in and rerouted to the homepage.

The homepage (localhost:5000) provides information about musical modes (the subject of
the website). It also displays the user's username plus links to logout and change their password.

The link to change the user's password leads to localhost:5000/update_password. Each password the
user suggests will be checked for its commonality and complexity. When a valid password is
suggested, the password will be updated, a success message will appear, and the user will be
provided a link back to the homepage.

'''
import datetime
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from passlib.hash import sha256_crypt
import yaml
import os
import matplotlib.pyplot as plt
import time

app = Flask(__name__)
app.secret_key = "CMSC495"



@app.route('/')
def homepage():
    '''
    Loads the homepage
    '''
    # Checks if the user is logged in
    if 'username' in session:
        history = get_history()
        print('history: ' + str(history))
        transactions = history['transactions']
        categories = history['categories']

        # Checking if there is any financial history to display, if not then show a message on the page directing
        # the user where to get started
        if len(transactions) == 0:
            return render_template('homepage.html', today=datetime.datetime.now(), username=session['username'],
                                   empty='yes', income=None, expenses=None, net=None)

        # Calculating the income and expenses of the user's recorded financial history
        income = 0
        expenses = 0
        income_categories = categories.copy()
        expense_categories = categories.copy()
        income_category_amounts = [0] * len(categories)
        expense_category_amounts = [0] * len(categories)
        for transaction in transactions:
            category = transaction['category']
            amount = transaction['amount']
            if transaction['type'] == 'deposit':
                income += amount
                index = categories.index(category)
                income_category_amounts[index] += amount
            else:
                expenses += amount
                index = categories.index(category)
                expense_category_amounts[index] += amount

        print('categories: ' + str(categories))
        print('income_categories: ' + str(income_categories))
        print('income_category_amounts: ' + str(income_category_amounts))
        print('expense_categories: ' + str(expense_categories))
        print('expense_category_amounts: ' + str(expense_category_amounts))

        for category in categories:
            if category in income_categories:
                index = income_categories.index(category)
                if income_category_amounts[index] == 0:
                    income_category_amounts.pop(index)
                    income_categories.pop(index)
            if category in expense_categories:
                index = expense_categories.index(category)
                if expense_category_amounts[index] == 0:
                    expense_category_amounts.pop(index)
                    expense_categories.pop(index)

        # Create and save a bar graph that compares income vs expenses
        x = ['Income', 'Expenses']
        y = [income, expenses]
        print('x: ' + str(x))
        print('y: ' + str(y))

        f1 = plt.figure()
        plt.bar(x, y, color='g')
        plt.title("Income vs. Expenses")
        plt.ylabel("US Dollars $")
        plt.savefig('static/bar_graph.png', dpi=300, bbox_inches='tight')
        #plt.cla()

        plt.clf()
        f2 = plt.figure()
        plt.pie(income_category_amounts, labels=income_categories)
        plt.title("Income Category Breakdown")
        plt.savefig('static/pie_chart1.png', dpi=300, bbox_inches='tight')

        plt.clf()
        f3 = plt.figure()
        plt.pie(expense_category_amounts, labels=expense_categories)
        plt.title("Expense Category Breakdown")
        plt.savefig('static/pie_chart2.png', dpi=300, bbox_inches='tight')
        plt.cla()

        return render_template('homepage.html', today=datetime.datetime.now(), username=session['username'],
                               empty=None, income=str(income), expenses=str(expenses), net=str(income-expenses))

    # If not, links the user to the login page
    return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"



@app.route('/login', methods=['GET', 'POST'])
def login_page():
    '''
    Loads the login page
    '''
    # Loads the login page
    if request.method == 'GET':
        return render_template('login.html', error=None)

    # Checks the username and password provided
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = valid_user(username, password)

        # If the login failed, logs the failed attempt and shows the user and error message
        # with the reason for the failed login
        if error != "":
            # Adds failed loggin attempt to the logger
            with open('static/failed_loggins.txt', "a", encoding="utf8") as file:
                date_time = str(datetime.datetime.now())
                ip_address = request.remote_addr
                file.writelines(username + ', ' + date_time + ', ' + ip_address + '\n')

            return render_template('login.html', error=error)

        session['username'] = request.form['username']
        return redirect('/')



@app.route('/register', methods=['GET', 'POST'])
def registration_page():
    '''
    Loads the registration page
    '''
    # Loads the registration page
    if request.method == 'GET':
        return render_template('register.html', error=None)

    # Checks the username and password provided
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Checks if the user is alread registered
        if is_registered(username):
            error = "There is already an account with that username."
            return render_template('register.html', error=error)

        # Checks if the password is common enough
        if not uncommon_password(password):
            error = 'That password is too commonly used. Please choose another.'
            return render_template('register.html', error=error)

        error = complex_password(password)

        # Checks if the password is complex enough
        if error != "":
            return render_template('register.html', error=error)

        password_hash = sha256_crypt.hash(password)

        # Opens the account file and stores the new username and password
        with open('static/accounts.txt', "a", encoding="utf8") as file:
            file.writelines(username + '\n')
            file.writelines(password_hash + '\n')

        # Logs in and redirects to homepage
        session['username'] = request.form['username']
        return redirect('/')



def is_registered(username):
    '''
    Checks if the given username already exists within the account file
    '''
    # Opens the account file
    with open('static/accounts.txt', encoding="utf8") as file:
        i = 1

        # Goes through each line of the file
        for line in file:
            line = line.strip()

            # Usernames are on odd lines so, compares every other line to the
            # given username to see if it is a match
            if i%2 != 0:

                # If the line is a match, then the user is already registered
                if line == username:
                    return True
            i += 1

    return False



def uncommon_password(password):
    '''
    Checks if the password is one of the common passwords listed in CommonPasswords.txt
    '''
    with open('static/CommonPasswords.txt', encoding="utf8") as file:
        return password not in file.read()



def complex_password(password):
    '''
    Checks if the given password is complex enough
    A password complexity should be enforced to include at least 8 characters in length, and
    include at least 1 uppercase character, 1 lowercase character, 1 number and 1 special character
    '''
    # Checks if the length is valid
    if len(password) < 8 :
        return "Your password must be at least 8 characters long."

    uppercase_included = False
    lowercase_included = False
    number_included = False
    special_included = False


    # Iterates through each character in the password to check if the password
    # includes all necessary characters
    for character in password:

        # Checks if the current character is a space
        if character.isspace():
            return "Please, do not include spaces in your password."

        # Checks if the current character is uppercase
        if character.isupper():
            uppercase_included = True

        # Checks if the current character is lowercase
        elif character.islower():
            lowercase_included = True

        # Checks if the current character is a digit
        elif character.isdigit():
            number_included = True

        # if the character has not yet been identified, then it is a special character
        else:
            special_included = True


    error = ""

     #If there is no uppercase character, adds to error message
    if not uppercase_included:
        error += "Your password must include at least one uppercase character."

    # If there is no lowercase character, adds to error message
    if not lowercase_included:
        error += " Your password must include at least one lowercase character."

    # If there is no digit, adds to error message
    if not number_included:
        error += " Your password must include at least one digit."

    # If there is no special character, adds to error message
    if not special_included:
        error += " Your password must include at least one special character."

    return error



def valid_user(username, password):
    '''
    Checks if the given username and password belong to an existing account
    '''
    # Opens the account file
    with open('static/accounts.txt', encoding="utf8") as file:
        i = 1
        found_user = False

        # Goes through each line of the file
        for line in file:
            line = line.strip()

            if found_user:
                try:
                    if sha256_crypt.verify(password, line):
                        return ""
                except ValueError:
                    return "Incorrect Password."

            # Usernames are on odd lines so, compares every other line to the
            # given username to see if it is a match
            if i%2 != 0:
                # If the line is a match, then the user is already registered
                if line == username:
                    found_user = True
            i += 1

    return "Username or Password is Incorrect."



@app.route('/logout')
def logout():
    '''
    Logs the user out and returns them to the login page
    '''
    session.pop('username', None)
    return redirect('/')



@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    '''
    Loads the page which will enable a logged in user to update their password
    '''
    username = username=session['username']

    # Loads the update password page
    if request.method == 'GET':
        return render_template('update_password.html', username=username, error=None, success=None)

    # Processes the new password
    if request.method == 'POST':
        password = request.form['password']

        # Checks if the password is too common
        if not uncommon_password(password):
            error = 'That password is too commonly used. Please choose another.'
            return render_template('update_password.html', username=username,\
                error=error, success=None)

        error = complex_password(password)

        # Checks if the password is complex enough
        if error != "":
            return render_template('update_password.html', username=username,\
                error=error, success=None)


        password_hash = sha256_crypt.hash(password)

        # Opens the account file and replaces the old password with the new one
        # First finds the username, marks username_found = 1, then the following line
        # where the old password is will be replaced with the new password
        with open('static/accounts.txt', "r+", encoding="utf8") as fileworker:
            file = fileworker.readlines()
            fileworker.seek(0)
            username_found = 0

            # Copies the lines from the old copy of the file to a new copy except the
            # line with the old password is replaced with the new one
            for line in file:

                # Checks if we are still searching for the username
                if username_found >= 0:

                    # Replaces the old password with the new one
                    if username_found:
                        fileworker.write(password_hash + "\n")
                        username_found = -1

                    else:
                        # Checks if the username has been found
                        # If it is, marks that it has been found so the password on
                        # the next line can be replaced with the new one
                        if username in line:
                            username_found = 1

                        fileworker.write(line)

                # If not, just continues copying the remaining lines to the file
                else:
                    fileworker.write(line)

            fileworker.truncate()

        return render_template('update_password.html', username=username, error=None, success='yes')


def get_history_filepath():
    username = session['username']
    return os.getcwd() + '\\account_histories\\' + username + '_history.yml'


def get_history():
    filepath = get_history_filepath()
    if os.path.exists(filepath):
        with open(filepath) as f:
            history = yaml.safe_load(f)
        return history

    return {'transactions' : [], 'categories' : []}


# Route for update_financial_history.html
@app.route('/update_financial_history', methods=['GET', 'POST'])
def update_financial_history():
    username = session['username']
    history = get_history()

    # If not a form submission then go through to the page
    if request.method == 'GET':
        return render_template('update_financial_history.html', username=username, categories=history['categories'], \
                               error=None, success=None)

    # If a form submission, evaluate the form submission
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        amount = request.form['amount']

        if category not in history['categories']:
            history['categories'].append(category)

        # Checking if all fields have been filled in
        if title == '' or category == '' or amount == '':
            return render_template('update_financial_history.html', username=username, categories=history['categories'], \
                                   error='Error! Please fill in all fields!', success=None)

        # Attempting to convert the amount the user entered for this transaction to a float
        try:
            amount = float(amount)

        # If the user entered a non float, then display an error on the page
        except:
            return render_template('update_financial_history.html', username=username, categories=history['categories'], \
                                   error='Error! Please enter a numeric value for the amount!', success=None)

        transaction = {}
        transaction['type'] = request.form['type']
        transaction['title'] = title
        transaction['amount'] = amount
        transaction['category'] = category
        transaction['month'] = int(request.form['month'])
        transaction['day'] = int(request.form['day'])
        transaction['year'] = int(request.form['year'])

        history['transactions'].append(transaction)
        if category not in history['categories']:
            history['categories'].append(category)

        # Writing the new transaction to the user's financial history file
        with open(get_history_filepath(), 'w') as f:
            yaml.dump(history, f)

        return render_template('update_financial_history.html', username=username, categories=history['categories'], \
                               error=None, success='yes')
