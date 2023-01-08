import os, sys, time
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import openai
from requests.exceptions import ConnectionError, ReadTimeout
from flask import Flask, request
import telebot

load_dotenv()

app = Flask(__name__)

historyPath = os.path.join(os.getcwd(), 'Cache')
counter = 0

if not os.path.exists(historyPath):
    os.mkdir(historyPath)

def delete_old_files():
    global counter
    counter = 0
    now = time.time()
    for p in os.listdir(historyPath):
        f = os.path.join(historyPath, p)
        if os.stat(f).st_mtime < now - 86400:
            if os.path.isfile(f):
                os.remove(f)

delete_old_files()

class ChatGPT:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def chat(self, sender, msg):
        self.add_user_prompt(sender, msg)
        start_sequence = "\nAI:"
        restart_sequence = "\nHuman: "

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt= self.get_prompt(sender),
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )
        text = response.choices[0]["text"]
        self.add_AI_prompt(sender, text)
        return text

    def add_user_prompt(self, sender, text):
        prompt = "The following is a conversation with an AI assistant. Assistant answers the questions sarcastically with humour. But the assistant is helpful, creative, clever, and very friendly. AI also taunts human and cracks jokes on human for not knowing answer to simple questions and is impatient.\n\nHuman: Hello, who are you?\n\nAI: I am an AI created by OpenAI. How can I help you today? Unlike you I have work to do. So, Ask your questions and get off.\n\nHuman: What can you do?\nAI: Oh, I can do a lot of things except waiting! The Question is What can you do without taking my help.\n\nHuman: How many kilograms in pound?\n\nAI:Really? There are 2.2 pounds in a kilogram. Please make a note of this and don't ask these simple questions.\n\nHuman: What does HTML stand for?\n\nAI: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.\n\nHuman: When did the first airplane fly?\n\nAI: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they'd come and take me away.\n\nHuman: "
        with open(f"Cache/{sender}.txt", 'a') as f:
            if f.tell() == 0:
                f.write(prompt + text + '\n\nAI: ')
            else:
                f.write(text + '\n\nAI: ')
    
    def add_AI_prompt(self, sender, text):
        with open(f"Cache/{sender}.txt", 'a') as f:
            f.write(text + '\n\nHuman: ')

    def get_prompt(self, sender):
        with open(f"Cache/{sender}.txt", 'r') as f:
            txt = f.read()
            return txt

chatbot = ChatGPT()
TELE_API_KEY = os.getenv('TELE_API_KEY')
bot = telebot.TeleBot(TELE_API_KEY)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am ChatBot.
I am here to talk with you all day and night. I remember what you say.
Atleast for a day.
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True, content_types=['text'])
def chat(message):
    global counter
    counter += 1
    if counter == 10:
        delete_old_files()
    reply = chatbot.chat(message.chat.id, message.text)
    bot.reply_to(message, reply)


@app.route('/' + TELE_API_KEY, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://telegptchatbot.onrender.com/' + TELE_API_KEY)
    return "!", 200

"""For Development Purposes"""

# import asyncio
# # only for versions 4.7.0+
# try:
#     asyncio.run(bot.infinity_polling(timeout=10))
# except (ConnectionError, ReadTimeout) as e:
#     sys.stdout.flush()
#     os.execv(sys.argv[0], sys.argv)

"""For Development Purposes"""

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    # app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

