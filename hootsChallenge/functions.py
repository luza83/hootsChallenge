from .models import User
from .extensions import db
from werkzeug.security import generate_password_hash
import re, random


def CreateUser(username, email, password):
    account = User.query.filter_by(email=email).first()
    isUserCreated = False
    if account:
        msg = 'Account already exists!'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        msg = 'Invalid email address!'
    elif not re.match('[A-Za-z0-9]+', username):
        msg = 'Username must contain only characters and numbers!'
    elif not username or not password or not email:
        msg = 'Please fill out the form!'
    else:     
        hashed_pass = generate_password_hash(password)
        isUserCreated =True
        user = User(username=username, email=email, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        msg = 'You have successfully registered!'

    return msg, isUserCreated

def UpdateSubjectScore(userId, subject):
    user = User.query.get(userId)
    if not user:
        return None
    if subject == "maths":
        newMathScore = user.mathScore + 10
        user.mathScore = newMathScore
        db.session.commit()
        return newMathScore
    newNatureScienceScore = user.natureScienceScore + 10
    user.natureScienceScore = newNatureScienceScore
    db.session.commit()
    return newNatureScienceScore  
  
# Region Subjects
correctAnswerEmoji = [
		"128077", "127942", "9989", "128079",  
		"127881", "129321", "11088", "128170",  
		"129395", "128175", "128516", "128578",  
		"128640", "127775", "128293", "128079",  
		"127873", "129504", "129311"   
]
 
wrongAnswerEmoji = [
		"128577", "10060", "128533", 
		"128542", "9940", "128577", 
	  "128534", "128553", "128148",  
		"128547", "128580", "128533",  
		"128128", "128121", "128529", 
		"128555", "128577", "129300",  
		"128547"   
]

correctAnswerFeedback = [
					"Great job!","Well done!", "Correct!",
					"Nice work!","You got it!","Excellent!",
					"That's right!","Bravo!","Spot on!",
					"You're doing great!","Keep it up!",
					"Perfect answer!","Nailed it!",
					"Impressive!","You aced it!"
]

wrongAnswerFeedback = [
						"Oops, not quite.","That's not correct.",
						"Try again!","Incorrect.",
					 	"Not the right answer.","Close, but not quite.",
					 	"Better luck next time.","Nope, that's wrong.",
					 	"Keep trying!","Don't give up!","That's a miss.",
					 	"Hmm, that's not it.","Almost had it!",
					 	"Wrong answer.","Nice try, though!"
]


def check_answer(userId, subject, userInput, correctAnswer):
    if userInput == correctAnswer:
        isCorrect = True
        UpdateSubjectScore(userId, subject)
        UpdateSubjectLevel(userId, subject)
        feedbackString = random.choice(correctAnswerFeedback)
        resultStr, emoji = "Correct", random.choice(correctAnswerEmoji)
    else:
        isCorrect = False
        feedbackString = random.choice(wrongAnswerFeedback)
        resultStr, emoji = f"Incorrect. The correct answer is {correctAnswer}", random.choice(wrongAnswerEmoji)
    
    return isCorrect, feedbackString, resultStr, emoji

def GetSubjectScore(subject, userId):
    currentSubject =  "mathScore" if  subject == "maths" else "natureScience"
    user = User.query.get(userId)
    if not user:
          return 0
    if currentSubject == "maths": 
        userScore = user.mathScore
        return userScore
    
    userScore = user.natureScienceScore
    return userScore

def GetSubjectLevel(subject, userId):
    currentSubject =  "mathLevel" if  subject == "maths" else "natureScienceLevel"
    user = User.query.get(userId)
    if not user:
          return 0
    if currentSubject == "maths": 
        userLevel = user.mathLevel
        return userLevel
    
    userLevel = user.natureScienceLevel
    return userLevel

def UpdateSubjectLevel(userId, subject):
    user = User.query.get(userId)
    if not user:
        return None
      
    if subject == "maths":
        newMathLevel = setLevel(user.mathScore)
        if newMathLevel != user.mathLevel:
            user.mathLevel = newMathLevel
            db.session.commit()
        return newMathLevel
    
    newNatureScienceLevel = setLevel(user.natureScienceScore)
    if newNatureScienceLevel != user.natureScienceLevel:
        user.natureScienceLevel = newNatureScienceLevel
        db.session.commit()
    return newNatureScienceLevel  

def setLevel(score):
    if score < 500:
        return 1
    elif score < 1000:
        return 2
    else:
        return 3

def getProgress(level, score):
    if level == 1:
        level_start = 0
        next_level = 500
    elif level == 2:
        level_start = 500
        next_level = 1000
    else:
        level_start = 1000
        next_level = None  # Max level

    if next_level:
        progress = (score - level_start) / (next_level - level_start) * 100
        progress = round(progress, 2)
        print(progress)
    else:
        progress = 100  # Maxed out

    return progress, next_level

# EndRegion
        