import os
import shutil
import tempfile
import hashlib
import flask
from flask import request, redirect, url_for, session, abort
import arrow
import onepost
import twitter
import time
import pytumblr
import threading
from PIL import Image
import requests
from urllib.parse import urlparse, parse_qs
from InstagramAPI import InstagramAPI
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl
import oauth2 as oauth



@onepost.app.route('/', methods=['GET', 'POST'])
def show_index():
    if 'username' not in session:
        return redirect(url_for('show_login'))
    context = {}
    data = onepost.model.get_db()
    #fbAuth
    res = data.execute('SELECT username FROM facebook\
            WHERE username = \''+  session['username'] + '\'')
    for cur in res:
        context["facebook"] = "1"
    #insAuth
    res = data.execute('SELECT username FROM instagram\
            WHERE username = \''+  session['username'] + '\'')
    for cur in res:
        context["instagram"] = "1"
    #tumblrAuth
    res = data.execute('SELECT username FROM tumblr\
            WHERE username = \''+  session['username'] + '\'')
    for cur in res:
        context["tumblr"] = "1"
    #twitterAuth
    res = data.execute('SELECT username FROM twitter\
            WHERE username = \''+  session['username'] + '\'')
    for cur in res:
        context["twitter"] = "1"
    return flask.render_template("index.html", **context)


@onepost.app.route('/instagram', methods=['GET', 'POST'])
def post_instagram():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    context = {}   
    if request.method == 'POST':
        #get file and text
        dummy, temp_filename = tempfile.mkstemp()
        file = flask.request.files["files"]
        file.save(temp_filename)
        text = request.form.get("caption")
        delay = int(request.form.get("delay"))

        data = onepost.model.get_db()
        res =data.execute('SELECT account, password FROM instagram\
                WHERE username = \''+  session['username'] + '\'')
        row = res.fetchone()
        account = row['account']
        password = row['password']
        InstagramAPI1 = InstagramAPI(account, password)
        InstagramAPI1.login()  # login

        photo_path = temp_filename
        caption = text
        
        def inner(InstagramAPI1, photo_path, caption, delay):
            d = delay
            while d >= 1:
                d -= 1
                time.sleep(60)
            im = Image.open(photo_path)
            rgb_im = im.convert('RGB')
            dummy, temp_filename1 = tempfile.mkstemp()
            rgb_im.save("pic.jpg")
            InstagramAPI1.uploadPhoto("pic.jpg", caption=caption)
        t = threading.Thread(target=inner, args = (InstagramAPI1, photo_path, caption, delay))
        t.daemon = True
        t.start()
    return redirect(url_for('show_index')) 


@onepost.app.route('/facebook/text', methods=['GET', 'POST'])
def post_facebook():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    context = {}   
    if request.method == 'POST':
        #get file and text
        text = request.form.get("caption")
        delay = int(request.form.get("delay"))
        data = onepost.model.get_db()
        res =data.execute('SELECT accessToken FROM facebook\
                WHERE username = \''+  session['username'] + '\'')
        row = res.fetchone()
        tk = row['accessToken']
        # print(tk)
        #head = {'Authorization': 'token {}'.format(tk)}
        def inner(text, tk, delay):
            d = delay
            while d >= 1:
                d -= 1
                time.sleep(60)
            r = requests.post("https://graph.facebook.com/me/feed", data={'message': text, 'access_token' : tk})
        t = threading.Thread(target=inner, args = (text,tk,delay))
        t.daemon = True
        t.start()
        #print(r.status_code, r.reason)
    return redirect(url_for('show_index')) 

@onepost.app.route('/facebook/photo', methods=['GET', 'POST'])
def post_facebook_photo():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    if request.method == 'POST':
        context = {}   
        data = onepost.model.get_db()
        delay = int(request.form.get("delay"))
        cur = data.execute('SELECT accessToken \
                FROM facebook WHERE username =\'' + session['username'] + '\'').fetchone()
        if cur: 
            accessToken = cur["accessToken"]

            #get form content
            dummy, temp_filename = tempfile.mkstemp()
            file = flask.request.files["files"]
            file.save(temp_filename)
            text = request.form.get("caption")
            # status = text
            # image = open(temp_filename, 'rb')
            # api.PostUpdate(status=status, media=image)
            url = 'https://graph.facebook.com/me/photos'
            print(url)
            files = {'file': open(temp_filename, 'rb')}
            def inner(url, files, text, accessToken, delay):
                d = delay
                while d >= 1:
                    d -= 1
                    time.sleep(60)
                r = requests.post(url, files=files, data={'caption': text, 'access_token' : accessToken})
                print(r.status_code, r.reason)
            t = threading.Thread(target=inner, args = (url, files, text, accessToken, delay))
            t.daemon = True
            t.start()
            
    return redirect(url_for('show_index')) 


