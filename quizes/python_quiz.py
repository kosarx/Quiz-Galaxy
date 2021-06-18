import quiz_handler as qz

class Python_Quiz(qz.Quiz_Handler):
    def __init__(self, file, database, name, id):
        print('-----------------------------')
        print("Welcome to Python Quiz!")
        qz.Quiz_Handler.__init__(self, file, database, name, id, Python_Quiz.__name__)
        print("Exiting Python Quiz.")

    
if __name__=='__main__':
    Python_Quiz("python_quiz_data")