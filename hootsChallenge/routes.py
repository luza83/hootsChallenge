from flask import Blueprint, render_template, request, url_for, flash, redirect, session
import random, json
from werkzeug.security import check_password_hash
from .models import User
from .functions import CreateUser, check_answer, getProgress, GetSubjectScore, GetSubjectLevel
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
        return redirect(url_for('main.index'))  # or redirect to a 'home' route if exists

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
            mathProgress, mathNextLevel = getProgress(currentUser.mathLevel,currentUser.mathScore)
            natureScienceProgress, natureScienceNextLevel = getProgress(currentUser.natureScienceLevel, currentUser.natureScienceScore)

            return render_template("profile.html", 
                                   mathScore = currentUser.mathScore, 
                                   natureScienceScore = currentUser.natureScienceScore, 
                                   name = currentUser.username, 
                                   mathLevel = currentUser.mathLevel, 
                                   natureScienceLevel = currentUser.natureScienceLevel,
                                   mathProgress = mathProgress,
                                   natureScienceProgress = natureScienceProgress,
                                   mathNextLevel = mathNextLevel,
                                   natureScienceNextLevel = natureScienceNextLevel)
    
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
    
    mathProgress, mathNextLevel = getProgress(currentUser.mathLevel,currentUser.mathScore)

    if currentUser.mathLevel == 1:
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


    elif currentUser.mathLevel == 2:
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
                        op=op_list[op_type], 
                        ans=ans, 
                        level=currentUser.mathLevel,
                        mathProgress=mathProgress,
                        mathNextLevel=mathNextLevel,
                        mathScore = currentUser.mathScore
                        )


	
@main.route('/math_conf', methods=['post'])
def math_conf():
    if 'loggedin' in session:
        currentUser = User.query.get(session['id'])
        if not currentUser:
            return redirect(url_for('main.index'))	
        
        inpUser=request.form['result']
        ans=request.form['ans']
        isCorrect, st, corr, emoji = check_answer(session["id"],"maths",inpUser, ans)
        mathScore = GetSubjectScore("maths", currentUser.id)
        mathProgress, mathNextLevel = getProgress(currentUser.mathLevel,currentUser.mathScore)
        return render_template("subjects/matte/math_conf.html", 
                                result = inpUser, 
                                answer = corr, 
                                emoji = emoji, 
                                st = st, 
                                isCorrect = isCorrect,
                                level = currentUser.mathLevel,
                                mathScore = mathScore,
                                mathProgress = mathProgress,
                                mathNextLevel = mathNextLevel)
	
    
	

	###Nature science#####

@main.route('/natureScience')
def natureScience():
    TRIVIA_API_URL = "https://the-trivia-api.com/api/questions"
    
    if 'loggedin' in session:
        currentUser = User.query.get(session['id'])
        if not currentUser:
            return redirect(url_for('main.index'))
        
        if currentUser.natureScienceLevel == 1: 
          difficulty = "easy"
        elif currentUser.natureScienceLevel == 2:
          difficulty = "medium"
        else:
          difficulty = "hard"
        
        params = {
            "categories": "science",
            "limit": 5,
            "difficulty": difficulty # or "easy", "hard"
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

        natureScienceScore = GetSubjectScore("natureScience", currentUser.id)
        natureScienceProgress, natureScienceNextLevel = getProgress(currentUser.natureScienceLevel,currentUser.natureScienceScore)
        return render_template("subjects/natureScience/natureScience.html",  
														question = question,
														level =	currentUser.natureScienceLevel,
                                                        natureScienceScore = natureScienceScore,
                                                        natureScienceProgress = natureScienceProgress,
                                                        natureScienceNextLevel = natureScienceNextLevel)
    	

@main.route('/natureScience_conf', methods=['post'])
def natureScience_conf():
    if 'loggedin' in session:
        currentUser = User.query.get(session['id'])
        if not currentUser:
            return redirect(url_for('main.index'))
        
        userInput=request.form['answer']
        result = request.form['qAnswer']
        isCorrect, feedback, resultStr, emoji = check_answer(session["id"],"natureScience", userInput, result)
        natureScienceScore = GetSubjectScore("natureScience", currentUser.id)
        natureScienceProgress, natureScienceNextLevel = getProgress(currentUser.natureScienceLevel,currentUser.natureScienceScore)
        return render_template("subjects/natureScience/natureScience_conf.html",  
                               userInput = userInput, 
                               result = result, 
                               emoji = emoji, 
                               resultStr = resultStr,
                               feedback= feedback, 
                               isCorrect = isCorrect,
                               level = currentUser.natureScienceLevel,
                               natureScienceScore = natureScienceScore,
                               natureScienceProgress = natureScienceProgress,
                               natureScienceNextLevel = natureScienceNextLevel
                               )
        
    

# endregion