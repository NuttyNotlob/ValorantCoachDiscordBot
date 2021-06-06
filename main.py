# Bot designed to provide some pre-game inspiration for all you Valorant players out there

import os
import discord
import requests
import json
import random
from replit import db
from server_runner import keep_running
from discord.ext import commands

client = discord.Client()

# Need to add intents to let bot see who's in voice channel - won't use command_prefix but
# need it for method to work
intents = discord.Intents().all()
client = commands.Bot(command_prefix="!", intents=intents)

# Word list which can be used to say thanks to the bot after any action, and will result
# in a humble message from the bot
grateful_words = ["thanks", "cheers", "inspirational", "wow", "gracias", "danke"]

humble_messages = [
  "No need to thank me - you make it easy to inspire by watching you play",
  "I meant every word of it",
  "No problem - you just needed a push, now go out and win!",
  "The inspiration was always inside you - I just set it free"
  ]

# A starter set of phrases which will go into the bot's speech production, which can't be 
# removed. these are always available to the bot as a fallback for speech-writing
starter_speech_intro = [
  "The game ahead is all but won, we just have to go out there and play. ",
  "We've got this win in the bag. ",
  "The next game's gonna take some gumption, but I know we've got it in us. ",
  "Nothing can stop us right now. ",
  "The world is our oyster when we play as a team. ",
  "The passion we have for this game is unreal, and I want you all to show that today. ",
  "Ain't no pressure on you - you've got this, no team's gonna stop that from happening. ",
  "It's all on you guys, if you want the win then you'll get it, I promise you that. ",
  "I can't wait to watch this next game you're playing - history in the making. "
]
starter_speech_phrases = [
  "your peeks are on point, take 'em on and they'll be left wondering what happened!",
  "is there anyone that can stop you when you're on a roll?",
  "I think I see an Ace incoming, it's written in the stars.",
  "the enemy team won't know what's coming, I can already picture their salty messages.",
  "we all know you're way under-ranked. Go show them that.",
  "your leadership is gonna give this group that secret ingredient it's been craving.",
  "Tenz for a seven-figure sum? They'll be calling that chump-change when you enter the scene.",
  "you're the glue that holds this team together, now go stick it to them.",
  "it's a shame there's no replay saving, because otherwise future Valorant players would be watching your next game for generations.",
  "even as a bot I think I'm going to struggle to count up to how many kills you're about to get.",
  "I've got Aimlabs on the phone with a sponsor deal after the flicks you've been pulling.",
  "phantom? Vandal? It doesn't matter when we've got you on the team.",
  "get ready to bat away those reports because there's no way you're not on aimbot with the shots you're about to pull off.",
  "I'm no fan of smurfs but it's hard for you not to be one when you're in a rank of your own.",
  "hope you've been working on your back muscles because I can see you carrying.",
  "I've already received the transfer request from Fnatic - sad to see you go but go show 'em why they signed you.",
  "they're gonna have to start calling you the grillhouse with those juicy flanks you're coming out with.",
  "no need for blinds on our team, as you're about to dazzle them with your performance!",
  "did you know you're in the UrbanDictionary? There's a picture of you under the phrase 'coming in clutch'.",
  "you've got some totes mad skills brah.",
  "have you been on the G-fuel? That's the only explanation that computes for your outrageous performances.",
  "it's a-bot time you let the rest of your team get some kills, leave some for the rest of 'em!"
]
starter_speech_outro = [
  "Now go out there and do me proud!",
  "Now get out there and get the w!",
  "If that doesn't inspire you I don't know what will!",
  "The game's out there for the taking, let's go grab it!",
  "You've put in the practise - now go reap the rewards!",
  "Now go show 'em how it's done!",
  "Let's see what they've got!"
]

# Add responsive variable to database, which is used to set whether bot responds to 
# grateful_words
if "responsive" not in db.keys():
  db["responsive"] = True

# Method to get an inspirational quote from ZenQuotes API
def get_inspiring_quote():
  # Request the quote in JSON form
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)

  # Extract the quote and associated author form the JSON and return the string
  quote = json_data[0]['q'] + " - " + json_data[0]['a']
  return(quote)

