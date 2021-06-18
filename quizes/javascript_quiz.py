import quiz_handler as qz

class JavaScript_Quiz(qz.Quiz_Handler):
    def __init__(self, file, database, name, id):
        print('-----------------------------')
        print("Welcome to the JavaScript Programming Language Quiz!")
        qz.Quiz_Handler.__init__(self, file, database, name, id, JavaScript_Quiz.__name__)
        print("Exiting JavaScript Quiz.")

    
if __name__=='__main__':
    JavaScript_Quiz("javascript_quiz_data")
