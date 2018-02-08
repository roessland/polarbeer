"""
Bare-bones script to get an access token to the Polar Accesslink API.
"""

import requests
from requests.auth import HTTPBasicAuth
import base64

CLIENT_ID = open("CLIENT_ID").read().strip()
CLIENT_SECRET = open("CLIENT_SECRET").read().strip()

def print_info():
    print("client_id:", CLIENT_ID)
    print("client_secret:", CLIENT_SECRET)
    print("b64(id:secret):", b64encode(CLIENT_ID + ":" + CLIENT_SECRET))

def redirect():
    REDIRECT_URI = "https://polarbeer.roessland.com/"
    AUTH_URL = "https://flow.polar.com/oauth2/authorization?response_type=code&scope={SCOPE}&client_id={CLIENT_ID}&state={STATE}"
    print("Retrieve authorization code from the following URL")
    print(AUTH_URL.format(
        SCOPE="accesslink.read_all",
        STATE="YOLO",
        CLIENT_ID=CLIENT_ID
    ))

def ask_for_auth_code():
    auth_code = input("Paste code here:").strip()
    print("Using auth code:", auth_code)
    return auth_code

def b64encode(s):
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")
assert b64encode("12345:verySecret") == "MTIzNDU6dmVyeVNlY3JldA=="

def retrieve_access_token(auth_code):
    TOKEN_URL = "https://polarremote.com/v2/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json;charset=UTF-8"
    }
    post_data = {"grant_type": "authorization_code", "code": auth_code}
    auth = (CLIENT_ID, CLIENT_SECRET)
    resp = requests.post(TOKEN_URL, post_data, headers=headers, auth=auth)
    print("Response code:", resp.status_code)
    print("Response headers:", resp.headers)
    print("Response body:", resp.json())

print_info()
redirect()
auth_code = ask_for_auth_code()
retrieve_access_token(auth_code)