# Method to produce an inspirational speech aimed at anyone in the given channel
def create_speech(server, channel_name):
  # Get a random intro and outro for the list
  intro = random.choice(starter_speech_intro)
  outro = random.choice(starter_speech_outro)

  # Now to create a speech for the players, but first we need to get the names of all the members in our channel
  voice_channel = discord.utils.get(server.voice_channels, name=channel_name)

  # Get the members in the voice channel, and then extract their names into an array
  members = voice_channel.members
  mem_names = []
  for member in members:
    mem_names.append(member.name)

  # Now to make the part of the speech using the players' names. Make a copy of the array and 
  # remove our random choice so as to not get a speech phrase twice
  player_speech = ""
  speech_phrases = starter_speech_phrases.copy()
  for name in mem_names:
    speech_choice = random.choice(speech_phrases)
    player_speech += (name + " - " + speech_choice + " ")
    speech_phrases.remove(speech_choice)

  #And now return the final speech
  return (intro + player_speech + outro)

# Method to add a quote to the database
def update_val_quotes(quote):
  # If we already have some quotes in the database
  if "quotes" in db.keys():
    quotes = db["quotes"]
    quotes.append(quote)
    db["quotes"] = quotes
  # If there's no quotes in the database
  else:
    db["quotes"] = [quote]

# Method to delete a quote from the database
def delete_val_quote(index):
  quotes = db["quotes"]
  if len(quotes) > index:
    del quotes[index]
    db["quotes"] = quotes

# On successful login, we print to the console that bot has managed to log in
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

# Following bot functionality is all based on when a message is received
@client.event
async def on_message(message):
  # If the message is from the bot, we ignore it
  if message.author == client.user:
    return

  # Bot function to provide a list of all available commands
  if message.content.startswith('$list'):
    commands_list = "- $inspire for a random inspirational quote\n- $list for a list of all available bot commands\n- $quoteadd (quote), $quotedel (quote number) or $quotelist to add to, delete from or see all the Valorant quotes I have stored\n- $quoterandom to get a random quote from our group\n- $responding (true/false) to turn on or off responses to grateful messages\n- $speech (voice channel name) to provide a rousing speech for all players in that voice channel"
    await message.channel.send(commands_list)
  
  # Bot function to provide an inspirational quote from ZenQuotes API
  if message.content.startswith('$inspire'):
    await message.channel.send(get_inspiring_quote())

  # Bot function to provide an inspiring, player-specific speech
  if message.content.startswith('$speech'):
    channel_name = message.content.split("$speech ",1)[1]
    await message.channel.send(create_speech(message.guild, channel_name))

  # Bot function to respond with a humble message to any grateful messages
  if db["responsive"] and any(word in message.content for word in grateful_words):
    await message.channel.send(random.choice(humble_messages))

  # Bot function to turn on/off responding to grateful messages
  if message.content.startswith('$responding'):
    value = message.content.split("$responding ",1)[1]
    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on")
    elif value.lower() == "false":
      db["responding"] = False
      await message.channel.send("Responding is off")

  # Bot function to add a local quote
  if message.content.startswith('$quoteadd'):
    new_quote = message.content.split("$quoteadd ",1)[1]
    update_val_quotes(new_quote)
    await message.channel.send("New quote added.")

  # Bot function to delete a quote
  if message.content.startswith('$quotedel'):
    if "quotes" in db.keys():
      index = int(message.content.split("$quotedel ",1)[1]) - 1
      deleted_quote = db["quotes"][index]
      delete_val_quote(index)
    await message.channel.send("Quote of '" + deleted_quote + "' has been deleted.")

  # Bot function to list all quotes
  if message.content.startswith('$quotelist'):
    quotes = []
    if "quotes" in db.keys() and len(db["quotes"]) != 0:
      quotes = list(db["quotes"])
      quotes_list = ""
      for index, quote in enumerate(quotes):
        quotes_list += str(index + 1) + ": " + quote + "\n"
      await message.channel.send(quotes_list)
    else:
      await message.channel.send("No quotes to list!")

  # Bot function to give a random quote from the database
  if message.content.startswith('$quoterandom'):
    if "quotes" in db.keys() and len(db["quotes"]) != 0:
      await message.channel.send(random.choice(db["quotes"]))


# Now set up the server and start it with discord
keep_running()

client.run(os.environ['TOKEN'])