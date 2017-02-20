from flask import Flask, flash, redirect, render_template, url_for, request, jsonify
from flaskext.mysql import MySQL
import sys, datetime
from passlib.hash import bcrypt

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
mysql = MySQL()

app.secret_key = 'jongroeinsacademyqingdaochina'
app.config['MYSQL_DATABASE_USER'] = 'website'
app.config['MYSQL_DATABASE_PASSWORD'] = '0905aebin'
app.config['MYSQL_DATABASE_DB'] = 'academy'
app.config['MYSQL_DATABASE_HOST'] = '117.52.89.194'

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

@app.route('/datalist')
def datalist():
	cursor = (mysql.connect()).cursor()
	get_data_lists_sql = "SELECT * FROM student;"
	cursor.execute(get_data_lists_sql)
	data_lists = cursor.fetchall()
	return render_template('datalist.html', data_lists=data_lists)

@app.route('/_change_db')
def change_db():
	db_name = request.args.get('db_name', type=str)
	cursor = (mysql.connect()).cursor()
	get_data_lists_sql = "SELECT * FROM {0};".format(db_name)
	cursor.execute(get_data_lists_sql)
	data_lists = cursor.fetchall()
	if db_name == "student":
		keys = ['Student ID', 'Name', 'Date of Birth', 'Phone Number', 'Address', 'School', 'Grade']
	elif db_name == "teacher":
		keys = ['Teacher ID', 'Name', 'Date of Birth', 'Phone Number', 'Address']
	elif db_name == "class":
		keys = ['Class ID', 'Name', 'Teacher ID', 'Start Date', 'End Date', 'Start Time', 'End Time', 'Day of Week', 'Textbook', 'Flag', 'Group Name']
	elif db_name == "parent":
		keys = ['Parent ID', 'Name', 'Date of Birth', 'Phone Number', 'Address']
	return jsonify(db_name=db_name, columns=keys, rows=data_lists)

@app.route('/student/<studentid>')
def student_profile(studentid):
	cursor = (mysql.connect()).cursor()
	# student profile
	get_data_sql = "SELECT * FROM student WHERE UUID = {0};".format(studentid)
	cursor.execute(get_data_sql)
	data = cursor.fetchone()
	# student class data
	today = datetime.datetime.now()
	today_date = today.strftime("%Y-%m-%d")
	student_condition = "(cs.studentUID = '{0}')".format(studentid)
	class_base_sql = "SELECT cg.name, c.name, t.name FROM classGroup cg, class c, teacher t, classStudent cs WHERE (cg.ID = c.groupID) AND (c.teacherUID = t.UUID) AND (c.uniqueID = cs.classUID) AND {0}".format(student_condition)
	current_condition_sql = "(date('{0}') BETWEEN c.startDate AND c.endDate)".format(today_date, str(today.weekday()))
	history_condition_sql = "NOT(" + current_condition_sql + ")"
	class_current_sql =  class_base_sql + "  AND {0};".format(current_condition_sql)
	class_history_sql =  class_base_sql + " AND {0};".format(history_condition_sql)
	cursor.execute(class_current_sql)
	class_current = cursor.fetchall()
	cursor.execute(class_history_sql)
	class_history = cursor.fetchall()
	# student score data
	get_scores_sql = "SELECT name, date, score, subject, content FROM test WHERE (studentUID = '1800030') AND (name LIKE '%hsk%4%');"
	cursor.execute(get_scores_sql)
	scores = cursor.fetchall()
	return render_template("students.html", studentid=data[0], studentname=data[1], birth=data[2], phone=data[3], address=data[4], school=data[5], grade=data[6], class_current=class_current, class_history=class_history)

