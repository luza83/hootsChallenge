from flask import Blueprint, render_template, request, url_for, flash, redirect, session
import random, json
from werkzeug.security import check_password_hash
from .models import User, Subject
from .functions import CreateUser, check_answer, getUserProgress, getSubjectProgress
import requests
main = Blueprint("main", __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if session and 'loggedin' in session:
        return render_template('home.html', username=session['username'])

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password') or ""

        user = User.query.filter_by(email=email).first()
       
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('main.index'))

        session['loggedin'] = True
        session['id'] = user.id
        session['username'] = user.username
        return redirect(url_for('main.index'))  
    
    # For GET request, just show login page
    return render_template("index.html")


@main.route('/home')
def home():
    if 'loggedin' not in session:
        return redirect(url_for('main.index'))
    return render_template('home.html', username=session['username'])

@main.route('/about')
def about():
	if 'loggedin' not in session:
		return redirect(url_for('main.index'))
	return render_template("about.html")


@main.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    currentUser = None
    return redirect(url_for('main.index'))


# Region USER 

@main.route('/profile')
def profile():
    if 'loggedin' in session:
        currentUser = User.query.get(session['id'])

        if currentUser:
            progress = getUserProgress(currentUser.id)

            return render_template("profile.html", 
                                   name = currentUser.username, 
                                   subjectsProgress = progress)
    
    # User is not logged in
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    response = False
   
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        msg, response = CreateUser(username,email,password)

    return render_template('register.html', response=response, msg=msg)

# region Subjets

@main.route('/subjects')
def level():
	if 'loggedin' in session:
		return render_template("subjects/subjects.html")
	return redirect(url_for('main.index'))
#####################################################

## ***SUBJECTS*** ##

		###Mathematics###
@main.route('/math')
def math():

    if 'loggedin' not in session:
        return redirect(url_for('main.index'))

    currentUser = User.query.get(session['id'])
    
    if not currentUser:
        return redirect(url_for('main.index'))	
    subject = Subject.query.filter_by(subjectName='Math').first()
    subjectProgress = getSubjectProgress(currentUser.id, subject.id)


    if subjectProgress.level == 1:
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        op_list = ["+", "-"]
        op_type = random.randint(0, 1)

        if op_type == 0:
            ans = a + b
        else:
            if a < b:
                a, b = b, a  
            ans = a - b


    elif subjectProgress.level == 2:
        op_list = ["x", "÷"]
        op_type = random.randint(0, 1)

        if op_type == 1:
            # Division with exact result
            while True:
                a = random.randint(2, 100)
                b = random.randint(2, 10)
                if a % b == 0:
                    ans = a // b
                    break
        else:
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            ans = a * b

    else:
        op_list = ["x", "÷"]
        op_type = random.randint(0, 1)

        if op_type == 1:
            a = random.randint(2, 100)
            b = random.randint(2, 10)
            ans = round(a / b, 2)  
        else:
            a = random.randint(2, 100)
            b = random.randint(2, 100)
            ans = a * b
        
    return render_template("subjects/matte/math.html", 
                        a=a, b=b, 
                        op = op_list[op_type], 
                        ans = ans, 
                        level = subjectProgress.level,
                        mathProgress = subjectProgress.progressPercentage,
                        mathNextLevel = subjectProgress.nextLevelStart,
                        mathScore = subjectProgress.score,
                        isMaxLevel =subjectProgress.isMaxLevel
                        )

	
