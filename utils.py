import plaid
import settings
from plaid.api import plaid_api

# Available environments are
# 'Production'
# 'Development'
# 'Sandbox'
def plaid_obj(self):
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET_KEY_DEV,
        }
    )

    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)

    return client



#Authentication
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
    A password complexity should be enforced to include at least 12 characters in length, and
    include at least 1 uppercase character, 1 lowercase character, 1 number and 1 special character
    '''
    # Checks if the length is valid
    if len(password) < 12 :
        return "Your password must be at least 12 characters long."

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
