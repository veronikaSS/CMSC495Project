from flask import Blueprint, render_template, abort
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

plaid_urls = Blueprint('plaid_urls', __name__,
                        template_folder='templates')

@plaid_urls.route("/create_link_token", methods=['POST'])
def create_link_token():

    # Get the client_user_id by searching for the current user
    user = User.find(...)
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
