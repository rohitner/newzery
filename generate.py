from newspaper import Article
import urllib.request
import numpy as np
from sumy.summarizers.lex_rank import LexRankSummarizer
from moviepy.editor import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import random

ARTICLE_URL = "https://www.androidpolice.com/2020/08/17/facebook-starts-integrating-messenger-with-instagram/"
N_TEXT = 3
WIDTH, HEIGHT = 900, 600
INTRO_TIMEOUT = 2
TEXT_TIMEOUT = 4
FADE_TIMEOUT = 1
CODEC = 'libx264'
FPS = 24


def download_web_image(url, i):
    path = os.getcwd() + "/images/" + str(i) + ".jpg"
    urllib.request.urlretrieve(url, path)


def get_music_path(lines):
    dic = [0, 1, 2]
    type = {0: "neg", 1: "neu", 2: "pos"}
    length = len(lines)
    sid = SentimentIntensityAnalyzer()
    mood_coeff = [0, 0, 0]
    for sentence in lines:
        ma = -1
        ss = sid.polarity_scores(sentence)
        for k in ss:
            temp = int(ss[k] * 1000)
            j = 0
            if(k == "neg"):
                j = 0
            elif(k == "neu"):
                j = 1
            elif(k == "pos"):
                j = 2
            mood_coeff[j] += temp
    mizaz = 1  # default neutral mood
    total_max = 0
    for i in range(3):
        mood_coeff[i] /= length
        if(mood_coeff[i] > total_max):
            mizaz = i
    r = random.randint(0, 1)
    music_string = "sound_tracks/" + type[mizaz] + "-" + str(r) + ".mp3"
    return music_string


def getArticleText(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    print(article.title)
    print(article.top_image)
    lines = article.text.split('\n')
    lines = [line for line in lines if line]
    text = []
    for line in lines:
        for oneline in line.split('. '):
            text.append(oneline)
    text = [line for line in text if line]
    for line in text:
        print(line, '\n')
    return text


def generateVideoClip(url, clip_duration):
    if(clip_duration == 20):
        N_TEXT = 4
    else:
        N_TEXT = 3
    generated = 0
    try:
        text = getArticleText(url)

        total_duration = 0
        textClip = []
        for line in text[0:N_TEXT]:
            with TextClip(line, size=(WIDTH, HEIGHT), fontsize=30, font='DejaVu-Sans',
                          color='black', stroke_width=5, align='center', method='caption', kerning=1) \
                    .set_duration(TEXT_TIMEOUT).on_color(color=(255, 255, 255), col_opacity=0.5) \
                    .fadein(FADE_TIMEOUT).fadeout(FADE_TIMEOUT) as clip:
                textClip.append(clip)
            total_duration += TEXT_TIMEOUT
        textClip = concatenate(textClip, method='chain')

        musicClip = AudioFileClip(get_music_path(text))

        # append intro : dont concat image with text, causes pixelation
        introClip = ImageClip('static/newzery.png').resize(width=WIDTH, height=HEIGHT).set_pos(
            ('center', 'center')).set_duration(total_duration + INTRO_TIMEOUT).fadein(FADE_TIMEOUT)

        finalClip = CompositeVideoClip([introClip, textClip.set_start(
            INTRO_TIMEOUT).set_position('center', 'center')]).set_audio(musicClip).set_duration(total_duration + INTRO_TIMEOUT)

        finalClip.write_videofile('final.mp4', fps=FPS, codec=CODEC)

        textClip.close()
        musicClip.close()
        introClip.close()
        finalClip.close()

        generated = 1
    except Exception as e:
        print(e)
    return generated


if __name__ == "__main__":
    generateVideoClip(ARTICLE_URL, 0)
