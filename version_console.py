from sqlite3.dbapi2 import connect
from quizes import python_quiz, c_quiz, javascript_quiz, html_css_quiz
import sqlite3 as sql

#console version, used only for the database-related functions.
class Quiz_Galaxy:
    def __init__(self):
        print('===========================')
        print("Welcome to Quiz Galaxy!")
        name, id, database=self.log_in()
        self.name, self.id, self.database= name, id, database
        while True:
            print('-----------------------')
            print("This is the Quiz Hub:")
            self.quiz_choice=self.get_input("select: ")
            self.open_quiz(self.quiz_choice)
    
    def get_input(self, add_on):
        x=input(add_on)
        return x

    def log_in(self):
        name=self.get_input("Enter your name: ")
        password=self.get_input("Enter your password: ")
        database="UsersQG.db"
        conn=Quiz_Galaxy.open_database_connection(database)
        print("--->connection opened")
        #self.delete_user(conn)  ##Debugging
        #print("--->deletion done")
        found, id=Quiz_Galaxy.search_through_db(conn, name, password)
        if not found:
            id=Quiz_Galaxy.insert_into_db(conn, name, password)
            print("--->insertion done")
        conn.commit()
        print("--->committed data")
        conn.close()
        print("--->connection closed")
        
        return name, id, database

    def open_quiz(self, choice):
        if choice==str(0):
            python_quiz.Python_Quiz("python_quiz_data.txt", self.database, self.name, self.id)
        elif choice==str(1):
            c_quiz.C_Quiz("c_quiz_data.txt", self.database, self.name, self.id)
        elif choice==str(2):
            javascript_quiz.JavaScript_Quiz("javascript_quiz_data.txt", self.database, self.name, self.id)
        elif choice==str(3):
            html_css_quiz.HTML_CSS_Quiz("html_css_quiz_data.txt", self.database, self.name, self.id)
        else:
            if ("exit" in choice or choice=="" or choice==str(-1) or choice=='end'):
                print("Goodbye.")
                raise SystemExit()
            else:
                print("Incorrect choice.")

    def open_database_connection(database):
        conn=sql.connect(database)
        cur=conn.cursor()

        user_db=('''CREATE TABLE IF NOT EXISTS users(
                    id integer PRIMARY KEY,
                    user_name text NOT NULL,
                    password text NOT NULL,
                    last_score int );''')
        
        cur.execute(user_db)

        return conn
    
    def search_through_db(conn, name, password):
        cur=conn.cursor()

        search_user_db=('''SELECT user_name, password, id FROM users;''')

        usernames_passwords=cur.execute(search_user_db)
        for u,p,id in usernames_passwords:
            print(u, p, id)
            if name==u and p==password:
                print("--->User found! Welcome back.")
                return True, id
            elif name==u and p!=password:
                print("User with name {} already exists, but with a different password. Try again.". format(name))
                #raise SystemExit # for command line. If in browser, simply bar entry
                return 'Incorrect_pword', None 
        else:
            print("--->User not found. Creating now...")
            return False, None

    def insert_into_db(conn, user_name, password):
        cur=conn.cursor()

        insert_user_db=('''INSERT INTO users(
                            user_name,
                            password)
                            VALUES (?,?)''')
        cur.execute(insert_user_db, (user_name, password))

        select_user_id_db=('''SELECT id FROM users WHERE user_name=? AND password=?''')
        for i in cur.execute(select_user_id_db, (user_name, password)):
            id=i[0]
        return id

    #debugging
    def delete_user(self, conn):
        cur=conn.cursor()

        delete_user_db=('''DELETE FROM users WHERE id=?''')

        cur.execute(delete_user_db,None)
        cur.execute(delete_user_db,None)
        conn.commit()



if __name__=='__main__':
    Quiz_Galaxy()