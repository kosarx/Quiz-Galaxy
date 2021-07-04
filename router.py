from flask import Flask
from flask import render_template, redirect, url_for, abort
from flask import request, session
import version_console as authent #useful only for database handling
from quiz_handler import Quiz_Handler

app= Flask(__name__)
app.config['SECRET_KEY']="'8bfe8abbe81bdd72f6da242c7aa94f71'"

@app.route("/")
def root():
    return redirect(url_for("login"))       #start

@app.route("/login", methods = ['POST', 'GET'])
def login():
    print("ROUTE /login")
    user_database="UsersQG.db"
    session['database']=user_database #saving the database name in session
    if request.method=='POST':       #If user pressed the button
        session['user']= request.form['userName']      #get name in the form
        session['pword']= request.form['userPassword'] #get password in the form
        print("--->Data inputed: ",session['user'], session['pword'])
        username=session['user'] #just for clarity
        password=session['pword']
        conn=authent.Quiz_Galaxy.open_database_connection(user_database) #authentication...
        exists, id= authent.Quiz_Galaxy.search_through_db(conn, username, password)
        if exists=='Incorrect_pword':
            print("INCORRECT PASSWORD")
            return render_template("login.html", show= exists) #ALERT THROUGH THE BROWSER
        elif not exists:
            print("CREATING USER...") #ALERT THROUGH THE BROWSER
            conn.close()        #closing connection for now
            return redirect(url_for("login_alert"))     # possible redirecting to login_alert
        session['id']=id
        return redirect(url_for("menu"))       #redirecting to menu
    else:
        return render_template("login.html")     #First reroute from root, renders login.html

@app.route("/login_alert", methods=['POST','GET'])
def login_alert():
    print("ROUTE /login_alert", session['database'])
    if request.method=='POST':      #if user pressed submit
        print ("radio response:", request.form["radioOptions"])
        if request.form["radioOptions"] == "yes":     #if user selected 'Yes, please'
            conn=authent.Quiz_Galaxy.open_database_connection(session['database'])
            session['id']=authent.Quiz_Galaxy.insert_into_db(conn, session['user'], session['pword'])       #creating the user in the database
            conn.commit()      #saving the user in the database
            conn.close()       #closing connection for now
            return redirect(url_for("menu"))   #redirecting to menu
        else:
            return redirect(url_for("login"))   #sending the user back, redirecting to login
    else:
        return render_template("login_alert.html") #reroute from login, renders login_alert.html

@app.route("/menu")
def menu():
    print("ROUTE /menu")
    return render_template("menu.html")         #second reroute from login, renders menu.html

@app.route("/start/<quiz>/", methods=['POST', 'GET'])
def start_quiz(quiz): #reachable only through pressing the correspondant button in menu.
    print("ROUTE /start_quiz")
    valid_quizes=['python_quiz', 'c_quiz', 'javascript_quiz', 'html_css_quiz'] #acceptable query strings
    if quiz not in valid_quizes: #if not acceptable
        print("bad request:", quiz) 
        abort(404)
    else: #if acceptable
        try: #if something goes wrong, failsafe
            if request.method=='POST': #if user pressed the button:
                rQuiz= Quiz_Handler(quiz+'_data.txt', session['database'], session['user'], session['id'], quiz.title()) #create instance of Quiz_Handler
                rQuiz.initialize_elements() 
                rQuiz.get_file_data()
                rQuiz.num_questions_toshow=int(request.form.get("radioOptions")) #getting request for max number of questions to show
                session['quiz_name']=quiz #retaining which quiz info...
                session['max_questions']=rQuiz.num_questions_toshow #retaining max number of questions info...
                session['questions'], session['answers']=rQuiz.draw_some_questions() #retaining the questions and answers (a,b,c,d format) drawn info...
                session['indiv_answers_list']=rQuiz.format_answers(session['questions']) #editing the answers to 'questions' in a list (text format)...
                session['score']=0 #score starts at 0
                session['number']=1 #count starts at 1
                return redirect(url_for("questions", q=session['number'])) #redirecting to questions
            else:
                return render_template("start.html") #rendering "start.html"
        except:
            return render_template("start.html") #rendering "start.html"


