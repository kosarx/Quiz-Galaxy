import quiz_handler as qz

class HTML_CSS_Quiz(qz.Quiz_Handler):
    def __init__(self, file, database, name, id):
        print('-----------------------------')
        print("Welcome to the JavaScript Programming Language Quiz!")
        qz.Quiz_Handler.__init__(self, file, database, name, id, HTML_CSS_Quiz.__name__)
        print("Exiting JavaScript Quiz.")

    
if __name__=='__main__':
    HTML_CSS_Quiz("html_css_quiz_data")
