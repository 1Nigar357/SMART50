from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from functools import wraps
from time import sleep
from cryptography.fernet import Fernet

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

key = b'kNLPZ2x6Ez7-JXv6eghWclD59YV8Oq7KgL2vV7RJx5g='
cipher_suite = Fernet(key)


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

subjects = (
     
    "PROBABILITY",
    "LAB",
    "INTRO TO DATA SCIENCE",
    "TURKISH",
    "ENGLISH",
    "DATA STRUCTURES",
    "WATERLOO",
    "APPLICATION",
    "INTERNSHIPS",
    "GENERAL"
)

parts = (
    "Noun",
    "Adjective",
    "Verb",
    "Adverb",
    "Conjuction",
    "Abbreviation",
    "Exclamation",
    "Interjection"
)


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/homework", methods=["GET", "POST"])
@login_required
def homework():
    if request.method == 'GET':
        homework = db.execute("SELECT * FROM homework WHERE user_id = ? ORDER BY deadline", session["user_id"])
        return render_template("homework.html", homework=homework)


@app.route("/addHomework", methods=["GET", "POST"])
@login_required
def addHomework():
    if request.method == 'POST':
        subject = request.form.get("subject")
        requirements = request.form.get("requirements").capitalize()
        deadline = request.form.get("deadline")
        description = request.form.get("description").capitalize()

        if not subject or not description or not requirements:
            flash("Fill in all the required fields")
            return render_template("/addHomework.html", subjects=subjects)
        elif subject not in subjects:
            flash("Error")
            return render_template("/addHomework.html", subjects=subjects)

        db.execute("INSERT INTO homework (user_id, subject, materials_required, deadline, description) VALUES(?, ?, ?, ?, ?)",
                    session["user_id"], subject, requirements, deadline, description)

        return redirect("/homework")

    else:
        return render_template("/addHomework.html", subjects=subjects)


@app.route("/completed", methods=["GET", "POST"])
@login_required
def completed():

    id = request.form.get("id")
    if not id:
        flash("Error")

    db.execute("DELETE FROM homework WHERE id = ?", id)
    flash("Well done!")

    return redirect("/homework")


@app.route("/vocab", methods=["GET", "POST"])
@login_required
def vocab():
    if request.method == 'GET':
        vocab = db.execute("SELECT * FROM vocab WHERE user_id = ? ORDER BY word", session["user_id"])
        return render_template("vocab.html", vocab=vocab)


