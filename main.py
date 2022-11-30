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
from utils import *

app = Flask(__name__)
app.register_blueprint('plaid_urls')
app.secret_key = "CMSC495"



@app.route('/')
def homepage():
    '''
    Loads the homepage
    '''
    try:
      request = AccountsGetRequest(
          access_token=access_token
      )
      accounts_response = client.accounts_get(request)
    except plaid.ApiException as e:
      response = json.loads(e.body)
      return jsonify({'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}})

    response = jsonify(accounts_response.to_dict()

    # Checks if the user is logged in
    if 'username' in session:
        return render_template('homepage.html', today=datetime.datetime.now(),\
            username=session['username'], response)
    else:
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
