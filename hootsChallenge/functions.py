from .models import User, User_Subject, Subject
from .schemas.user_progress import UserProgress
from .extensions import db
from werkzeug.security import generate_password_hash
import re, random


def CreateUser(username, email, password):
    account = User.query.filter_by(email=email).first()
    userCreated = False
    userSubjectsGenerated = False
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
        user = User(username=username, email=email, password=hashed_pass)

        try:
            db.session.add(user)
            db.session.commit()
            userSubjectsGenerated = GenerateUserSubjects(user.id)
        except Exception as e:
            db.session.rollback() 
            msg = e
        else:
            userCreated = user.id > 0 and userSubjectsGenerated 
            msg = 'You have successfully registered!'
        
    return msg, userCreated

## Level thresholds
level2 = 500
level3 = 1000


def GenerateUserSubjects(userId):
    subjects = db.session.query(Subject).all()
    try:
        for  s in subjects:
            userSubject = User_Subject(userId = userId, subjectId = s.id, score= 0, level=1)
            db.session.add(userSubject)
            db.session.commit()
        return True
    except Exception as e:
        return False


def UpdateUserSubjectProgress(userId, subjectId):
    user = User.query.get(userId)
    if not user:
        return None
    userSubject = User_Subject.query.filter_by(userId=userId, subjectId=subjectId).first()
    level = setLevel(userSubject.score)
    newLevel = False
    if level != userSubject.level:
        userSubject.level = level
        newLevel = True
    newScore = userSubject.score + 10
    userSubject.score = newScore
    db.session.commit()

    return newLevel
  
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


def check_answer(userId, subjectId, userInput, correctAnswer):
    
    if userInput == correctAnswer:
        isCorrect = True
        isNewLevelReached = UpdateUserSubjectProgress(userId, subjectId)
        feedbackString = random.choice(correctAnswerFeedback)
        resultStr, emoji = "Correct", random.choice(correctAnswerEmoji)
    else:
        isCorrect = False
        isNewLevelReached = False
        feedbackString = random.choice(wrongAnswerFeedback)
        resultStr, emoji = f"Incorrect. The correct answer is {correctAnswer}", random.choice(wrongAnswerEmoji)
    
    return isCorrect, feedbackString, resultStr, emoji, isNewLevelReached


def setLevel(score):
    if score < level2:
        return 1
    elif score < level3:
        return 2
    else:
        return 3

def getUserProgress(userId):
    userSubjects = User_Subject.query.filter(User_Subject.userId == userId).all()
    userSubjectsProgress = []
    for item in userSubjects:
        userProgress = calculateProgress(userSubject=item)
        userSubjectsProgress.append(userProgress)

    return userSubjectsProgress


def getSubjectProgress(userId, subjectId):
    userSubject = User_Subject.query.filter_by(userId=userId, subjectId=subjectId).first()
    userSubjectsProgress = calculateProgress(userSubject=userSubject)
   
    return userSubjectsProgress

def calculateProgress(userSubject):
    subject = Subject.query.get(userSubject.subjectId)
    isMaxLevel = False
    if userSubject.level == 1:
        currentlevel_start = 0
        nextLevel_start = level2
    elif userSubject.level == 2:
        currentlevel_start = level2
        nextLevel_start = level3
    else:
        currentlevel_start = level3
        nextLevel_start = None 
        isMaxLevel = True
    if nextLevel_start:
        progress = (userSubject.score - currentlevel_start) / (nextLevel_start - currentlevel_start) * 100
        progress = round(progress)
    else:
        progress = 100
    userProgress = UserProgress(name=subject.subjectName, progress=progress,level=userSubject.level, score=userSubject.score, nextLevelStart=nextLevel_start, isMaxLevel=isMaxLevel)
    return userProgress

# EndRegion
        