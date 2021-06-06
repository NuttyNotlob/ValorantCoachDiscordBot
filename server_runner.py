from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Hi! This is a webserver created to run my Valorant Inspiration bot, which can be added to a discord channel to provide some inspiration before a game of Valorant"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_running():
    t = Thread(target=run)
    t.start()