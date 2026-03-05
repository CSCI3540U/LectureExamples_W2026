from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from pymongo import MongoClient
from secrets import db_url, session_secret
import re

app = Flask(__name__)
app.secret_key = session_secret
PORT = 9000

client = MongoClient(db_url)
db = client['auth']
#db = client.get_default_database()
users = db['users']

# fixes:
# 1. ensuring that the dictionary values are strings
# 2. using regex validation to check for allowed characters unnecessary with 1, but an alternative
EMAIL_RE = re.compile(r'^[a-zA-Z]+@[a-zA-Z]+\.[a-zA-Z]{2,}$')
PASSWORD_RE = re.compile(r'^[a-zA-Z0-9!@#$%^&*]{8,32}$')

def init_db():
	# print(f'Using MongoDB URL: {db_url}')
	if users.find_one({'email': 'admin@abc.com'}):
		print('Avoiding re-creating default user')
	else:
		users.insert_one({'email': 'admin@abc.com', 'password': 'openup'})

init_db()

@app.context_processor
def inject_auth():
    return {
        'logged_in': 'user' in session,
        'current_user': session.get('user')
    }

@app.get('/login')
def login_get():
	return render_template('login.html', title='Please Log In')

@app.post('/login')
def login_post():
	data = request.get_json() 
	email = data.get('email')
	password = data.get('password')

	print(f'query: {{"email": "{email}", "password": "{password}"}}')

	# FIX: reject anything that isn't a plain string before querying
	# if not isinstance(email, str) or not isinstance(password, str):
	# 	return jsonify({'message': 'Login Incorrect'}), 401

	# FIX: validate both the E-Mail and Password with an allow list of characters
	# if not EMAIL_RE.match(email) or not PASSWORD_RE.match(password):
	# 	return jsonify({'message': 'Login Incorrect'}), 401

	user = users.find_one({'email': email, 'password': password})

	if user:
		session['user'] = email
		return jsonify({'message': 'Success'})
	else:
		return jsonify({'message': 'Login Incorrect'}), 401

@app.get('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login_get'))
    user = users.find_one({'email': session['user']}, {'_id': 0})
    return render_template('profile.html', user=user)

@app.get('/logout')
def logout():
	session.clear()
	return redirect(url_for('login_get'))

if __name__ == '__main__':
	app.run(port=PORT)
