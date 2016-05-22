from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Series, Part, User
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Public Relay Library"


# Connect to Database and create database session
engine = create_engine('sqlite:///relayDatabase.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# testSeries = session.query(Series).filter_by(id=1).one()
# print testSeries.name

def createUser(login_session):
	newUser = User(name = login_session['username'],email = login_session['email'],picture = login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id
	
def getUserInfo(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	return user

def getUserID(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.5/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.5/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.5/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"
	
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    #print "LOGIN DEBUGGING - HERE IS THE CREDENTIALS ACCESS TOKEN"
    #print login_session['credentials']
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists; if not, create a new one.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
	
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    # print 'this is the access token'
    # print login_session['credentials']
    myaccess_token = login_session['credentials']
    # print 'In gdisconnect access token is %s', myaccess_token
    # print 'User name is: ' 
    # print login_session['username']
    if myaccess_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']
    # print "url is " + str(url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print 'result is '
    # print result
    if result['status'] == '200':
		# del login_session['username']
		# del login_session['email']
		# del login_session['picture']
		del login_session['credentials']
		del login_session['gplus_id']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
	
# JSON APIs to view series Information
@app.route('/series/<int:series_id>/JSON')
@app.route('/series/<int:series_id>/parts/JSON')
def seriesMenuJSON(series_id):
    series = session.query(Series).filter_by(id=series_id).one()
    items = session.query(Part).filter_by(
        series_id=series_id).all()
    return jsonify(Parts=[i.serialize for i in items])

@app.route('/series/<int:series_id>/parts/<int:part_id>/JSON')
def partJSON(series_id, part_id):
    One_Part = session.query(Part).filter_by(id=part_id).one()
    return jsonify(One_Part=One_Part.serialize)

@app.route('/JSON')
@app.route('/series/JSON')
def seriesListJSON():
    seriesList = session.query(Series).all()
    return jsonify(seriesList=[r.serialize for r in seriesList])

# Show all Series
@app.route('/')
@app.route('/series/')
def showSeriesList():
	seriesList = session.query(Series).order_by(asc(Series.name))
	if 'username' not in login_session:
		return render_template('publicSeries.html', seriesList = seriesList)
	else:
		return render_template('series.html', seriesList = seriesList)
		
# Create a new series

@app.route('/series/new/', methods=['GET', 'POST'])
def newSeries():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newseries = Series(name=request.form['name'], user_id=login_session['user_id'], manufacturer=request.form['manufacturer'], description=request.form['description'])
        session.add(newseries)
        flash('New series %s Successfully Created' % newseries.name)
        session.commit()
        return redirect(url_for('showSeriesList'))
    else:
        return render_template('newSeries.html')

# Edit a series


@app.route('/series/<int:series_id>/edit/', methods=['GET', 'POST'])
def editSeries(series_id):
	if 'username' not in login_session:
		return redirect('/login')
	editedSeries = session.query(Series).filter_by(id=series_id).one()
	if editedSeries.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not \
			authorized to edit this series. please create your \
			own series in order to edit.');}</script><body onload='myFunction()''>"		
	if request.method == 'POST':
		if request.form['name'] != editedSeries.name:
			flash('Sucessfull changed Series '+str(editedSeries.name)+' name to '+str(request.form['name']))
			editedSeries.name = request.form['name']
		if request.form['manufacturer'] != editedSeries.manufacturer:
			flash('Successfully changed manufacturer '+str(editedSeries.manufacturer)+' to '+str(request.form['manufacturer']))
			editedSeries.manufacturer = request.form['manufacturer']
		if request.form['description'] != editedSeries.description:
			flash('Successfully changed the description for %s' % editedSeries.name)
			editedSeries.description = request.form['description']
		session.add(editedSeries)
		session.commit()
		return redirect(url_for('showSeries', series_id = series_id))
	else:
		return render_template('editSeries.html', series=editedSeries)


# Delete a series
@app.route('/series/<int:series_id>/delete/', methods=['GET', 'POST'])
def deleteSeries(series_id):
    if 'username' not in login_session:
        return redirect('/login')
    seriesToDelete = session.query(Series).filter_by(id=series_id).one()
    if seriesToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
            authorized to delete this series. please create your \
            own series in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(seriesToDelete)
        flash('%s Successfully Deleted' % seriesToDelete.name)
        session.commit()
        return redirect(url_for('showSeriesList'))
    else:
        return render_template('deleteSeries.html', series = seriesToDelete)

# Show a series list of parts
@app.route('/series/<int:series_id>/')
@app.route('/series/<int:series_id>/parts/')
def showSeries(series_id):
    series = session.query(Series).filter_by(id=series_id).one()
    creator = getUserInfo(series.user_id)
    items = session.query(Part).filter_by(series_id=series_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicParts.html', items = items, series = series, creator = creator)
    else:
        return render_template('parts.html', items=items, series=series, creator = creator)


# Create a new part for a series
@app.route('/series/<int:series_id>/parts/new/', methods=['GET', 'POST'])
def newPart(series_id):
    if 'username' not in login_session:
        return redirect('/login')
    series = session.query(Series).filter_by(id=series_id).one()
    if series.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
            authorized to add a part to this series. please create your \
            own series in order to add parts.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = Part(name=request.form['name'], footprint=request.form['footprint'], contactForm=request.form[
							   'contactForm'], enclosure=request.form['enclosure'], enhancement=request.form['enhancement'],
							   voltage=request.form['voltage'], series_id=series_id, user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Part %s Successfully Created' % (newItem.name))
        return redirect(url_for('showSeries', series_id=series_id))
    else:
        return render_template('newPart.html', series_id = series_id)

# Edit a menu item


@app.route('/series/<int:series_id>/parts/<int:part_id>/edit', methods=['GET', 'POST'])
def editPart(series_id, part_id):
	if 'username' not in login_session:
		return redirect('/login')
	editedItem = session.query(Part).filter_by(id=part_id).one()
	series = session.query(Series).filter_by(id=series_id).one()
	if series.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not \
		authorized to edit a part to this series. please create your \
		own series in order to edit parts.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['footprint']:
			editedItem.footprint = request.form['footprint']
		if request.form['contactForm']:
			editedItem.contactForm = request.form['contactForm']
		if request.form['enclosure']:
			editedItem.enclosure = request.form['enclosure']
		if request.form['enhancement']:
			editedItem.enhancement = request.form['enhancement']
		if request.form['voltage']:
			editedItem.voltage = request.form['voltage']
		session.add(editedItem)
		session.commit()
		flash('Part %s Successfully Edited' % editedItem.name)
		return redirect(url_for('showSeries', series_id=series_id))
	else:
		return render_template('editPart.html', series_id = series_id, part_id = part_id, item = editedItem)

# Delete a menu item
@app.route('/series/<int:series_id>/parts/<int:part_id>/delete', methods=['GET', 'POST'])
def deletePart(series_id, part_id):
    if 'username' not in login_session:
        return redirect('/login')
    series = session.query(Series).filter_by(id=series_id).one()
    itemToDelete = session.query(Part).filter_by(id=part_id).one()
    if series.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not \
            authorized to delete parts in this series. please create your \
            own series in order to delete parts.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Part Successfully Deleted')
        return redirect(url_for('showSeries', series_id=series_id))
    else:
        return render_template('deletePart.html', series_id=series_id, item=itemToDelete)

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			gdisconnect()
			#del login_session['gplus_id']
		if login_session['provider'] == 'facebook':
			fbdisconnect()
			del login_session['facebook_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['user_id']
		del login_session['provider']
		flash("You have successfully been logged out.")
		return redirect(url_for('showSeriesList'))
	else:
		flash("You were not logged in")
		return redirect(url_for('showSeriesList'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)