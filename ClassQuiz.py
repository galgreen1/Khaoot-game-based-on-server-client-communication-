import random
import json
 #class quiz- Contains features of a general questionnaire


# read the question data and save him to variables
with open('quizData.json', 'r') as file:
    quiz_data = json.load(file)

categories = quiz_data['categories']
questions = quiz_data['questions']
answers = quiz_data['answers']
options = quiz_data['options']


class quiz:
    players = []

    # construct a quiz according to the category and username it gets from the client
    def __init__(self, category, username):
        self.category = category
        self.questions = questions[category]
        self.players = [username]
        self.score = {}
        self.InProgress = False

        # choose a random id to new quiz
        rand = random.randint(1, 10000)
        self.id = rand
        # reset scores
        self.score[username] = 0
        self.IsOver = False

    def start(self):
        # defult Definitions
        self.used = []
        self.current_question = ''
        self.correct_answer = ''
        self.current_options = []

    def GameOver(self):
        self.IsOver = True

    def get_score(self):
        return self.score

    # handle the score of every player in the quiz
    def HandleScore(self, username, score1):
        self.score[username] = score1


    def get_options(self):
        return options[self.current_question]

    def getID(self):
        return self.id

    def getPlayers(self):
        return self.players

    def getQ(self):
        return self.questions

    def usedQ(self, question):
        self.used.append(question)

    # take care in providing questions in random order without repetitions
    def getCurrentQ(self):
        #if all the questions were already provided: game over
        if len(self.questions) == len(self.used):
            #finish game
            self.current_question = ''
            self.current_options = ''
            self.category = ''
            self.correct_answer = ''

        else:
            question = random.choice(self.questions)
            while question in self.used:
                question = random.choice(self.questions)
            self.usedQ(question)
            self.current_question = question
            self.correct_answer = answers[self.current_question]
            self.current_options = options[question]
            return question

    def get_correct_answer(self):
        return self.correct_answer

    def getCategory(self):
        return self.category

    def get_used(self):
        return self.used

    def add_players(self, username):
        self.players.append(username)









