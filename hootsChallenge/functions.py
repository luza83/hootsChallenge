from .models import User, User_Subject, Subject
from .schemas.user_progress import UserProgress
from .extensions import db
from werkzeug.security import generate_password_hash
import re, random, math


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

# Region Math
def gen_negative_arithmetic():
    a = random.randint(-50, 50)
    b = random.randint(-50, 50)
    if random.randint(0, 1) == 0:
        return f"{a} + ({b})", a + b
    return f"{a} - ({b})", a - b


def gen_decimal_multiply():
    a = round(random.uniform(0.5, 9.9), 1)
    b = random.randint(2, 12)
    return f"{a} × {b}", round(a * b, 2)


def gen_decimal_divide():
    b = random.choice([2, 4, 5, 8, 10, 20, 25])
    ans = round(random.uniform(0.5, 15.0), 1)
    a = round(ans * b, 1)
    return f"{a} ÷ {b}", ans


def gen_fraction_to_decimal():
    b = random.choice([2, 4, 5, 8, 10, 20, 25])
    a = random.randint(1, b - 1)
    while math.gcd(a, b) != 1 and b != 2:
        a = random.randint(1, b - 1)
    return f"{a}/{b} = ? (as a decimal)", round(a / b, 2)


# ─── Level 2: Percentages, order of operations, equations ───

def gen_percentage_of():
    pct = random.choice([5, 10, 15, 20, 25, 50, 75])
    base = random.choice([40, 60, 80, 100, 120, 150, 200, 240, 300, 400])
    ans = (pct / 100) * base
    return f"What is {pct}% of {base}?", int(ans) if ans == int(ans) else ans


def gen_order_of_operations():
    a = random.randint(2, 10)
    b = random.randint(2, 10)
    c = random.randint(1, 9)
    if random.randint(0, 1) == 0:
        return f"{a} + {b} × {c} = ?", a + b * c
    return f"({a} + {b}) × {c} = ?", (a + b) * c


def gen_one_step_add_sub():
    x = random.randint(-30, 30)
    a = random.randint(-20, 20)
    b = x + a
    if a >= 0:
        return f"Solve for x:  x + {a} = {b}", x
    return f"Solve for x:  x - {abs(a)} = {b}", x


def gen_one_step_multiply():
    x = random.randint(-12, 12)
    while x == 0:
        x = random.randint(-12, 12)
    a = random.randint(2, 12)
    return f"Solve for x:  {a}x = {b}", x


# ─── Level 3: Compound, two-step, geometry, percent change ───

def gen_compound_expression():
    a = random.randint(2, 15)
    b = random.randint(2, 15)
    c = random.randint(2, 10)
    d = random.randint(1, 8)
    if random.randint(0, 1) == 0:
        return f"{a} × {b} + {c} − {d} = ?", a * b + c - d
    while (a + b * c) % d != 0:
        d = random.randint(1, 8)
    return f"{a} + {b} × {c} ÷ {d} = ?", a + (b * c) // d


def gen_two_step_equation():
    x = random.randint(-10, 10)
    while x == 0:
        x = random.randint(-10, 10)
    a = random.randint(2, 9)
    b = random.randint(-15, 15)
    c = a * x + b
    if b >= 0:
        return f"Solve for x:  {a}x + {b} = {c}", x
    return f"Solve for x:  {a}x − {abs(b)} = {c}", x


def gen_geometry():
    shape = random.randint(0, 2)
    if shape == 0:
        l, w = random.randint(3, 20), random.randint(3, 20)
        return f"Area of a rectangle with length {l} and width {w}?", l * w
    elif shape == 1:
        base, height = random.randint(4, 20) * 2, random.randint(3, 15)
        return f"Area of a triangle with base {base} and height {height}?", (base * height) // 2
    s = random.randint(2, 12)
    return f"Volume of a cube with side length {s}?", s ** 3


def gen_percent_change():
    original = random.choice([50, 80, 100, 120, 150, 200, 250, 300, 400, 500])
    pct = random.choice([10, 15, 20, 25, 30, 40, 50])
    if random.randint(0, 1) == 0:
        ans = original * (1 + pct / 100)
        q = f"A price of {original} kr increases by {pct}%. New price?"
    else:
        ans = original * (1 - pct / 100)
        q = f"A price of {original} kr is reduced by {pct}%. New price?"
    return q, int(ans) if ans == int(ans) else ans


def gen_probability():
    total = random.choice([10, 12, 20, 24])
    fav = random.randint(1, total - 1)
    q = f"A bag has {total} balls: {fav} red, {total - fav} blue. P(red) as a decimal?"
    return q, round(fav / total, 2)


# ─── Level generators ───

LEVEL_1 = [gen_negative_arithmetic, gen_decimal_multiply, gen_decimal_divide, gen_fraction_to_decimal]
LEVEL_2 = [gen_percentage_of, gen_order_of_operations, gen_one_step_add_sub, gen_one_step_multiply]
LEVEL_3 = [gen_compound_expression, gen_two_step_equation, gen_geometry, gen_percent_change, gen_probability]


def generate_problem(level):
    generators = {1: LEVEL_1, 2: LEVEL_2, 3: LEVEL_3}
    pool = generators.get(level, LEVEL_3)
    return random.choice(pool)()
# EndRegion
        