@app.route("/addWord", methods=["GET", "POST"])
@login_required
def addWord():
    if request.method == 'POST':
        word = request.form.get("word")
        part = request.form.get("part")
        definition = request.form.get("definition")
        synonym = request.form.get("synonym")
        antonym = request.form.get("antonym")
        sample = request.form.get("sample")

        if not word or not part or not definition:
            flash("Fill in all the required fields")
            return render_template("/addWord.html", parts=parts)

        elif part not in parts:
            flash("Error")
            return render_template("/addWord.html", parts=parts)

        db.execute("INSERT INTO vocab (user_id, word, part, definition, synonym, antonym, sample) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    session["user_id"], word, part, definition, synonym, antonym, sample)

        return redirect("/vocab")

    else:
        return render_template("/addWord.html", parts=parts)



@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():

    id = request.form.get("id")
    if not id:
        flash("Error")

    db.execute("DELETE FROM vocab WHERE id = ?", id)
    return redirect("/vocab")

@app.route("/login", methods=["GET", "POST"])
def login():
     # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        newUsername = request.form.get("username")
        newPassword = request.form.get("password")
        verifyPassword = request.form.get("confirmation")

        # Ensure username was submitted
        if not newUsername:
            flash("must provide username")
            return render_template("register.html")

        # Ensure that the username doesn't exist
        check = db.execute("SELECT username FROM users")
        for i in check:
            if i["username"] == newUsername:
                flash("username exists")
                return render_template("register.html")

        # Ensure password was submitted
        if not newPassword:
            flash("must provide password")
            return render_template("register.html")

        # Ensure password was submitted
        elif not verifyPassword or not newPassword == verifyPassword:
            flash("password doesn't match")
            return render_template("register.html")


        # Hash the Password
        hashedPassword = generate_password_hash(newPassword, method='pbkdf2:sha256', salt_length=7)
        db.execute("INSERT INTO users (username, hash) VALUES(?,?)", newUsername, hashedPassword)
        id = db.execute("SELECT id FROM users WHERE username = ?", newUsername)

        # Remember which user has logged in
        session["user_id"] = id[0]['id']

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/addWordDict", methods=["GET", "POST"])
@login_required
def addWordDict():
    if request.method == 'POST':
        word = request.form.get("word").lower()

        if not word:
            flash("Fill in all the required fields")
            return render_template("addWordDict.html")


        web2 = requests.get("https://www.britannica.com/dictionary/" + word)
        data2 = web2.content
        soup2 = BeautifulSoup(data2, features="html.parser")

        web3 = requests.get("https://sentence.yourdictionary.com/" + word)
        data3 = web3.content
        soup3 = BeautifulSoup(data3, features="html.parser")

        web4 = requests.get("https://www.wordhippo.com/what-is/the-opposite-of/" + word + ".html")
        data4 = web4.content
        soup4 = BeautifulSoup(data4, features="html.parser")

        web5 =  requests.get("https://www.wordhippo.com/what-is/another-word-for/" + word + ".html")
        data5 = web5.content
        soup5 = BeautifulSoup(data5, features="html.parser")

        web6 =  requests.get("https://www.wordhippo.com/what-is/the-meaning-of-the-word/" + word + ".html")
        data6 = web6.content
        soup6 = BeautifulSoup(data6, features="html.parser")

        d = soup2.find_all("span", "def_text")
        part = soup6.find_all("div", "defv2wordtype")
        synonym = soup5.find_all("div", "wb")
        antonym = soup4.find_all("div", "wb")
        sample = soup3.find_all("p", "sentence-item__text")



        a = 0
        for i in synonym:
            if a == 0:
                synonym2 = i
            elif a == 3:
                break
            else:
                synonym2.append(", ")
                synonym2.append(i)
            a += 1

        a = 0
        for i in antonym:
            if a == 0:
                antonym2 = i
            elif a == 3:
                break
            else:
                antonym2.append(", ")
                antonym2.append(i)
            a += 1

        a = 0
        part2 = []
        for i in part:
            if a == 0:
                part2.append(i)
                # part2 = i.text
            else:
                if i not in part2:
                    part2.append(i)
            a += 1

        a = 0
        part3 = []
        for i in part2:
            if a == 0:
                part3.append(i.text)
                # part2 = i.text
            else:
                part3.append(i.text)
            a += 1

        string = ', '.join(map(str,part3))





        try:
            id = db.execute("INSERT INTO vocab (user_id, word, part, definition, sample, synonym, antonym) VALUES(?,?, ?, ?, ?, ?, ?)",
            session["user_id"], word, string, d[0].text, sample[0].text, synonym2.text, antonym2.text)
        except:
            flash("Word could not be found")
            return redirect("/vocab")

        if len(d) > 1:
            db.execute("UPDATE vocab SET d1 = ? WHERE id = ?", d[1].text, id)
        if len(d) > 2:
            db.execute("UPDATE vocab SET d2 = ? WHERE id = ?", d[2].text, id)
        if len(d) > 3:
            db.execute("UPDATE vocab SET d3 = ? WHERE id = ?", d[3].text, id)
        if len(d) > 4:
            db.execute("UPDATE vocab SET d4 = ? WHERE id = ?", d[4].text, id)
        if len(d) > 5:
            db.execute("UPDATE vocab SET d5 = ? WHERE id = ?", d[5].text, id)
        if len(d) > 6:
            db.execute("UPDATE vocab SET d6 = ? WHERE id = ?", d[6].text, id)
        if len(d) > 7:
            db.execute("UPDATE vocab SET d7 = ? WHERE id = ?", d[7].text, id)
        if len(d) > 8:
            db.execute("UPDATE vocab SET d8 = ? WHERE id = ?", d[8].text, id)
        if len(d) > 9:
            db.execute("UPDATE vocab SET d9 = ? WHERE id = ?", d[9].text, id)
        if len(d) > 10:
            db.execute("UPDATE vocab SET d10 = ? WHERE id = ?", d[10].text, id)
        if len(d) > 11:
            db.execute("UPDATE vocab SET d11 = ? WHERE id = ?", d[11].text, id)

        return redirect("/vocab")

    else:
        return render_template("/addWordDict.html", parts=parts)



@app.route("/resetPassword", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == 'POST':
        oldPassword = request.form.get("oldPassword")
        newPassword = request.form.get("newPassword")
        confirmation = request.form.get("confirmation")

        # Ensure old password was submitted
        if not oldPassword:
            flash("must provide old password")
            return render_template("resetPassword.html")

        # Ensure new password was submitted
        if not newPassword:
            flash("must provide new password")
            return render_template("resetPassword.html")

        # Ensure password was submitted
        elif not confirmation or not newPassword == confirmation:
            flash("confirmation password doesn't match")
            return render_template("resetPassword.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], oldPassword):
            flash("wrong password")
            return render_template("resetPassword.html")

        # Ensure that new password isn't the same as the old password
        if oldPassword == newPassword:
            flash("your new password can't be your old password")
            return render_template("resetPassword.html")

        # Hash the Password
        hashedPassword = generate_password_hash(newPassword, method='pbkdf2:sha256', salt_length=3)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashedPassword, session["user_id"])

        return redirect("/")

    else:
        return render_template("resetPassword.html")
    






portals = {
    "BBF 103E":"34297.107352",
    "YZV 104E":"32328.107498",
    "ING 112A": "27079.107010",
    "BBF 201E": "35291.111472"
}

def addGrade(subject, assigment, grade):
    '''  If the grade is not present in the database, adds the grade to the database '''
    # Checks if the grade for the current assigment exists in the database
    result = db.execute("SELECT COUNT(*) FROM grades WHERE user_id =? AND exam_name = ?", session["user_id"],  assigment)[0]
    if result["COUNT(*)"] != 0 or  grade =='-':
        return
    
    # If the grade is not in the databse, add it 
    db.execute("INSERT INTO grades (user_id, subject, exam_name, grade) VALUES(?, ?, ?, ?)",
            session["user_id"], subject, assigment, grade)

@app.route("/grades", methods=["GET", "POST"])
@login_required
def grades():

    """ Display the grades and check for any updates in the grades """
    # User reached route via POST (by submitting a form via POST)
    if request.method == 'POST':
        
        # Get the username and password for the school account associated with the current user
        username =  db.execute("SELECT username FROM school_accounts WHERE user_id =?", session["user_id"])
        password =  db.execute("SELECT password FROM school_accounts WHERE user_id =?", session["user_id"])
        
        # If the user has not previously entered a school account, redirect to changeSchoolAccount route
        if len(username) ==0 or len(password) == 0:
            flash("must provide username and password of your university account")
            return redirect("/changeSchoolAccount")
        
        username = username[0]["username"]
        password = password[0]["password"]
        
        # Decrypt the password
        password = cipher_suite.decrypt(password).decode()
       
        # Use selenium on chrome to access the portal and login to the school account
        driver = webdriver.Chrome()
        driver.get("https://girisv3.itu.edu.tr/Login.aspx?...")
        driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$tbUserName").send_keys(username)
        driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$tbPassword").send_keys(password)
        driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$btnLogin").click()
        
    
        # Iterate over each class portal
        for key,value in portals.items():

            # Get the URL
            
            grades_portal = "https://ninova.itu.edu.tr/Sinif/" + value + "/Notlar"
            driver.get(grades_portal)
            sleep(2)
            # Parse the HTML content
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Get the assigment names and corresponding grades
            assigments = soup.find_all('span', id=lambda x: x and x.startswith('eas'))
            grades = soup.find_all("span", id=lambda x: x and x.endswith('txtNot'))
            
            for assigment, grade in zip(assigments,grades):
                #  Call the addGrade function
                addGrade(key, assigment.text.strip(), grade.text.strip())

        # Access the MATHAVUZ website
        sleep(2)
        mathavuz = "https://www.mathavuz.itu.edu.tr"
        driver.get(mathavuz)

        # Login to the website
        driver.find_element(By.CLASS_NAME, "btn.btn-outline-primary").click()
        sleep(2)

        # Open the webpage where the grades are displayed
        mathavuz = "https://www.mathavuz.itu.edu.tr/mypage.php"
        driver.get(mathavuz)
        
        # Parse the HTML content
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Collect the grades
        data = soup.find_all('button', attrs={
            'data-target': lambda val: val and val.startswith('#modal') and val.endswith('MAT104E')
        })  
        data_string = [str(grade) for grade in data]
        
        # Get the list of exam names
        exam_name = []
        for grade in data_string:             
            exam_name_start = grade.find('modal') + len('modal')   
            exam_name.append(grade[exam_name_start:exam_name_start+2].strip())

        for i, grade in enumerate(data):
            assigment = exam_name[i]
            grade = grade.text.strip()[:-1]

            #  Call the addGrade function
            addGrade("MAT 104E", assigment.strip(), grade)
        
        return redirect("/grades")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Get the list of grades and assigment/exam names from the database
        grades_data = db.execute("SELECT * FROM grades WHERE user_id = ?", session["user_id"])
        
        # Render the 'grades.html' template with the grades data
        return render_template("grades.html", grades=grades_data)
    

@app.route("/changeSchoolAccount", methods=["GET", "POST"])
@login_required
def changeSchoolAccount():

    """ Render the html code and change the school account associated with the current user"""

    # User reached route via POST (by submitting a form via POST)
    if request.method == 'POST':

        # Get the username and password
        username = request.form.get("username") 
        password = request.form.get("password")
        
        # Ensure username was submitted
        if not username:
            flash("must provide username")
            return render_template("changeSchoolAccount.html")

        # Ensure password was submitted
        elif not password:
            flash("must provide password")
            return render_template("changeSchoolAccount.html")
        
        # Encrypt the password
        password = cipher_suite.encrypt(password.encode())

        # Delete the previous school account associated with this account (if exists)
        count =  db.execute("SELECT COUNT(*) FROM school_accounts WHERE user_id =?", session["user_id"])
        if count: 
            db.execute("DELETE FROM school_accounts WHERE user_id = ?", session["user_id"])

        # Add the new school account to the databse
        db.execute("INSERT INTO school_accounts (user_id, username, password) VALUES(?, ?, ?)", session["user_id"], username, password)
        
        # Empty the grades associated with the previous school account
        db.execute("DELETE FROM grades WHERE user_id = ?", session["user_id"])

        # Redirect to the grades route
        return redirect("/grades")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Render the 'ChangeSchoolAccount.html' template
        return render_template("changeSchoolAccount.html")