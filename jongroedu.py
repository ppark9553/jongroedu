from flask import Flask, flash, redirect, render_template, url_for, request, jsonify
from flaskext.mysql import MySQL
import sys, datetime
from passlib.hash import bcrypt

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
mysql = MySQL()

app.secret_key = 'jongroeinsacademyqingdaochina'
app.config['MYSQL_DATABASE_USER'] = 'jongro'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jongro123456'
app.config['MYSQL_DATABASE_DB'] = 'academy'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['Username']
		password = request.form['Password']
		cursor = (mysql.connect()).cursor()
		username_check_sql = "SELECT EXISTS(SELECT 1 FROM user WHERE ID = '{0}');".format(username)
		cursor.execute(username_check_sql)
		username_check_result = cursor.fetchone()[0]
		if username_check_result == 1:
			get_password_sql = "SELECT PW FROM user WHERE ID = '{0}';".format(username)
			cursor.execute(get_password_sql)
			get_password_result = cursor.fetchone()[0]
			if bcrypt.verify(password, get_password_result):
				flash("Login successful")
				return redirect(url_for('dashboard'))
			else:
				flash("Invalid Credentials. Please try again")
		else:
			flash("Invalid Username or Password. Please try again")
	return render_template('login.html')

if __name__ == '__main__':
	app.run(debug=True)