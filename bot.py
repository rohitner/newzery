import random
import os, gc
from flask import Flask, request, render_template
from pymessenger.bot import Bot
from generate import generateVideoClip
from threading import Thread, enumerate

app = Flask(__name__)
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
QUICK_REPLIES = ['15', '20']
bot = Bot(ACCESS_TOKEN)


@app.route("/", methods=['GET'])
def landing_page():
    return render_template('landing.html')


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/bot", methods=['GET', 'POST'])
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
                    if message['message'].get('quick_reply'):
                        quick_reply = message['message'].get('quick_reply')
                        url = quick_reply['payload']
                        clip_duration = message['message'].get('text')
                        print('quick_reply')
                        print(clip_duration, url)
                        videoThread = Thread(target=pushVideoClip, args=(recipient_id, url, clip_duration,))
                        videoThread.start()
                    # If url message, send quicky reply to get clip duration
                    elif message['message'].get('text'):
                        url = message['message'].get('text')
                        # print(message)
                        print('text')
                        sendQuickReply(recipient_id, 'Choose a preferred video duration in seconds', url)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        print('attachment')
                        for thread in enumerate():
                            print(thread.name)
                        # TODO: only entertain richlink conversions
                        print(message['message'].get('attachments'))
    gc.collect()
    return "Message Processed"


def pushVideoClip(recipient_id, url, clip_duration):
    print(url, len(enumerate()))
    # prevent concurrent requests
    if(len(enumerate()) > 3):
        send_message(recipient_id, 'Server full: please try again in few minutes')
        gc.collect()
        return
    send_message(recipient_id, 'We are processing your request')
    if(generateVideoClip(url, clip_duration) == 1):
        send_message(recipient_id, 'Here\'s a newzery of the article 🎉')
        send_video(recipient_id, os.getcwd() + '/final.mp4')
    else:
        send_message(recipient_id, 'Your request could not be processed, please ensure you\'ve entered a valid url')
    # garbage collector to avoid heroku error R14
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


def sendQuickReply(recipient_id, text, url):
    bot.send_quick_replies_message(recipient_id, text, QUICK_REPLIES,
                                   list_of_payloads=len(QUICK_REPLIES) * [url])


if __name__ == "__main__":
    app.run()
