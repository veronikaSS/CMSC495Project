import plaid
import settings as settings
from plaid.api import plaid_api

# Available environments are
# 'Production'
# 'Development'
# 'Sandbox'
def plaid_obj():
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET_KEY_DEV,
        }
    )

    print("Client ID: ",settings.PLAID_CLIENT_ID)
    print("Secret Key: ",settings.PLAID_SECRET_KEY_DEV)
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    print("Client Response: ", client)
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

def get_transactions(request):
	user = request.user

	if user.is_authenticated:
		transactions = []
		plaid_items = user.plaiditem_set.all()

		timespan_weeks = 4 * 24 # Plaid only goes back 24 months
		start_date = '{:%Y-%m-%d}'.format(datetime.now() + timedelta(weeks=(-timespan_weeks)))
		end_date = '{:%Y-%m-%d}'.format(datetime.now())

		for item in plaid_items:
			try:
				access_token = item.access_token

				data = {
					'client_id': PLAID_CLIENT_ID,
					'access_token': access_token,
					'secret': PLAID_SECRET,
					'start_date': start_date,
					'end_date': end_date
				}

				response = client.Transactions.get(access_token,
									start_date=start_date,
									end_date=end_date)

				transactions = response['transactions']
					
				accounts = response['accounts']
				error = None

				for account in accounts:
					try:
						existing_acct = user.account_set.get(plaid_account_id=account['account_id'])
						continue
					except:
						new_acct = Account()
						new_acct.plaid_account_id = account['account_id']
						new_acct.balances = account['balances']
						new_acct.mask = account['mask']
						new_acct.name = account['name']
						new_acct.official_name = account['official_name']
						new_acct.subtype = account['subtype']
						new_acct.account_type = account['type']
						new_acct.user = user
						new_acct.save()

				while len(transactions) < response['total_transactions']:
					response = client.Transactions.get(access_token,
											start_date=start_date,
											end_date=end_date,
											offset=len(transactions)
											)
					transactions.extend(response['transactions'])
				
				categorize_transactions(transactions)

				for transaction in transactions:
					try:
						existing_trans = user.transaction_set.get(transaction_id=transaction['transaction_id'])
						builtin_cat = Category.objects.get(pk=transaction['builtin_cat_id'])
						existing_trans.builtin_category = builtin_cat
						existing_trans.save()
						continue
					except Transaction.DoesNotExist:
						new_trans = Transaction()
						new_trans.account = user.account.get(plaid_account_id=transaction['account_id'])
						new_trans.account_owner = transaction['account_owner']
						new_trans.amount = transaction['amount']
						new_trans.authorized_date = transaction['authorized_date']

						builtin_cat = Category.objects.get(pk=transaction['builtin_cat_id'])
						new_trans.builtin_category = builtin_cat

						new_trans.category = transaction['category']
						new_trans.category_id = transaction['category_id']
						new_trans.date = datetime.strptime(transaction['date'], '%Y-%m-%d')
						new_trans.iso_currency_code = transaction['iso_currency_code']
						new_trans.location = transaction['location']
						new_trans.merchant_name = transaction['merchant_name']
						new_trans.name = transaction['name']
						new_trans.payment_meta = transaction['payment_meta']
						new_trans.payment_channel = transaction['payment_channel']
						new_trans.pending = transaction['pending']
						new_trans.pending_transaction_id = transaction['pending_transaction_id']
						new_trans.transaction_code = transaction['transaction_code']
						new_trans.transaction_id = transaction['transaction_id']
						new_trans.transaction_type = transaction['transaction_type']
						new_trans.unofficial_currency_code = transaction['unofficial_currency_code']
						new_trans.user = user
						new_trans.save()
			except Exception as e:
				print(e)
				# error = {'display_message': 'You need to link your account.' }
		json.dumps(transactions, sort_keys=True, indent=4)
		return HttpResponseRedirect('/',{'error': error, 'transactions': transactions})
	else:
		redirect('/')