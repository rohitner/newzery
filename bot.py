import random
import os, gc
from flask import Flask, request
from pymessenger.bot import Bot
from generate import generateVideoClip
from threading import Thread

app = Flask(__name__)
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
bot = Bot(ACCESS_TOKEN)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        # response_sent_text = get_message()
                        url = message['message'].get('text')
                        print('text')
                        print(url)
                        videoThread = Thread(target=pushVideoClip, args=(recipient_id, url,))
                        videoThread.start()
                        # send_message(recipient_id, 'Sorry, your request could not be processed :/')
                        # send_video(recipient_id, '/home/rohitner/newzery/stock.mp4')
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        print('attachment')
                        # TODO: only entertain richlink conversions
                        print(message['message'].get('attachments'))
                        # response_sent_nontext = get_message()
                        # send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def pushVideoClip(recipient_id, url):
    send_message(recipient_id, 'We are processing your request')
    if(generateVideoClip(url) == 1):
        send_video(recipient_id, os.getcwd() + '/final.mp4')
    else:
        send_message(recipient_id, 'Your request could not be processed, please ensure you\'ve entered a valid url')
    gc.collect()


def verify_fb_token(token_sent):
    """ take token sent by facebook and verify it matches the verify token you sent
        if they match, allow the request, else return an error"""
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def get_message():
    """chooses a random message to send to the user"""
    sample_responses = ["You are stunning!", "We're proud of you.",
                        "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)


def send_message(recipient_id, response):
    """sends user the text message provided via `response` parameter"""
    bot.send_text_message(recipient_id, response)
    return "success"


def send_video(recipient_id, video_path):
    """sends user the video file provided via `video_path` parameter"""
    bot.send_video(recipient_id, video_path)


if __name__ == "__main__":
    app.run()
