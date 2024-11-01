import socket
import threading
import json
import random
import time
import ClassQuiz as cq

# Constants
HOST = '127.0.0.1'
PORT = 5005

# Global variables
connected_clients = {}
games_played = {}


# broadcast the message to all the players in the quiz
def broadcast(quiz, message):
    if quiz is None:
        print("Error: Quiz is None. Broadcasting aborted.")
        return

    # Assuming message is a string, encode it to bytes before sending
    message = str(message)
    encoded_message = message.encode()
    print(f'players:{quiz.getPlayers()}')

    users = quiz.getPlayers()
    # if there arent players in the quiz - so there isnt users to send the message to
    if users is None:
        print("Error: Users is None. Broadcasting aborted.")
        return

    for user in connected_clients.keys():
        try:
            if user in users and connected_clients[user]:
                print(f'send to user: {user}')
                # send the encoded message to all the players of the quiz
                connected_clients[user].send(encoded_message)
        # in case of mistake in communication print error
        except Exception as e:
            print(f"Error broadcasting to a client: {e}")


# Function to handle a client connection
def handle_client(client_socket, client_address):
    # default value
    message = 'Okay'
    # gets username from client- if the username exist deny it and else accept it
    username = client_socket.recv(1024).decode('utf-8')
    if connected_clients is None:
        message = 'Okay'

    else:
        flag = 0
        for users in connected_clients:
            if users == username:
                message = 'caught username!'
                flag = 1
    print(f'{message}')
    client_socket.send(message.encode('utf-8'))
    if flag == 0:
        connected_clients[username] = client_socket
        # connected_clients[username] = client_socket
        newOrExist = ""
        while True:
            newOrExist = client_socket.recv(1024).decode('utf-8')
            print(f'newOrExist:{newOrExist}')
            if "new game" in newOrExist or "exist game' in newOrExist":
                break

        if "new game" in newOrExist:
            category = client_socket.recv(1024).decode('utf-8')
            print(f'Client {client_address} connected as {username} in category {category}')
            # client_socket.send(f"Quiz starting!".encode('utf-8'))
            New_id = start_new_quiz(username, category)
            game = games_played[New_id]

        else:
            if "exist game" in newOrExist:

                ID = client_socket.recv(1024).decode('utf-8')
                check = 0
                for id_keys in games_played.keys():
                    if id_keys == int(ID):
                        check = 1
                        game = games_played[int(ID)]
                        game.add_players(username)
                        mes = "There is a game with that ID!"
                        if game.InProgress == True:
                            mes = "The game has already started"
                        connected_clients[username].send(mes.encode('utf-8'))

                        while game.IsOver == False:
                            continue

                        score = connected_clients[username].recv(1024).decode('utf-8')
                        if username in game.getPlayers():
                            game.HandleScore(username, score)
                        time.sleep(2)

                        data = json.dumps(game.get_score())
                        print(f'score: {data}')

                        connected_clients[username].send(data.encode('utf-8'))

                if check == 0:
                    mes = "There isnt a game with that ID! "
                    connected_clients[username].send(mes.encode('utf-8'))

        for user in game.getPlayers():
            del connected_clients[user]
        del games_played[game.getID()]


# Function to start the quiz
def start_new_quiz(username, category):
    client_answer = ''

    quiz = cq.quiz(category, username)
    quiz.start()
    print(f'user name {username}')
    print(f'players:{quiz.getPlayers()}')

    id = quiz.getID()
    print(f'id: {id}')
    # send id of the game to the client

    encoded_message = str(id).encode('utf-8')
    connected_clients[username].send(encoded_message)
    # add the new quiz to global games list

    games_played.update({id: quiz})
    # wait for start questions message from the client to start the game
    while True:
        mes = connected_clients[username].recv(1024).decode('utf-8')
        if "start questions" in mes:
            quiz.InProgress = True
            break

    # category = random.choice(categories)
    # send to all the players that the game starts
    broadcast(quiz, 'Quiz starting! Get ready for the first question...\n')

    # get questions while unused questions are left
    while len(quiz.getQ()) != len(quiz.get_used()):
        question = quiz.getCurrentQ()
        # quiz.get_used().append(question)
        answer = quiz.get_correct_answer()
        option = quiz.get_options()

        current_question = f'Category: {quiz.getCategory()}\nQuestion: {question}'
        correct_answer = f'Correct Answer: {answer}'
        current_options = option

        # Broadcast to all clients that the quiz has started

        time.sleep(2)  # Simulating time before displaying the question
        # send all the needed information to the client
        broadcast(quiz, current_question)
        broadcast(quiz, current_options)
        broadcast(quiz, correct_answer)

        # Simulate the time for answering the question
        time.sleep(10)
        # Broadcast correct answer and start the next question
        time.sleep(2)  # Simulating time before the next question
    # When all the questions are used - game over
    broadcast(quiz, "game over!")
    quiz.GameOver()
    # gets the score of the admin
    score = connected_clients[username].recv(1024).decode('utf-8')
    #print(f'score0: {score} to username: {username}')
    #if username in quiz.getPlayers():
    quiz.HandleScore(username, score)
    #print(f'score1: {quiz.get_score()}')
    time.sleep(2)

    data = json.dumps(quiz.get_score())
    # print(f'score2: {data}')
    # send the score dict to client
    connected_clients[username].send(data.encode('utf-8'))
    return id


# Main server function
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a new socket type TCP
    server_socket.bind((HOST, PORT))  # bind server socket to the port and host
    server_socket.listen()  # the server listen to maximum of default connections

    print(f'Server listening on {HOST}:{PORT}')

    while True:
        client_socket, client_address = server_socket.accept()  # accept an incoming communication
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))  # open a new thread for every client
        client_thread.start()


if __name__ == "__main__":
    main()
