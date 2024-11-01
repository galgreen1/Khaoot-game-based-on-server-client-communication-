import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import socket
import threading
import json
from datetime import datetime


# Constants
HOST = '127.0.0.1'
PORT = 5005


class QuizClient:

    def __init__(self, root):

        self.root = root
        self.root.title("Quiz Game Client")

        # Server connection variables
        self.server_host = '127.0.0.1'
        self.server_port = 5005
        self.client_socket = None

        self.score = 0

        # Quiz variables
        self.quiz_in_progress = False
        self.current_question = ''
        self.username = ''

        self.IsAdmin = True
        self.ID = '0'

        self.NewOrExist_chosen = False
        self.NewGame_chose_category = True

        self.correct_answer = ''
        self.got_correct_answer = False

        self.current_time = 0
        self.answer_time = 0

        # GUI components
        self.label_status = ttk.Label(root, text="Not connected to the server", font=('Helvetica', 12))
        self.entry_username = ttk.Entry(root, font=('Helvetica', 12))
        self.button_connect = ttk.Button(root, text="Connect to Server", command=self.connect_to_server)

        self.timer_label = ttk.Label(root, text="", font=('Helvetica', 12))
        self.timer_interval = 1000  # Timer update interval in milliseconds
        self.timer_label.grid(row=2, column=0, columnspan=2, pady=10)

        # self.button_start_quiz = ttk.Button(root, text="Start Quiz", command=self.start_quiz)
        self.label_question = ttk.Label(root, text="", font=('Helvetica', 12))
        # self.entry_answer = ttk.Entry(root, font=('Helvetica', 12))
        self.entry_answer = ttk.Combobox(root, values=[])
        self.button_submit = ttk.Button(root, text="Submit Answer", command=self.submit_answer)

        self.text_scores = tk.Text(root, height=10, width=40, state=tk.DISABLED, font=('Helvetica', 12))

        # Layout GUI components
        self.label_status.grid(row=0, column=0, columnspan=2, pady=10)
        self.entry_username.grid(row=1, column=0, padx=10, pady=10)
        self.button_connect.grid(row=1, column=1, padx=10, pady=10)

        self.label_question.grid(row=4, column=0, columnspan=2, pady=10)
        self.entry_answer.grid(row=5, column=0, padx=10, pady=10)
        self.button_submit.grid(row=5, column=1, padx=10, pady=10)

        self.text_scores.grid(row=7, column=0, columnspan=2, pady=10)

    def start_timer(self, duration):
        self.timer_remaining = duration
        self.update_timer()

    def update_timer(self):
        if self.timer_remaining > 0:
            self.timer_label.config(text=f"Time left: {self.timer_remaining} seconds")
            self.timer_remaining -= 1
            self.root.after(self.timer_interval, self.update_timer)
        else:
            self.timer_label.config(text="Time's up!")
            # Perform actions when time is up (e.g., submit answer automatically)

    def connect_to_server(self):

        self.username = self.entry_username.get().strip()  # removes leading and trailing whitespaces
        if not self.username:
            messagebox.showerror("Error", "Please enter a username")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_host, self.server_port))
            self.client_socket.send(f'USERNAME {self.username}'.encode('utf-8'))

            time.sleep(0.1)
            message = self.client_socket.recv(1024).decode('utf-8')
            # if the username is caught so the connection will be closed and the window will be closed
            if 'caught username!' in message:
                messagebox.showerror("Error", "Caught username!\n Game will close in a few seconds")
                self.client_socket.close()
                self.root.after(5000, self.root.destroy)

            # if username is good so the client need to choose new game or exist game

            self.label_status.config(text=f"Connected as {self.username}")
            self.button_newQuiz = ttk.Button(self.root, text="Start new Quiz", command=self.new_game)
            self.button_ExistQuiz = ttk.Button(self.root, text="Start Exist Quiz", command=self.exist_game)
            self.button_newQuiz.grid(row=2, column=0, columnspan=2, pady=10)
            self.button_ExistQuiz.grid(row=2, column=1, padx=10, pady=10)
            self.button_connect.config(state=tk.DISABLED)

            threading.Thread(target=self.receive_messages).start()

        # in case of communication error close the game after showing text with the error
        except (socket.error, ConnectionRefusedError):
            messagebox.showerror("Error", "Unable to connect to the server")
            self.root.after(5000, self.root.destroy)

    def receive_messages(self):
        try:

            while True:
                # wait for the client to choose new or exist game
                if self.NewOrExist_chosen == True:
                    break
            while True:
                if not self.IsAdmin:
                    break
                # get here if the client is an admin (new game)
                # waiting for the client to choose category
                if self.NewGame_chose_category:
                    # get the game ID from the server
                    self.ID = self.client_socket.recv(1024).decode('utf-8')
                    # print(f'id:{self.ID}')
                # break if the ID was received (the value is different from defult)
                if self.ID != '0':
                    break
            #print(f'id: {self.ID}')
            while True:
                if self.IsAdmin:
                    break
                # get here if the client is not an admin (exist game)
                # waiting to see what the server say about the ID
                valid = self.client_socket.recv(1024).decode('utf-8')
                # if there isnt a game with that ID close the game
                if "There isnt a game with that ID! " in valid:
                    print(f'{valid}')
                    messagebox.showerror("Error", "there isn't a game with that ID")
                    self.client_socket.close()
                    self.root.destroy()

                else:
                    # if there is a game with that ID show text that the client is connected to the game
                    if "There is a game with that ID!" in valid:
                        self.labal_connect_to_exist=ttk.Label(self.root, text="connected to exist game \n waiting for the admin to start the questions")
                        self.labal_connect_to_exist.grid(row=2, column=0, columnspan=2, pady=10)
                        print(f'{valid}')
                        break
                    else:
                        # if there is a game with that ID  that already started close the window
                        if "The game has already started" in valid:
                            print(f'{valid}')
                            messagebox.showerror("Error", "The game has already started!")
                            self.client_socket.close()
                            self.root.destroy()

            while True:
                message = self.client_socket.recv(1024).decode('utf-8')
                print(f'message:{message}')
                if not message:
                    # print(f'didnt get message')
                    break

                if "Quiz starting!" in message:
                    if self.IsAdmin == False:
                        # there this button only for not admins
                        self.labal_connect_to_exist.grid_remove()

                    self.quiz_in_progress = True
                    self.label_answer = ttk.Label(self.root, text="", font=('Helvetica', 15))
                    self.label_answer.grid(row=5, column=0, padx=12, pady=12)
                elif "game over!" in message:
                    self.client_socket.send(str(self.score).encode('utf-8'))
                    self.quiz_in_progress = False

                    self.label_gameOver = ttk.Label(self.root, text="Game Over!!:", font=('Helvetica', 12))
                    self.label_gameOver.grid(row=7, column=0, columnspan=2, pady=10)

                    time.sleep(3)
                    score = self.client_socket.recv(1024).decode('utf-8')
                    # translate back to dict
                    score_dict = json.loads(score)

                    #  (delete all widgets)
                    # print(f'scores: {score_dict}')
                    for widget in self.root.winfo_children():
                        widget.destroy()
                    # Display the score dictionary
                    for key in score_dict:
                        score_dict[key] = int(score_dict[key])
                    sorted_score_dict = dict(sorted(score_dict.items(), key=lambda item: item[1], reverse=True))

                    text_widget = tk.Text(self.root, width=40, height=10, font=('Helvetica', 12))
                    text_widget.pack(padx=10, pady=10)

                    # Insert the formatted score dictionary into the Text widget
                    text_widget.insert(tk.END, "Score:\n")
                    for player, score in sorted_score_dict.items():
                        text_widget.insert(tk.END, f"{player}: {score}\n")
                        text_widget.insert(tk.END, f"\n")

                    # Disable editing in the Text widget
                    text_widget.config(state=tk.DISABLED)

                    # Schedule the window to close after 2 seconds
                    self.root.after(2000, self.root.destroy)

                elif self.quiz_in_progress:

                    if "Correct Answer:" in message:
                        self.got_correct_answer = True
                        answer = message.split(':')
                        answer = answer[1]
                        self.correct_answer = answer.replace("{", "").replace("}", "").strip()
                        # print(f'correct answer: {self.correct_answer}')
                    else:
                        message1 = self.client_socket.recv(1024).decode('utf-8')
                        if not message1:
                            break
                        # convert the options string to an array
                        options = []
                        option = ""
                        for letter in message1:
                            if letter != "," and letter != "[" and letter != "]" and letter != "'"  :
                                option += letter
                            else:
                                if option != "":
                                    options.append(option)
                                    option = ""
                                else:
                                    option = ""

                        self.current_question = message
                        self.start_timer(duration=9)
                        self.label_answer.destroy()
                        self.button_submit.config(state=tk.NORMAL)
                        # print(f'question: {message}')
                        self.current_time = datetime.now().timestamp()
                        self.label_question.config(text=self.current_question)
                        self.entry_answer.config(values=options)
        except (socket.error, ConnectionResetError):
            self.client_socket.close()
            self.label_status.config(text="Connection lost")
            self.root.after(4000, self.root.destroy)

    def getUsername(self):
        return self.username

    # if X is pressed close the game only for this client
    def disconnect_from_server(self):
        self.label_disconnect = ttk.Label(self.root, text="disconnecting!!!", font=('Helvetica', 22))
        self.label_disconnect.grid(row=2, column=1, columnspan=2, pady=10)
        if self.client_socket:
            time.sleep(1)
            self.label_disconnect.grid_forget()
            self.client_socket.close()
        self.root.destroy()

    def new_game(self):
        self.button_newQuiz.grid_remove()
        self.button_ExistQuiz.grid_remove()
        self.NewGame_chose_category = False
        message = "new game"
        self.client_socket.send(message.encode('utf-8'))
        time.sleep(0.1)
        self.NewOrExist_chosen = True
        self.label_category = ttk.Label(self.root, text="Select a Category", font=('Helvetica', 12))
        self.combo_category = ttk.Combobox(self.root, values=['General Knowledge', 'Science', 'History'])
        self.button_start_quiz = ttk.Button(self.root, text="Start Quiz", command=self.start_new_quiz)
        self.label_category.grid(row=2, column=0, columnspan=2, pady=10)
        self.combo_category.grid(row=3, column=0, padx=10, pady=10)
        self.button_start_quiz.grid(row=3, column=1, padx=10, pady=10)
        self.IsAdmin = True

    def start_questions(self):
        txt = "start questions"
        self.client_socket.send(txt.encode('utf-8'))
        self.button_start_questions.grid_remove()
        self.label_category.grid_remove()
        self.combo_category.grid_remove()

    def start_new_quiz(self):
        self.button_start_quiz.grid_remove()

        self.button_start_questions = ttk.Button(self.root, text="Start Questions", command=self.start_questions)
        self.button_start_questions.grid(row=4, column=0, padx=10, pady=10)

        if not self.quiz_in_progress:
            category = self.combo_category.get()
            self.client_socket.send(category.encode('utf-8'))
            self.NewGame_chose_category = True
            print(f'category:{category}')

            # to fix self to quiz!
            while self.ID == '0':
                continue
            idd = self.ID
            print(f'idd: {idd}')
            self.label_id = ttk.Label(self.root, text=f'id of the game:{idd}', font=('Helvetica', 12))
            self.label_id.grid(row=1, column=1, padx=10, pady=10)

        elif self.quiz_in_progress:
            messagebox.showinfo("Quiz in Progress", "A quiz is already in progress")

    def submit_answer(self):

        self.button_submit.config(state=tk.DISABLED)
        if self.quiz_in_progress:
            time.sleep(1)
            answer = self.entry_answer.get().strip()
            self.answer_time = datetime.now().timestamp()
            score_time = self.answer_time - self.current_time
            print(f'answer:{answer}')
            #time.sleep(1)
            while self.got_correct_answer == False:
                pass


            print(f'self.correctanswer:{self.correct_answer}')
            if answer:
                answer1 = "Not Correct Answer!"
                if answer == self.correct_answer:
                    answer1 = "Correct Answer!"
                    print('answer correct!')

                    self.score += max(1, 10-int(score_time/2))

                print(f'score: {self.score}')
                self.label_answer = ttk.Label(self.root, text=f'{answer1}', font=('Helvetica', 15))
                self.label_answer.grid(row=5, column=0, padx=12, pady=12)
                self.label_score = ttk.Label(self.root, text=f'your score: {self.score}', font=('Helvetica', 15))
                self.label_score.grid(row=6, column=0, padx=12, pady=12)

            else:
                messagebox.showerror("Error", "Please enter an answer")

            self.correct_answer = ''
            self.got_correct_answer = False

            self.entry_answer.delete(0, tk.END)
        else:
            messagebox.showinfo("Quiz not started", "The quiz has not started yet")

    def exist_game(self):
        self.button_ExistQuiz.grid_remove()
        self.IsAdmin = False

        #self.ExistGame = True
        message = "exist game"
        self.client_socket.send(message.encode('utf-8'))
        time.sleep(0.2)
        self.NewOrExist_chosen = True
        self.label_id = ttk.Label(self.root, text="entry game ID", font=('Helvetica', 12))
        self.entry_ID = ttk.Entry(self.root, font=('Helvetica', 12))
        self.button_submit = ttk.Button(self.root, text="Submit ID", command=self.join_exist)
        #self.button_start_quiz = ttk.Button(self.root, text="Start new Quiz", command=self.start_new_quiz)
        self.label_id.grid(row=2, column=0, columnspan=2, pady=10)
        self.entry_ID.grid(row=4, column=0, padx=10, pady=10)
        self.button_submit.grid(row=4, column=1, padx=10, pady=10)

    def join_exist(self):
        self.label_id.grid_remove()
        self.button_newQuiz.grid_remove()
        self.entry_ID.grid_remove()
        self.button_submit.grid_remove()
        self.ID = self.entry_ID.get().strip()# removes leading and trailing whitespaces
        self.IsAdmin = False
        encoded_message = (str(self.ID)).encode('utf-8')
        self.client_socket.send(encoded_message)
        time.sleep(0.2)

# Main function to run the GUI
def main():
    root = tk.Tk()
    quiz_client = QuizClient(root)
    root.protocol("WM_DELETE_WINDOW", quiz_client.disconnect_from_server)
    root.mainloop()

if __name__ == "__main__":
    main()