@onepost.app.route('/facebook/setting', methods=['GET', 'POST'])
def update_facebook():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    context = {}   
    if request.method == 'POST':
        #get file and text
        accessToken = str(request.form.get("accessToken"))
        # print(accessToken)
        data = onepost.model.get_db()
        cur = data.execute('SELECT * \
            FROM facebook WHERE username =\'' + session['username'] + '\'').fetchone()
        if cur:
            data.execute('UPDATE facebook \
                SET accessToken = \'' + accessToken + '\'' +' WHERE username =\'' + session['username'] + '\'')
        else:
            data.execute('INSERT INTO facebook \
                VALUES(?, ?) ', [session['username'], accessToken])
        data.commit()
        return flask.render_template("twittersetting.html", **context)
    return flask.render_template("twittersetting.html", **context)



@onepost.app.route('/instagram/setting', methods=['GET', 'POST'])
def update_instagram():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    context = {}   
    if request.method == 'POST':
        #get file and text
        account = str(request.form.get("account"))
        password = str(request.form.get("password"))
        data = onepost.model.get_db()
        cur = data.execute('SELECT * \
            FROM instagram WHERE username =\'' + session['username'] + '\'').fetchone()
        if cur:
            data.execute('UPDATE instagram \
                SET account = \'' + account + '\',password = \''+password+ '\' WHERE username =\'' + session['username'] + '\'')
        else:
            data.execute('INSERT INTO instagram \
                VALUES(?, ?, ?) ', [session['username'], account, password])
        data.commit()
        return redirect(url_for('show_index')) 
    return flask.render_template("inssetting.html", **context)

@onepost.app.route('/twitter/setting', methods=['GET', 'POST'])
def set_twitter():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    context = {}   
    REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
    SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'

    consumer_key    = "HhJrg0xTo3o0CYmZH0472kVJf"
    consumer_secret = "gNcybIYQvVCs7USfLyqYMATdG0oLapJHtxX28reJ0neFktObYM"

    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    oauth_consumer             = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    oauth_client               = oauth.Client(oauth_consumer)

    resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')

    if resp['status'] != '200':
        print('Invalid respond from Twitter requesting temp token: %s' % resp['status'])
    else:
        request_token = dict(parse_qsl(content))
        print(request_token)
        request_token = {str(key, 'utf-8'):str(value, 'utf-8') for key, value in request_token.items()}

        print(request_token)
        print('')
        print('Please visit this Twitter page and retrieve the pincode to be used')
        print('in the next step to obtaining an Authentication Token:')
        print('')
        print(str(AUTHORIZATION_URL)+'?oauth_token='+request_token['oauth_token'])
        print('')
        context["twitterAuth"] = str(AUTHORIZATION_URL)+'?oauth_token='+request_token['oauth_token']
        context["tokenSecret"] = request_token['oauth_token_secret']
        context["OauthToken"] = request_token['oauth_token']
    if request.method == 'POST':
        if 'username' not in session:
            return redirect(url_for('show_login')) 
        #get file and text
        pincode = str(request.form.get("pincode"))
        s1 = str(request.form.get("OauthToken"))
        s2 = str(request.form.get("tokenSecret"))
        token = oauth.Token(s1, s2)
        token.set_verifier(pincode)
        oauth_client  = oauth.Client(oauth_consumer, token)
        resp, content = oauth_client.request(ACCESS_TOKEN_URL, method='POST', body='oauth_callback=oob&oauth_verifier='+pincode)
        access_token  = dict(parse_qsl(content))
        access_token = {str(key, 'utf-8'):str(value, 'utf-8') for key, value in access_token.items()}
        if resp['status'] != '200':
            print('The request for a Token did not succeed: '+  resp['status'])
            print(access_token)
        else:
            oauth_token = access_token['oauth_token']
            oauth_token_secret = access_token['oauth_token_secret']
            data = onepost.model.get_db()
            cur = data.execute('SELECT * \
                FROM twitter WHERE username =\'' + session['username'] + '\'').fetchone()
            if cur:
                data.execute('UPDATE twitter \
                    SET accessToken = \'' + oauth_token + '\',accessTokenSecret = \''+oauth_token_secret+ '\' WHERE username =\'' + session['username'] + '\'')
            else:
                data.execute('INSERT INTO twitter \
                    VALUES(?, ?, ?) ', [session['username'], oauth_token, oauth_token_secret])
            data.commit()
            return redirect(url_for('show_index')) 
    return flask.render_template("twittersetting.html", **context)



