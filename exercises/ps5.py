"""
Name:
Collaborators:
Time:
"""

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz
import re


# -----------------------------------------------------------------------

# ======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
# ======================


def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
        #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
        #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret


# ======================
# Data structure design
# ======================

# Problem 1

class NewsStory:
    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid
    
    def get_title(self):
        return self.title
    
    def get_description(self):
        return self.description
    
    def get_link(self):
        return self.link
    
    def get_pubdate(self):
        return self.pubdate


# ======================
# Triggers
# ======================


class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError


# PHRASE TRIGGERS

# Problem 2

# puncts: for splitting text when contains punctuation and space. 
# the delimiters are the punctuation characters and space.
puncts = '[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\s+]'

class PhraseTrigger(Trigger):
    """
    Subclass of Trigger.
    PhraseTrigger should not be case-sensitive.
    Input: assumed to be valid string (no punctuation, no extra spaces)
    """
    def __init__(self, phrase):
        self.phrase = phrase.lower()

    def is_phrase_in(self, text):
        """
        Returns True if the phrase is in the input text. False otherwise.
        Notes: 
        * words in phrase must maintain order of appearance in text,
        and must be right next to each other
        * not case-sensitive
        * ignore punctuations
        """
        phrase_arr = self.phrase.split()

        # removes punctuations from text. creates array of just words.
        # for example: 
        # * 'purple@#$%cow' -> ['purple', '', '', '', '', 'cow']
        # * 'Purple!!! Cow!!!' -> ['Purple', '', '', 'Cow', '', '', '']
        
        text_arr = re.split(puncts, text)
        
        # if found_prev, then the very next word in the text 
        # must be the next word in the phrase
        found_prev = False

        for word_phrase in phrase_arr:
            for i in range(len(text_arr)):
                # lowercase the current word in text_arr
                word_text = text_arr[i].lower()

                # if word_text is an empty string (aka a removed punctuation) skip it
                if word_text == '':
                    continue

                if found_prev:
                    if word_phrase == word_text:
                        # mark start of new text array, as words in 
                        # word phrases must maintain order of appearance
                        # in text_arr
                        text_arr = text_arr[i+1:] 
                        break
                    else:
                        # if found the prev word in the phrase but
                        # the current word_phrase and current 
                        # word_text doesn't match, return false
                        # (bad order)
                        return False
                
                # if haven't found any words yet (this only happens once)
                else:
                    if word_phrase == word_text:
                        found_prev = True
                        text_arr = text_arr[i+1:]
                        break
            # immediately return False if cannot find word_phrase in text_arr
            if i == len(text_arr) - 1 and word_text != word_phrase: 
                return False
        
        # return True if found all word phrases in text_arr, with each having 
        # correct order of appearance
        return True

# Problem 3
class TitleTrigger(PhraseTrigger):
    def __init__(self, phrase):
        super().__init__(phrase)
    
    def evaluate(self, story):
        title = story.get_title()
        if super().is_phrase_in(title):
            return True
        else:
            return False

# Problem 4
class DescriptionTrigger(PhraseTrigger):
    def __init__(self, phrase):
        super().__init__(phrase)
    
    def evaluate(self, story):
        description = story.get_description()
        if super().is_phrase_in(description):
            return True
        else:
            return False

# TIME TRIGGERS

# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.



# Problem 6
# TODO: BeforeTrigger and AfterTrigger


# COMPOSITE TRIGGERS

# Problem 7
# TODO: NotTrigger

# Problem 8
# TODO: AndTrigger

# Problem 9
# TODO: OrTrigger


# ======================
# Filtering
# ======================


# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    # This is a placeholder
    # (we're just returning all the stories, with no filtering)
    return stories


# ======================
# User-Specified Triggers
# ======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, "r")
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith("//")):
            lines.append(line)

    # TODO: Problem 11
    # line is the list of lines that you need to parse and for which you need
    # to build triggers

    print(lines)  # for now, print it so you see what it contains!


SLEEPTIME = 120  # seconds -- how often we poll


def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("election")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Clinton")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]

        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line
        # triggerlist = read_trigger_config('triggers.txt')

        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT, fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica", 14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify="center")
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []

        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title() + "\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:
            print("Polling . . .", end=" ")
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")

            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.yahoo.com/rss/topstories"))

            stories = filter_stories(stories, triggerlist)

            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)

            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    # root = Tk()
    # root.title("Some RSS parser")
    # t = threading.Thread(target=main_thread, args=(root,))
    # t.start()
    # root.mainloop()

    cuddly = NewsStory("", "The purple cow is soft and cuddly.", "", "", datetime.now())
    # exclaim = NewsStory("", "Purple!!! Cow!!!", "", "", datetime.now())
    # symbols = NewsStory("", "purple@#$%cow", "", "", datetime.now())
    spaces = NewsStory("", "Did you see a purple     cow?", "", "", datetime.now())
    # caps = NewsStory("", "The farmer owns a really PURPLE cow.", "", "", datetime.now())
    # exact = NewsStory("", "purple cow", "", "", datetime.now())

    # plural = NewsStory("", "Purple cows are cool!", "", "", datetime.now())
    separate = NewsStory("", "The purple blob over there is a cow.", "", "", datetime.now())
    # brown = NewsStory("", "How now brown cow.", "", "", datetime.now())
    # badorder = NewsStory("", "Cow!!! Purple!!!", "", "", datetime.now())
    nospaces = NewsStory("", "purplecowpurplecowpurplecow", "", "", datetime.now())
    nothing = NewsStory("", "I like poison dart frogs.", "", "", datetime.now())

    s1 = TitleTrigger("PURPLE COW")
    s2 = TitleTrigger("purple cow")

    for trig in [s1, s2]:
        print(trig.evaluate(cuddly))
