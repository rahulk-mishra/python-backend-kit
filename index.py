import json
from flask import Flask, request, jsonify, render_template
# from expresscheckout-python-client.juspay import JuspaySDK
from datetime import datetime
import random
import time

# import importlib.util
import secrets
import sys
import os
module_path = os.path.abspath("expresscheckout-python-client")

if module_path not in sys.path:
    sys.path.insert(0, module_path)

from juspay import JuspaySDK

# with open('config.json') as f:
#     config = json.load(f)

# MERCHANT_ID = config['MERCHANT_ID']
# CLIENT_ID = config['PAYMENT_PAGE_CLIENT_ID']
# BASE_URL = config['BASE_URL']
# KEY_ID = config['KEY_UUID']
# PUBLIC_KEY = config['PUBLIC_KEY_PATH']
# PRIVATE_KEY = config['PRIVATE_KEY_PATH']


from dotenv import load_dotenv
import os
load_dotenv() 


PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
KEY_ID = os.getenv("KEY_ID")
API_KEY = os.getenv("API_KEY")
MERCHANT_ID = os.getenv("MERCHANT_ID")
BASE_URL = os.getenv("BASE_URL")
CLIENT_ID = os.getenv("PAYMENT_PAGE_CLIENT_ID")

app = Flask(__name__)

PORT = 5002


# to add return_url in order_session
@app.route('/initiateJuspayPayment', methods=['POST'])
def initiate_payment():
    order_id = f"order_{int(datetime.now().timestamp())}"
    amount = 1 + secrets.randbelow(100)
    return_url = f"{request.scheme}://{request.host.split(':')[0]}/handleJuspayResponse"
    # return_url = f"{NGROK_URL}/handleJuspayResponse"

    try:
        juspay = JuspaySDK(False, MERCHANT_ID, BASE_URL, {'public_key' : PUBLIC_KEY, 'private_key' : PRIVATE_KEY, 'key_id' : KEY_ID}) # merchant can also pass logger in JuspaySDK otherwise default Juspay logger will be called.
        response = juspay.order_session({
            "order_id" : order_id,
            "payment_page_client_id" : CLIENT_ID,
            "amount" : amount,
            "return_url" : return_url
                })
        return jsonify(response)
    except Exception as e:
        return jsonify({"message": str(e)})


@app.route('/handleJuspayResponse', methods=['POST'])
def handle_response():
    order_id = request.form.get('order_id') or request.form.get('orderId')
    if not order_id:
        return jsonify({"message": "order_id not present"})

    try:
        juspay = JuspaySDK(False, MERCHANT_ID, BASE_URL, {'public_key' : PUBLIC_KEY, 'private_key' : PRIVATE_KEY, 'key_id' : KEY_ID})
        response = juspay.order_status({'order_id': order_id})
        return jsonify(response).status
    except Exception as e:
        return jsonify({"message" : str(e)})




@app.route('/initiateRefund', methods=['POST'])
def initiate_refund():
    order_id = request.form.get('order_id') or request.form.get('orderId')
    if not order_id:
        return jsonify({"message": "order_id not present"})

    try:
        juspay = JuspaySDK(False, MERCHANT_ID, BASE_URL, {'public_key' : PUBLIC_KEY, 'private_key' : PRIVATE_KEY, 'key_id' : KEY_ID})
        response = juspay.order_refund({"order_id": order_id, "amount": secrets.randbelow(10), "unique_request_id": f'uff{int(time.time() * 100)}'})
        return jsonify(response)
    except Exception as e:
        return jsonify({"message": str(e)})
    




@app.route('/')
def homepage():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=PORT, debug=True)