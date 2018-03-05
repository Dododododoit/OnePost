try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl
import oauth2 as oauth

consumer_key = 'ijkbgt66qLbYkc1DLYUVDf9bEPrsRLPSO0Bbt5VFpjEtIvrT5i'
consumer_secret = 'ZbRVAW6PEBKfNWkVTtCE63OO6IDgYxuYHLYTfKtvnyqlLHYddF'

request_token_url = 'https://www.tumblr.com/oauth/request_token'
access_token_url = 'https://www.tumblr.com/oauth/access_token'
authorize_url = 'https://www.tumblr.com/oauth/authorize'

consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)

# Step 1: Get a request token. This is a temporary token that is used for
# having the user authorize an access token and to sign the request to obtain
# said access token.

resp, content = client.request(request_token_url, "POST")
print(resp)
if resp['status'] != '200':
        raise Exception("Invalid response ." + resp['status'])

request_token = dict(parse_qsl(content))
request_token = {str(key, 'utf-8'):str(value, 'utf-8') for key, value in request_token.items()}
print(request_token)
print("Request Token:")
print("    - oauth_token        = " + request_token['oauth_token'])
print("    - oauth_token_secret = " + request_token['oauth_token_secret'])

# Step 2: Redirect to the provider. Since this is a CLI script we do not
# redirect. In a web application you would redirect the user to the URL
# below.

print("Go to the following link in your browser:")
print(authorize_url+"?oauth_token=" + request_token['oauth_token'])

# After the user has granted access to you, the consumer, the provider will
# redirect you to whatever URL you have told them to redirect to. You can
# usually define this in the oauth_callback argument as well.
accepted = 'n'
while accepted.lower() == 'n':
    accepted = input('Have you authorized me? (y/n) ')
    oauth_verifier = input('What is the OAuth Verifier? ')

# Step 3: Once the consumer has redirected the user back to the oauth_callback
# URL you can request the access token the user has approved. You use the
# request token to sign this request. After this is done you throw away the
# request token and use the access token returned. You should store this
# access token somewhere safe, like a database, for future use.
token = oauth.Token(request_token['oauth_token'],
    request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)

resp, content = client.request(access_token_url, "POST")
access_token = dict(parse_qsl(content))
access_token = {str(key, 'utf-8'):str(value, 'utf-8') for key, value in access_token.items()}

print("Access Token:")
print("    - oauth_token        = " + access_token['oauth_token'])
print("    - oauth_token_secret = " + access_token['oauth_token_secret'])
print("You may now access protected resources using the access tokens above.")