@onepost.app.route('/twitter/photo', methods=['GET', 'POST'])
def post_twitter_photo():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    if request.method == 'POST':
        context = {}   
        consumer_key    = "HhJrg0xTo3o0CYmZH0472kVJf"
        consumer_secret = "gNcybIYQvVCs7USfLyqYMATdG0oLapJHtxX28reJ0neFktObYM"
        delay = int(request.form.get("delay"))
        data = onepost.model.get_db()
        cur = data.execute('SELECT accessToken, accessTokenSecret\
                FROM twitter WHERE username =\'' + session['username'] + '\'').fetchone()
        if cur: 
            oauth_token = cur["accessToken"]
            oauth_token_secret = cur["accessTokenSecret"]
            api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=oauth_token,access_token_secret=oauth_token_secret)

            #get form content
            dummy, temp_filename = tempfile.mkstemp()
            file = flask.request.files["files"]
            file.save(temp_filename)
            text = request.form.get("caption")
            status = text
            image = open(temp_filename, 'rb')
            def inner(api, status, image, delay):
                d = delay
                while d >= 1:
                    d -= 1
                    time.sleep(60)
                api.PostUpdate(status=status, media=image)
            t = threading.Thread(target=inner, args = (api, status, image, delay))
            t.daemon = True
            t.start()
    return redirect(url_for('show_index')) 


@onepost.app.route('/twitter/text', methods=['GET', 'POST'])
def post_twitter_text():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    if request.method == 'POST':
        context = {}   
        consumer_key    = "HhJrg0xTo3o0CYmZH0472kVJf"
        consumer_secret = "gNcybIYQvVCs7USfLyqYMATdG0oLapJHtxX28reJ0neFktObYM"
        delay = int(request.form.get("delay"))
        data = onepost.model.get_db()
        cur = data.execute('SELECT accessToken, accessTokenSecret\
                FROM twitter WHERE username =\'' + session['username'] + '\'').fetchone()
        if cur: 
            oauth_token = cur["accessToken"]
            oauth_token_secret = cur["accessTokenSecret"]
            status = request.form.get("caption")
            
            def inner(status, delay, consumer_key, consumer_secret, oauth_token, oauth_token_secret):
                d = delay
                while d >= 1:
                    d -= 1
                    time.sleep(60)
                api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=oauth_token,access_token_secret=oauth_token_secret)
                api.PostUpdate(status=status)
            t = threading.Thread(target=inner, args = (status, delay, consumer_key, consumer_secret, oauth_token, oauth_token_secret))
            t.daemon = True
            t.start()

    return redirect(url_for('show_index')) 







@onepost.app.route('/tumblr/setting', methods=['GET', 'POST'])
def set_tumblr():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    context = {}   
    consumer_key = 'ijkbgt66qLbYkc1DLYUVDf9bEPrsRLPSO0Bbt5VFpjEtIvrT5i'
    consumer_secret = 'ZbRVAW6PEBKfNWkVTtCE63OO6IDgYxuYHLYTfKtvnyqlLHYddF'

    request_token_url = 'https://www.tumblr.com/oauth/request_token'
    access_token_url = 'https://www.tumblr.com/oauth/access_token'
    authorize_url = 'https://www.tumblr.com/oauth/authorize'
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    #Get request token
    resp, content = client.request(request_token_url, "POST")

    if resp['status'] != '200':
            raise Exception("Invalid response ." + resp['status'])

    request_token = dict(parse_qsl(content))
    request_token = {str(key, 'utf-8'):str(value, 'utf-8') for key, value in request_token.items()}
    context["TumblrAuth"] = authorize_url+"?oauth_token=" + request_token['oauth_token']
    context["OauthToken"] = request_token['oauth_token']
    context["tokenSecret"] = request_token['oauth_token_secret']
    if request.method == 'POST': 
        #get file and text
        oauth_verifier = str(request.form.get("verifier"))
        s1 = str(request.form.get("OauthToken"))
        s2 = str(request.form.get("tokenSecret"))
        token = oauth.Token(s1, s2)
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)
        resp, content = client.request(access_token_url, "POST")
        access_token = dict(parse_qsl(content))
        access_token = {str(key, 'utf-8'):str(value, 'utf-8') for key, value in access_token.items()}

        if resp['status'] != '200':
            print('The request for a Token did not succeed: '+  resp['status'])
            print(access_token)
        else:
            oauth_token = access_token['oauth_token']
            oauth_token_secret = access_token['oauth_token_secret']
            data = onepost.model.get_db()
            cur = data.execute('SELECT * \
                FROM tumblr WHERE username =\'' + session['username'] + '\'').fetchone()
            if cur:
                data.execute('UPDATE tumblr \
                    SET accessToken = \'' + oauth_token + '\',accessTokenSecret = \''+oauth_token_secret+ '\' WHERE username =\'' + session['username'] + '\'')
            else:
                data.execute('INSERT INTO tumblr \
                    VALUES(?, ?, ?) ', [session['username'], oauth_token, oauth_token_secret])
            data.commit()
            return redirect(url_for('show_index')) 
    return flask.render_template("tumblrsetting.html", **context)

