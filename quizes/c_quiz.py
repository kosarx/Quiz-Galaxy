import quiz_handler as qz

class C_Quiz(qz.Quiz_Handler):
    def __init__(self, file, database, name, id):
        print('-----------------------------')
        print("Welcome to the C Programming Language Quiz!")
        qz.Quiz_Handler.__init__(self, file, database, name, id, C_Quiz.__name__)
        print("Exiting C Quiz.")

    
if __name__=='__main__':
    C_Quiz("c_quiz_data")
