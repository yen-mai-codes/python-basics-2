"""
Name: Yen
Collaborators: None
Time: ~3 hours
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
    found = False
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
        try:
            description = translate_html(entry.description)
        except AttributeError:
            description = ""
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
        #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
        #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%Y-%m-%dT%H:%M:%SZ")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))

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

class TimeTrigger(Trigger):
    def __init__(self, time) -> None:
        # convert time string to datetime object with EST timezone
        self.time = datetime.strptime(time, "%d %b %Y %H:%M:%S")
        self.time = self.time.replace(tzinfo=pytz.timezone("EST"))

# Problem 6

class BeforeTrigger(TimeTrigger):
    def __init__(self, time):
        super().__init__(time)
    
    def evaluate(self, story):
        # gets the story's time
        story_time = story.get_pubdate()

        # if the story's time doesnt have timezone info, assume EST
        if not story_time.tzinfo:
            story_time = story_time.replace(tzinfo=pytz.timezone("EST"))

        # if story time is strictly less than the current time
        # return True. Else return False
        if story_time < self.time:
            return True
        else:
            return False
        
class AfterTrigger(TimeTrigger):
    def __init__(self, time):
        super().__init__(time)
    
    def evaluate(self, story):
        # gets the story's time
        story_time = story.get_pubdate()

        # if the story's time doesnt have timezone info, assume EST
        if not story_time.tzinfo:
            story_time = story_time.replace(tzinfo=pytz.timezone("EST"))
        
        # if story time is strictly greater than the current time
        # return True. Else return False
        if story_time > self.time:
            return True
        else:
            return False


# COMPOSITE TRIGGERS

# Problem 7
class NotTrigger(Trigger):
    def __init__(self, trig):
        self.trig = trig
    
    def evaluate(self, story):
        return not self.trig.evaluate(story)

# Problem 8
class AndTrigger(Trigger):
    def __init__(self, trig1, trig2):
        self.trig1 = trig1
        self.trig2 = trig2
    
    def evaluate(self, story):
        return self.trig1.evaluate(story) and self.trig2.evaluate(story)

# Problem 9
class OrTrigger(Trigger):
    def __init__(self, trig1, trig2):
        self.trig1 = trig1
        self.trig2 = trig2
    
    def evaluate(self, story):
        return self.trig1.evaluate(story) or self.trig2.evaluate(story)

# ======================
# Filtering
# ======================


# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    filtered_stories = []

    # loop through each story, then for each story, loop through list of triggers
    # if there's any trigger that satisfies current story, add story to filtered stories
    # break loop when there's a satisfactory trigger
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story):
                filtered_stories.append(story)

                break
    return filtered_stories


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

    triggers_dict = {}
    final_triggers = []

    for line in lines:
        # split line into elements
        line = line.split(',')

        # trigger definition: Lines that do not begin with the keyword ADD define named triggers.
        if line[0] != 'ADD':
            # if there are just 2 args, then it's a named trigger with the other argument as a negated trigger
            if len(line) == 2:
                trig_name = line[0]
                negated_other_trig = line[1].split()
                trig_type = negated_other_trig[0]
                other_trig_name = negated_other_trig[1]
                
                if trig_type == 'NOT':
                    # makes sure the other trig has been declared
                    try: 
                        other_trig = triggers_dict[other_trig_name]
                        triggers_dict[trig_name] = NotTrigger(other_trig)
                    except KeyError:
                        raise KeyError(other_trig_name, 'has not been declared as a trigger yet!')
                    
            # if there are 3 arguments, then it's to name a simple trigger
            # simple trigs:
            # - title
            # - description
            # - after 
            # - before
            if len(line) == 3:
                trig_name = line[0]
                trig_type = line[1]
                trig_arg = line[2]
                if trig_type == 'TITLE':
                    triggers_dict[trig_name] = TitleTrigger(trig_arg)
                elif trig_type == 'DESCRIPTION':
                    triggers_dict[trig_name] = DescriptionTrigger(trig_arg)
                elif trig_type == 'BEFORE':
                    triggers_dict[trig_name] = BeforeTrigger(trig_arg)
                elif trig_type == 'AFTER':
                    triggers_dict[trig_name] = AfterTrigger(trig_arg)

            # if there are 4 arguments, then it's a composite trigger
            # composite trigs:
            # - AND
            # - OR
            # note: a composite trig can consist of negated (NOT) triggers!
            elif len(line) == 4:
                trig_name = line[0]
                trig_type = line[1]
                arg1 = line[2].split()
                arg2 = line[3].split()

                arg1_negated = False
                arg2_negated = False
                arg1_len = len(arg1)
                arg2_len = len(arg2)
                
                # check if arg1 is a negated trig
                if arg1_len == 1:
                    arg1 = arg1[0]
                elif arg1_len == 2 and arg1[0] == 'NOT':
                    arg1_negated = True
                    arg1 = arg1[1]

                if arg2_len == 1:
                    arg2 = arg2[0]

                elif arg2_len == 2 and arg2[0] == 'NOT':
                    arg2_negated = True
                    arg2 = arg2[1]

                # make sure that both args have been declared
                try:
                    arg1 = triggers_dict[arg1]
                except:
                    raise KeyError(arg1, 'has not been declared as a trigger yet!')
                try: 
                    arg2 = triggers_dict[arg2]
                except:
                    raise KeyError(arg2, 'has not been declared as a trigger yet!')
                
                # if any of the triggers are negated, declare negation using NotTrigger
                if arg1_negated:
                    arg1 = NotTrigger(arg1)
                if arg2_negated:
                    arg2 = NotTrigger(arg2)
                
                # check either type is AND or OR
                if trig_type == 'AND':
                    triggers_dict[trig_name] = AndTrigger(arg1, arg2)

                elif trig_type == 'OR':
                    triggers_dict[trig_name] = OrTrigger(arg1, arg2)
        
        # add triggers
        # note: can consist of negated (NOT) triggers!
        else:

            #go thru the list of triggers to add
            for i in range (1, len(line)):
                trig = line[i].split()
                trig_len = len(trig)
                trig_negated = False

                # check if trig is a negated trig
                if trig_len == 1:
                    trig = trig[0]
                elif trig_len == 2 and trig[0] == 'NOT':
                    trig_negated = True
                    trig = trig[1]

                # check if trig has been declared
                try:
                    trig = triggers_dict[trig]
                    # if trig is negated, declare its negation using NotTrigger
                    if trig_negated:
                        trig = NotTrigger(trig)
                    # add trigger to final triggers list
                    final_triggers.append(trig)

                except:
                    raise KeyError(trig_name, 'has not been declared as a trigger!')

    return final_triggers
SLEEPTIME = 120  # seconds -- how often we poll


def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    # try:
    t0 = TitleTrigger('NASA')
    t00 = TitleTrigger("Trump")
    t1 = OrTrigger(t0, t00)
    t2 = DescriptionTrigger("Trump")
    t3 = DescriptionTrigger("Clinton")
    t4 = AndTrigger(t2, t3)
    triggerlist = [t1, t4]

    # Problem 11
    # TODO: After implementing read_trigger_config, uncomment this line
    triggerlist = read_trigger_config('triggers.txt')

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
        # stories.extend(process("http://news.yahoo.com/rss/topstories"))

        stories = filter_stories(stories, triggerlist)

        list(map(get_cont, stories))
        scrollbar.config(command=cont.yview)

        print("Sleeping...")
        time.sleep(SLEEPTIME)

    # except Exception as e:
        # print(e)


if __name__ == "__main__":
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()