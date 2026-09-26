from datetime import datetime
from fatsecret import Fatsecret
import os
from dotenv import load_dotenv
load_dotenv()

consumer_key= os.getenv("FATSECRET_CONSUMER_KEY")
consumer_secret= os.getenv("FATSECRET_CONSUMER_SECRET")

fs = Fatsecret(consumer_key, consumer_secret)

auth_url = fs.get_authorize_url()

print("Browse to the following URL in your browser to authorize access:\n{}"\
    .format(auth_url))

pin = input("Enter the PIN provided by FatSecret: ")
session_token = fs.authenticate(pin)

print("Session Token: {}".format(session_token))
print("Most Eaten Food Results: {}".format(len(foods)))