@app.route('/calendar')
def calendar():
	change_type = "daily"
	date_type = "daily"
	academy_type = "both"
	date_types = ['daily', 'weekly']
	academy_types = ['jongro', 'eins', 'both']

	cursor = (mysql.connect()).cursor()

	base_sql = "SELECT a.name, b.name, a.startDate, a.endDate, a.startTime, a.endTime, a.dayOfWeek FROM class a, teacher b WHERE (a.teacherUID = b.UUID)"
	get_teacher_base_sql = "SELECT DISTINCT b.name FROM class a, teacher b WHERE (a.teacherUID = b.UUID)"
	today = datetime.datetime.now()
	today_date = today.strftime("%Y-%m-%d")
	this_week_dates = [(today + datetime.timedelta(days=i)) for i in range(0-today.weekday(), 7-today.weekday())]
	start_date_this_wk = this_week_dates[0].strftime("%Y-%m-%d")
	end_date_this_wk = this_week_dates[-1].strftime("%Y-%m-%d")

	condition_daily = "(date('{0}') BETWEEN a.startDate AND a.endDate) AND (a.dayOfWeek LIKE '%{1}%')".format(today_date, str(today.weekday()))
	condition_weekly = "('{0}' <= a.endDate) AND ('{1}' >= a.startDate)".format(start_date_this_wk, end_date_this_wk)
	condition_jongro = "(a.name LIKE '%%hsk%%') OR (a.name LIKE '%%jongro%%')"
	condition_eins = "NOT(" + condition_jongro + ")"
	condition_both = "(a.name LIKE '%%')"
	condition = {"daily": condition_daily, "weekly": condition_weekly, "jongro": condition_jongro, "eins": condition_eins, "both": condition_both}

	def sql_statement(change_type, date_type, academy_type, date_types, academy_types, base_sql, condition):
		if change_type in date_types:
			get_data_lists_sql = base_sql + " AND {0} AND {1};".format(condition[change_type], condition[academy_type])
			jongro_teachers_sql = get_teacher_base_sql + " AND {0} AND {1};".format(condition['jongro'], condition[change_type])
			eins_teachers_sql = get_teacher_base_sql + " AND {0} AND {1};".format(condition['eins'], condition[change_type])
			status_return = [change_type, academy_type]
		elif change_type in academy_types:
			get_data_lists_sql = base_sql + " AND {0} AND {1};".format(condition[change_type], condition[date_type])
			jongro_teachers_sql = get_teacher_base_sql + " AND {0} AND {1};".format(condition['jongro'], condition[date_type])
			eins_teachers_sql = get_teacher_base_sql + " AND {0} AND {1};".format(condition['eins'], condition[date_type])
			status_return = [date_type, change_type]
		return [get_data_lists_sql, jongro_teachers_sql, eins_teachers_sql, status_return]

	sql_list = sql_statement(change_type, date_type, academy_type, date_types, academy_types, base_sql, condition)

	cursor.execute(sql_list[0])
	data_lists = cursor.fetchall()

	cursor.execute(sql_list[1])
	jongro_teacher_list = [teacher[0] for teacher in cursor.fetchall()]
	jongro_teacher_count = str(len(jongro_teacher_list))

	cursor.execute(sql_list[2])
	eins_teacher_list = [teacher[0] for teacher in cursor.fetchall()]

	teacher_list = jongro_teacher_list + eins_teacher_list

	if (change_type == "weekly") or ((change_type not in date_types) and (date_type == "weekly")):
		return_data_lists = list()
		for i in range(len(data_lists)):
			listified = list(data_lists[i])
			datelist = [int(val) for val in listified[-1].split('/')]
			datelist = [this_week_dates[date].strftime("%Y-%m-%d") for date in datelist]
			listified[-1] = datelist
			return_data_lists.append(listified)

	if (change_type == "daily") or ((change_type not in date_types) and (date_type == "daily")):
		return_data_lists = list()
		for i in range(len(data_lists)):
			listified = list(data_lists[i])
			listified[-1] = today_date
			return_data_lists.append(listified)

	return render_template('calendar.html', color=3)

if __name__ == '__main__':
	app.run(debug=True)