@onepost.app.route('/tumblr/verifier', methods=['GET'])
def tumblr_verifier():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    context = {}   
    url = request.full_path
    parsed_url = urlparse(url)
    context["verifier"] = parse_qs(parsed_url.query)["oauth_verifier"][0]
    return flask.render_template("tumblrverifier.html", **context)


@onepost.app.route('/tumblr/photo', methods=['GET', 'POST'])
def post_tumblr_photo():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    if request.method == 'POST':
        context = {}   
        consumer_key    = "ijkbgt66qLbYkc1DLYUVDf9bEPrsRLPSO0Bbt5VFpjEtIvrT5i"
        consumer_secret = "ZbRVAW6PEBKfNWkVTtCE63OO6IDgYxuYHLYTfKtvnyqlLHYddF"
        delay = int(request.form.get("delay"))
        data = onepost.model.get_db()
        cur = data.execute('SELECT accessToken, accessTokenSecret\
                FROM tumblr WHERE username =\'' + session['username'] + '\'').fetchone()
        if cur: 
            oauth_token = cur["accessToken"]
            oauth_token_secret = cur["accessTokenSecret"]
            api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=oauth_token,access_token_secret=oauth_token_secret)

            #get form content
            dummy, temp_filename = tempfile.mkstemp()
            file = flask.request.files["files"]
            file.save(temp_filename)
            text = request.form.get("caption")

            client = pytumblr.TumblrRestClient(
                consumer_key,
                consumer_secret,
                oauth_token,
                oauth_token_secret,
            )
            user_name = client.info()['user']['name']
            blogName = user_name+'.tumblr.com'
            def inner(client, blogName, text, temp_filename, delay):
                d = delay
                while d >= 1:
                    d -= 1
                    time.sleep(60)
                client.create_photo(blogName, state="published",
                    caption=text,
                    data=temp_filename)
            t = threading.Thread(target=inner, args = (client, blogName, text, temp_filename, delay))
            t.daemon = True
            t.start()
    return redirect(url_for('show_index')) 

@onepost.app.route('/tumblr/text', methods=['GET', 'POST'])
def post_tumblr_text():
    if 'username' not in session:
        return redirect(url_for('show_login')) 
    if request.method == 'POST':
        context = {}   
        consumer_key    = "ijkbgt66qLbYkc1DLYUVDf9bEPrsRLPSO0Bbt5VFpjEtIvrT5i"
        consumer_secret = "ZbRVAW6PEBKfNWkVTtCE63OO6IDgYxuYHLYTfKtvnyqlLHYddF"
        delay = int(request.form.get("delay"))
        data = onepost.model.get_db()
        cur = data.execute('SELECT accessToken, accessTokenSecret\
                FROM tumblr WHERE username =\'' + session['username'] + '\'').fetchone()
        if cur: 
            oauth_token = cur["accessToken"]
            oauth_token_secret = cur["accessTokenSecret"]
            api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=oauth_token,access_token_secret=oauth_token_secret)

            #get form content
            text = request.form.get("caption")

            client = pytumblr.TumblrRestClient(
                consumer_key,
                consumer_secret,
                oauth_token,
                oauth_token_secret,
            )
            user_name = client.info()['user']['name']
            blogName = user_name+'.tumblr.com'
            def inner(blogName, text, client, delay):
                d = delay
                while d >= 1:
                    d -= 1
                    time.sleep(60)
                client.create_text(blogName, state="published", body=text)
            t = threading.Thread(target=inner, args = (blogName,text, client, delay))
            t.daemon = True
            t.start()

    return redirect(url_for('show_index')) 