@app.route("/<q>/", methods=['POST', 'GET'])
def questions(q):
    print("ROUTE /questions", q)
    if not q.isdigit() or session['score']>session['max_questions']: #simple guard against cheating the system
        print("bad request:",q,type(q))
        abort(404)
    q=int(q)
    valid_q=session['max_questions']
    if q>valid_q or q<1:
        if q==session['max_questions']+1:
            if session['quiz_name']=="html_css_quiz":
                Quiz_Name=session['quiz_name'][0:8].upper() + session['quiz_name'][8::].title()
            else: Quiz_Name=session['quiz_name'].title()

            Quiz_Handler.save_data(session['database'], session['user'], session['id'], session['score'], Quiz_Name=Quiz_Name, total=session['max_questions']) #registering the finished Quiz once
            session['log_entries']=Quiz_Handler.read_from_log("static/log.txt") #for displaying in the /finished screen
            return redirect(url_for("end_of_quiz")) #quiz is finished
        print("bad request: ", q) #else:
        abort(404)
    else:
        try:
            if request.method=='POST': #user pressed a button
                mode=request.form.get("procbutton") 
                if mode == "evaluate": #if user pressed 'submit' button
                    user_reply=request.form["reply"] #take the answer submitted
                    if user_reply == session['answers'][q-1]: #if it's the correct answer:
                        print("CORRECT!", user_reply)
                        point=1
                    else: #if the user replied incorrectly:
                        print("FALSE", user_reply, "!=", session['answers'][q-1] )
                        point=0
                    session['number']=q+1
                    session['score']+=point
                    print("current score:", session['score'])
                    
                    if session['quiz_name']=="html_css_quiz":
                        Quiz_Name=session['quiz_name'][0:8].upper() + session['quiz_name'][8::].title()
                    else: Quiz_Name=session['quiz_name'].title()
                    question_part=session['questions'][q-1].split('\n',1)[0]
                    code_part=session['questions'][q-1].split('\n',1)[1].strip()
                    
                    #load the evaluation of the reply, section:
                    return render_template("question.html", Quiz=Quiz_Name, number=q, username=session['user'], id=session['id'],\
                     current_question=question_part, code=code_part,replies=session['indiv_answers_list'][q-1], score=session['score'],\
                          correct_answer=session['answers'][q-1],is_disabled="disabled", user_answer=user_reply, evaluate=True)
                
                elif mode=="continue": #if user pressed 'continue' button
                    return redirect(url_for("questions", q=session['number'])) #start over
                else: #reloading if something went wrong...
                    if session['quiz_name']=="html_css_quiz":
                        Quiz_Name=session['quiz_name'][0:8].upper() + session['quiz_name'][8::].title()
                    else: Quiz_Name=session['quiz_name'].title()
                    question_part=session['questions'][q-1].split('\n',1)[0]
                    code_part=session['questions'][q-1].split('\n',1)[1].strip()
                    
                    return render_template("question.html", Quiz=Quiz_Name, number=q, username=session['user'], id=session['id'],\
                     current_question=question_part, code=code_part,replies=session['indiv_answers_list'][q-1], score=session['score'],\
                          correct_answer=session['answers'][q-1], is_disabled=None, user_answer=None, evaluate=False)
            else: #showing the question,
                if session['quiz_name']=="html_css_quiz":
                    Quiz_Name=session['quiz_name'][0:8].upper() + session['quiz_name'][8::].title()
                else:Quiz_Name=session['quiz_name'].title()
                question_part=session['questions'][q-1].split('\n',1)[0]
                code_part=session['questions'][q-1].split('\n',1)[1].strip()
                
                return render_template("question.html", Quiz=Quiz_Name, number=q, username=session['user'], id=session['id'],\
                     current_question=question_part, code=code_part, replies=session['indiv_answers_list'][q-1], score=session['score'],\
                          correct_answer=session['answers'][q-1], is_disabled=None, user_answer=None, evaluate=False)
        except:
            #if for some reason something went wrong, reload. radio button possibly not pressed
            return render_template("question.html", Quiz=session['quiz_name'].title(), number=q, username=session['user'], id=session['id'],\
                 current_question=session['questions'][q-1].split('\n',1)[0], code=session['questions'][q-1].split('\n',1)[1].strip(),\
                      replies=session['indiv_answers_list'][q-1], is_disabled=None, score=session['score'], correct_answer=session['answers'][q-1],\
                          )
#--------

@app.route("/finished", methods=["POST", "GET"])
def end_of_quiz():
    print("ROUTE /end of quiz")
    congratulations_message='' #initializing
    try:
        if session['quiz_name']=="html_css_quiz":
                Quiz_Name=session['quiz_name'][0:8].upper() + session['quiz_name'][8::].title()
        else:Quiz_Name=session['quiz_name'].title()
    except: return redirect(url_for("menu"))
    
    if request.method=='POST': #if user pressed button
        button_pressed=request.form.get("button") #get requested button
        if button_pressed=="menu": #if user wants to go to menu
            return redirect(url_for("menu")) #redirect
        elif button_pressed=="restart": #if user wants to restart
            return redirect(url_for("start_quiz", quiz=session['quiz_name'])) #redirect to start_quiz
        else:
            #if something went wrong, reload
            return render_template("end_of_quiz.html", Quiz=Quiz_Name, score=session['score'], total_questions=session['max_questions'],\
                user=session['user'], id=session['id'])
    if session['score']==session['max_questions']: #if perfect score
        congratulations_message="Well done! All questions answered correctly!"
    #rendering end_of_quiz template
    return render_template("end_of_quiz.html", Quiz=Quiz_Name, score=session['score'],congratulations_message=congratulations_message,\
         total_questions=session['max_questions'], user=session['user'], id=session['id'], log_entries=session.get('log_entries'))

@app.errorhandler(404)
def page_not_found(error):
    return '<h1>This page does not exist<h1> <h1><strong>404</strong></h1>', 404

if __name__=='__main__':
    app.run(debug=False)