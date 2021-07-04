import random
from datetime import datetime
import sqlite3 as sql

class Quiz_Handler:
    def __init__(self, file, database, name, id, Quiz_Name):
        self.file=file
        self.database=database
        self.name=name
        self.id=id
        self.Quiz_Name=Quiz_Name
        self.question_list=[]
        self.questions_seen=[]
        self.question_answer={}
        self.answers={}
        #self.start_quizzing_process() console version

    def initialize_elements(self):
        self.current_score=0
        self.current_question=0
        self.num_questions_toshow=5
        self.num_questions_limit=100

    def start_quizzing_process(self):
        self.get_file_data()
        self.begin_quizzing()
        congrats_message=''
        if self.current_score>=self.num_questions_toshow:
            congrats_message='Well done, {}!'.format(self.name)
        print("Final Score: {}. {}".format(self.current_score, congrats_message))
        self.save_data(self.database, self.name, self.id, self.current_score, self.Quiz_Name)
            
    
    def get_file_data(self):
        quizfile='quiz_data/'+self.file
        try:
            self.data=open(quizfile, 'r', encoding='UTF-8')
        except FileNotFoundError as FE:
            print("There seems to be an error with the program's file handling ({}).\nShutting down...".format(FE))
            raise SystemExit()
        except:
            print("An unidentified error occured.\nShutting down...")
            raise SystemExit()
        self.edit_data()
        self.data.close()
        
    def edit_data(self):
        for _i in range(0,self.num_questions_limit):
            question=''
            answers=''
            items=''
            pointer=False
            for items in self.data:
                if 'EOQ' in items: #if the end of question is reached, break. items retains value EOQ _[answer]_\n
                    break
                if 'a)' in items: #if the first possible answer is reached, switch to concatenating to answers
                    pointer=True
                if pointer!=True: #if the first possible answer hasn't been reached, keep concatenating to question
                    question+=items
                else:
                    answers+=items
            self.question_answer.update({question:items[-2]}) #items is EOQ _[answer]_\n , we're ignoring the \n
            self.question_list.append(question)
            self.answers.update({question:answers})
        print(len(self.question_list))
        random.shuffle(self.question_list)

    def draw_some_questions(self):
        selected_questions=[]
        answers_to_questions=[]
        for _i in range(self.num_questions_toshow):
            while True:
                question=self.question_list[random.randint(0,len(self.question_list)-1)] #draw a random question from question_list
                if question not in self.questions_seen: #if the question hasn't already been drawn...
                    self.questions_seen.append(question) #add it to the questions_seen list for future comparisons
                    selected_questions.append(question) #add it to the selected_questions list
                    answers_to_questions.append(self.question_answer[question]) #append the correct answer to the drawn question
                    print(question)
                    break
                else:
                    continue
        return selected_questions, answers_to_questions

    def begin_quizzing(self):
        for repeats in range(self.num_questions_toshow):
            self.show_random_question()
            answer=self.take_answer()
            if answer==-1:
                break
            running_score=self.evaluate_answer(answer)
            #self.score(running_score) #console version

    def show_random_question(self):
        self.current_question+=1
        print("Question {}:".format(self.current_question))
        while True:
            self.q=self.question_list[random.randint(0,len(self.question_list)-1)]
            if self.q not in self.questions_seen:
                break
        print(self.q + self.answers[self.q])
        self.questions_seen.append(self.q)
        self.format_answers(self.q)


    def format_answers(self, question_list):
        self.indiv_answers_list=[]       #creating individual_answers_list list
        for u in range(self.num_questions_toshow):
            split_markers=['a)','b)','c)','d)']  #the elements to be used for the split() function, characteristic of the replies
            reply=self.answers[question_list[u]] #go through the answers list
            self.indiv_answers=[]   #initialize the individual_answer list
            for i in split_markers: #for each element in split_markers...
                reply=reply.split(i) #do the splitting...
                if i=='a)':       #special case, element is the first one
                    reply=reply[1] #the string we care about is not the empty reply[0], but reply[1]
                    continue      #continue the 'for i in split_markers' loop
                elif i=='d)':     #special case, element is the last one.
                    self.indiv_answers.append(reply[0].strip()) #strip the whitespace from string reply[0] and append it to the list.
                    self.indiv_answers.append(reply[1].strip()) #strip the whitespace from string reply[1] and append it to the list.
                    break        #end the 'for i in split_markers' loop.
                self.indiv_answers.append(reply[0].strip()) #else, append the now "naked" answer (without the a),b),c) or d) signifier) to the list
                reply=reply[1]   #prepare for the continuation of the 'for i in split_markers' by changing reply to reply[1], where the rest of the answers are.
            self.indiv_answers_list.append(self.indiv_answers) #a single question is over, continue to the next one...
        return self.indiv_answers_list    #return the now complete indiv_answers_list for use in "question.html".


    def take_answer(self):
        while True:
            answer=input("Answer: ")
            answer=answer.strip()
            if answer=='stop' or answer==str(-1) or answer=='end':
                return -1
            elif answer not in 'abcd' or len(answer)>1 or not answer:
                print("Incorrect input.")
            else:
                return answer
    
    def evaluate_answer(self, answer):
        if answer==self.question_answer[self.q]:
            print("Correct!")
            return 1
        else:
            print("Wrong! Correct answer is", self.question_answer[self.q])
            return 0

    def score(previous_score, add): #def score(self, score): console version
        """if score!=0:
            self.current_score+=score
        print("Current score: ", self.current_score, "\n")
        return score""" #console version
        if add==True:
            return previous_score+1
        else:
            return 0

    
    def save_data(database, name, id, score, Quiz_Name, total):
        log_text_file="static/log.txt"

        print("save_data for id: {}".format(id))
        conn=sql.connect(database)
        cur=conn.cursor()

        update_score_of_user=('''UPDATE users SET last_score=? WHERE id=?;''')

        cur.execute(update_score_of_user,(score, id))
        conn.commit()
        conn.close()

        date=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log_file=open(log_text_file, "at", encoding='UTF-8')
        log_file.write("User {} finished the {} at {} with a score of {} out of {}.\n-----------------------\n".format(name, Quiz_Name, date, score, total))
    
    def read_from_log(log_file):
        #log_file="log.txt"; 

        try:
            with open(log_file, "rt", encoding='UTF-8') as log:
                log_record=log.read()
        except FileNotFoundError as FE:
            print("Error! {}".format(FE))
            return None
        print(log_record)
        return log_record

