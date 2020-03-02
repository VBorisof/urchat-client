import requests
import json
import datetime
from subprocess import call
import os
import threading
import time
from pynput.keyboard import Key, Listener
import sys

user_input_so_far=""

class ApiService:
    api_base = "your-api-base"
    token = ""

    def get(self, endpoint):
        headers = {'Content-Type': 'application/json'}
        if self.token != "":
            headers['Authorization'] = "Bearer " + self.token
        return requests.get(self.api_base + "/" + endpoint, headers=headers)

    def post(self, endpoint, payload):
        headers = {'Content-Type': 'application/json'}
        if self.token != "":
            headers['Authorization'] = "Bearer " + self.token
        return requests.post(self.api_base + "/" + endpoint,
                             headers=headers,
                             data=json.dumps(payload))

    def register(self, username, password):
        payload = {
            'username': username,
            'password': password
        }
        response = self.post("register", payload)
        if response.status_code == 200:
            print("[+] Registered okay, meow. Login now and join the fun, meow")
        elif response.status_code == 409:
            print("[!] Failed to register you in meow. Another user with that name exists, meow.")
        else:
            print("[!] Failed to register you in meow. No idea why, meow. " + str(response.status_code))

    def login(self, username, password):
        payload = {
            'username': username,
            'password': password
        }
        response = self.post("login", payload)
        if response.status_code == 200:
            self.token = response.text
            print("[+] Meow! Welcome, meow!")
            return True
        elif response.status_code == 470:
            print("[!] Failed to log you in meow. Check ur creds asshole, meow.")
        else:
            print("[!] Failed to log you in meow. No idea why, meow." + str(response.status_code))
        return False

    def get_messages(self):
        response = self.get("message?pageSize=20&page=0")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("[!] You are not logged in, meow.\nPlease login by typing 'login' or typing 'register' to register, meow.")
        else:
            print("[!] Having trouble connecting you, meow.\nNo chat for you :(" + str(response.status_code))

    def send_message(self, message):
        response = self.post("message", {'message': message})
        if response.status_code == 200:
            return
        if response.status_code == 401:
            print("[!] You are not logged in, meow.\nPlease login by typing 'login' or typing 'register' to register, meow.")
        else:
            print("[!] Having trouble connecting you, meow.\nNo chat for you :(" + str(response.status_code))


def clear():
    # check and make call for specific operating system 
    _ = call('clear' if os.name =='posix' else 'cls')

def foo(api):
    while True:
        to_print = ""
        clear()
        messages = api.get_messages()
        if messages != None:
            for message in reversed(messages['page']):
                message_datetime = datetime.datetime.strptime(message['sentDate'], '%Y-%m-%dT%H:%M:%S.%f')
                message_datetime = f'{message_datetime.year}.{message_datetime.month}.{message_datetime.day} {message_datetime.hour}:{message_datetime.minute}:{message_datetime.second}'
                to_print += "["+ message_datetime +"] " + message["sender"] + ": " + message["message"] + "\n"

        global user_input_so_far
        if user_input_so_far != "":
            to_print += "> " + user_input_so_far

        print(to_print, end='')

        time.sleep(0.5)

api = ApiService()

def on_press(key):
    global user_input_so_far
    if key != Key.enter:
        try:
            user_input_so_far += key.char
        except:
            pass
    
def press_monitor():
    with Listener(on_press=on_press) as listener:
        listener.join()

print ("Welcome to UrChat, meow. Commands you need: 'register' and 'login'. Enjoy. Mmmmmrmeow.")

is_running = True
user_input = ""
while is_running:
    user_input_so_far = ""
    user_input = input("> ")

    try:
        if user_input == "quit":
            is_running = False
            continue

        elif user_input == "register":
            username = input("username? > ")
            password = input("password? > ")
            repassword = input("repeat password? > ")

            if password != repassword:
                print("[!] Passwords do not match, meow.")
                continue
            api.register(username, password)

        elif user_input == "login":
            username = input("username? > ")
            password = input("password? > ")

            if api.login(username, password):
                threading.Thread(target=foo, args=(api,)).start()
                threading.Thread(target=press_monitor).start()

        elif user_input == "":
            continue

        else:
            api.send_message(user_input)

    except ValueError:
        print("[!] Please enter a valid option.")
        continue

