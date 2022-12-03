from collections import UserList
from flask import Blueprint, render_template, abort
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode


plaid_urls = Blueprint('plaid_urls', __name__,
                       template_folder='templates')

# Need to route form to this link

@plaid_urls.route("/create_link_token", methods=['POST'])
def create_link_token():

    # Get the client_user_id by searching for the current user
    user = User.find('user_good')
    client_user_id = user.id

    # Create a link_token for the given user
    request = LinkTokenCreateRequest(
        products=[Products("auth")],
        client_name="Plaid Test App",
        country_codes=[CountryCode('US')],
        redirect_uri='https://domainname.com/oauth-page.html',
        language='en',
        webhook='https://webhook.example.com',
        user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id
        )
    )
    response = client.link_token_create(request)

    # Send the data to the client
    return jsonify(response.to_dict())


access_token = None

item_id = None


@plaid_urls.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():

    global access_token
    public_token = request.form['public_token']
    request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
    response = client.item_public_token_exchange(request)

    # These values should be saved to a persistent database and
    # associated with the currently signed-in user
    access_token = response['access_token']
    item_id = response['item_id']
    return jsonify({'public_token_exchange': 'complete'})