@main.route('/math_conf', methods=['GET', 'POST'])
def math_conf():
    if 'loggedin' not in session:
        return redirect(url_for('main.index'))

    currentUser = User.query.get(session['id'])
    subject = Subject.query.filter_by(subjectName='Math').first()

    if not currentUser:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        userInput = request.form['userAnswer']
        correctAnswer = request.form['correctAnswer']

        isCorrect, feedbackString, resultStr, emoji, isNewLevel = check_answer(session["id"], subject.id, userInput, correctAnswer)

        session['math_conf_data'] = {
            'userInput': userInput,
            'resultStr': resultStr,
            'emoji': emoji,
            'feedbackString': feedbackString,
            'isCorrect': isCorrect,
            'isNewLevel': isNewLevel
        }

        return redirect(url_for('main.math_conf'))

    data = session.pop('math_conf_data', None)
    subjectProgress = getSubjectProgress(currentUser.id, subject.id)

    if data:
            return render_template("subjects/matte/math_conf.html",
                           result=data['userInput'],
                           answer=data['resultStr'],
                           emoji=data['emoji'],
                           feedbackString=data['feedbackString'],
                           isCorrect=data['isCorrect'],
                           isNewLevel=data['isNewLevel'],
                           level=subjectProgress.level,
                           mathScore=subjectProgress.score,
                           mathProgress=subjectProgress.progressPercentage,
                           mathNextLevel=subjectProgress.nextLevelStart,
                           isMaxLevel =subjectProgress.isMaxLevel)
    else:
        return redirect(url_for('main.math'))


	###Nature science#####

@main.route('/natureScience')
def natureScience():
    TRIVIA_API_URL = "https://the-trivia-api.com/api/questions"
    
    if 'loggedin' in session:
        currentUser = User.query.get(session['id'])
        if not currentUser:
            return redirect(url_for('main.index'))
        
        subject = Subject.query.filter_by(subjectName='NatureScience').first()
        userSubjectProgress = getSubjectProgress(currentUser.id, subject.id)

        if userSubjectProgress.level == 1: 
          difficulty = "easy"
        elif userSubjectProgress.level == 2:
          difficulty = "medium"
        else:
          difficulty = "hard"
        
        params = {
            "categories": "science",
            "limit": 5,
            "difficulty": difficulty 
            }  
        
        questions = requests.get(TRIVIA_API_URL, params=params)

        if questions.status_code == 200:
           
            questions = questions.json()
            question = random.choice(questions) if questions else None
        
            options = question["incorrectAnswers"] + [question["correctAnswer"]]
            random.shuffle(options)
            question["shuffledOptions"] = options
        else:
            questions = []

        return render_template("subjects/natureScience/natureScience.html",  
														question = question,
														level =	userSubjectProgress.level,
                                                        natureScienceScore = userSubjectProgress.score,
                                                        natureScienceProgress = userSubjectProgress.progressPercentage,
                                                        natureScienceNextLevel = userSubjectProgress.nextLevelStart,
                                                        isMaxLevel =userSubjectProgress.isMaxLevel)
    	

@main.route('/natureScience_conf', methods=['GET', 'POST'])
def natureScience_conf():
    if 'loggedin' not in session:
        return redirect(url_for('main.index'))
    
    currentUser = User.query.get(session['id'])
    subject = Subject.query.filter_by(subjectName='NatureScience').first()

    if not currentUser:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
    
        userInput=request.form['userAnswer']
        result = request.form['correctAnswer']
        isCorrect, feedbackString, resultStr, emoji, isNewLevel = check_answer(userId=session["id"],subjectId=subject.id, userInput=userInput, correctAnswer=result)

        session['natureScience_conf_data'] = {
                'userInput': userInput,
                'resultStr': resultStr,
                'emoji': emoji,
                'feedbackString': feedbackString,
                'isCorrect': isCorrect,
                'isNewLevel': isNewLevel
        }
        
        return redirect(url_for('main.natureScience_conf'))

    data = session.pop('natureScience_conf_data', None)
    natureScienceProgress = getSubjectProgress(currentUser.id, subject.id)

    if data:
        return render_template("subjects/natureScience/natureScience_conf.html",  
                                userInput=data['userInput'],
                                answer=data['resultStr'],
                                emoji=data['emoji'],
                                feedbackString=data['feedbackString'],
                                isCorrect=data['isCorrect'],
                                isNewLevel=data['isNewLevel'],
                                level = natureScienceProgress.level,
                                natureScienceScore = natureScienceProgress.score,
                                natureScienceProgress = natureScienceProgress.progressPercentage,
                                natureScienceNextLevel = natureScienceProgress.nextLevelStart,
                                isMaxLevel =natureScienceProgress.isMaxLevel
                                )
    else:
        return redirect(url_for('main.natureScience'))

    


# endregion