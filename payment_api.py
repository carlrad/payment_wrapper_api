import os
import gocardless_pro
import requests
import stripe
import os
from flask import Flask, redirect, request, render_template

# to do - change html to flask render templates, copy stripe structure for GC and add buttons to the checkout html page to trigger different payment options

# This is your real test secret API key.
stripe.api_key =os.environ['STRIPE_ACCESS_TOKEN']

client = gocardless_pro.Client(
    access_token=os.environ['GC_ACCESS_TOKEN'],
    environment='sandbox'
)

app = Flask(__name__,
            static_url_path='',
            static_folder='.')

mandate_redirect_flow = client.redirect_flows.create(
    params={
        "description" : "Ale Casks", # This will be shown on the payment pages
        "session_token" : "dummy_session_token", # Not the access token
        "success_redirect_url" : "https://developer.gocardless.com/example-redirect-uri/",
        "prefilled_customer": { # Optionally, prefill customer details on the payment page
            "given_name": "Tim",
            "family_name": "Rogers",
            "email": "tim@gocardless.com",
            "address_line1": "338-346 Goswell Road",
            "city": "London",
            "postal_code": "EC1V 7LQ"
        }
    }
)

DD_payment = client.payments.create(
    params={
        "amount" : 1000, # 10 GBP in pence
        "currency" : "GBP",
        "links" : {
            "mandate": "MD0008WJQB3EQW"
                     # The mandate ID from the last section - note updtate this as a variable
        },
        "metadata": {
          "invoice_number": "001"
        }
    }, headers={
        'Idempotency-Key' : 'random_key',
})

DD_subscription = client.subscriptions.create(
    params={
        "amount" : 1500, # 15 GBP in pence
        "currency" : "GBP",
        "interval_unit" : "monthly",
        "day_of_month" : "5",
        "links": {
            "mandate": "MD0008WJQB3EQW"
                     # Mandate ID from the last section
        },
        "metadata": {
            "subscription_number": "ABC1234"
        }
    }, headers={
        'Idempotency-Key': "random_subscription_specific_string"
})

# billing_request = client.billing_requests.create(params={
#   "redirect_uri": "https://my-company.com/landing",
#   "links": {
#     "billing_request": "BRQ123"
#   }
# })

# stripe card payments
YOUR_DOMAIN = 'http://localhost:4242'
@app.route('/')
def index():
    return render_template('index.html')#, key=stripe_keys['publishable_key'])

@app.route("/success")
def success():
    return render_template("success.html")

@app.route('/cancelled')
def cancelled():
    return render_template("cancelled.html")

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[
              'card',
            ],
            line_items=[
                {
                    # TODO: replace this with the `price` of the product you want to sell
                    'price': 'price_1JNPTWBcB9Mmkk7XinyXCO87',
                    'quantity': 1,
                },
            ],
            mode='payment',
            #success_url=YOUR_DOMAIN + "success?session_id={CHECKOUT_SESSION_ID}",
            #cancel_url=YOUR_DOMAIN + 'cancelled',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)
if __name__ == '__main__':
    app.run(port=4242)

# Hold on to this ID - we'll need it when we
# "confirm" the redirect flow later
# print("ID: {} ".format(redirect_flow.id))
# print("URL: {} ".format(redirect_flow.redirect_url))
