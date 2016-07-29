# Name:             High-Level Emma Module
# Description:      Controls high-level functions and decision making
# Section:  
import time
import random
import os
import pickle
import cgi

import pattern.en
import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import tumblrclient
import parse
import questionparser
import pronouns
import associationtrainer
import sentencebuilder
import utilities
import settings

settings.load_settings()

class stack(list):
    def push(self, item):
        self.insert(0, item)
        self.remove(self[10])

connection = sql.connect('emma.db')
cursor = connection.cursor()

print "Checking for concept database...",
with connection:
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'associationmodel\';")
    if cursor.fetchone() == (u'associationmodel',): print Fore.GREEN + "[Done]"
    else:
        print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating new database...",
        cursor.executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        DROP TABLE IF EXISTS friends;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, is_new INTEGER DEFAULT 1, is_banned INTEGER DEFAULT 0);
        CREATE TABLE friends(username TEXT, can_reblog_from INTEGER DEFAULT 0);
        """)
        print Fore.GREEN + "[Done]"

print "Checking for mood file...",
if os.path.isfile('moodHistory.p'):
    print Fore.GREEN + "[Done]"
    with open('moodHistory.p','r') as moodFile: moodHistory = stack(pickle.load(moodFile))
else:   
    print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating file with randomized moods...",
    moodHistory = []
    with open('moodHistory.p','wb') as moodFile:
        for i in range(0, 10): moodHistory.append(random.uniform(-0.5, 0.5))
        moodHistory = stack(moodHistory)
        pickle.dump(moodHistory, moodFile)
    print Fore.GREEN + "[Done]"

# "Emma" banner
print Fore.MAGENTA + u"\n .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' \u006088b \u0060888P\"Y88bP\"Y88b  \u0060888P\"Y88bP\"Y88b  \u0060P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n\u0060Y8bod8P' o888o o888o o888o o888o o888o o888o \u0060Y888\"\"8o\n\n        EXPANDING MODEL of MAPPED ASSOCIATIONS\n                     Alpha v0.0.3\n"

with connection:
    cursor.execute("SELECT * FROM associationmodel")
    associationModelItems = "{:,d}".format(len(cursor.fetchall()))
    cursor.execute("SELECT * FROM dictionary")
    dictionaryItems = "{:,d}".format(len(cursor.fetchall()))
print Fore.MAGENTA + "Database contains %s associations and %s words." % (associationModelItems, dictionaryItems)

def get_mood(update=False, text="", expressAsText=True):
    global moodHistory
    # If update is set to true, use text to add new mood value. Otherwise, just return the mood without touching it
    # By default, this function does nothing and just returns Emma's mood in human-readable form (as opposed to numbers)
    if update == True: 
        sentiment = pattern.en.sentiment(text)       # Get the average mood from the moods of sentences in the text
        moodHistory.push(sum(sentiment) / float(len(sentiment)))        # Add the mood to the list of mood values
        with open('moodHistory.p','wb') as moodFile: pickle.dump(moodHistory, moodFile)       # Save to mood values file
    else: 
        with open('moodHistory.p', 'r') as moodFile: moodHistory = stack(pickle.load(moodFile))

    # More recent mood values have a higher weight when calculating Emma's overall mood
    weightedmoodHistory = []
    for i in range(0, 3): weightedmoodHistory.append(moodHistory[0])
    for i in range(0, 2): weightedmoodHistory.append(moodHistory[1])
    weightedmoodHistory.append(moodHistory[2])
    weightedmoodHistory = weightedmoodHistory + moodHistory
    mood = sum(weightedmoodHistory) / float(len(weightedmoodHistory))
    if settings.option('general', 'verboseLogging'): print Fore.MAGENTA + "Mood values: %s\nCalculated mood: %s" % (str(moodHistory), str(mood))

    if not expressAsText: return mood
    else:
        if -0.8 > mood: moodStr = u"abysmal \ud83d\ude31"
        elif -0.6 > mood >= -0.8: moodStr = u"dreadful \ud83d\ude16"
        elif -0.4 > mood >= -0.6: moodStr = u"bad \ud83d\ude23"
        elif -0.2 > mood >= -0.4: moodStr = u"crummy \ud83d\ude41"
        elif 0.0 > mood >= -0.2: moodStr = u"blah \ud83d\ude15"
        elif 0.2 > mood >= 0.0: moodStr = u"alright \ud83d\ude10"
        elif 0.4 > mood >= 0.2: moodStr = u"good \ud83d\ude42"
        elif 0.6 > mood >= 0.4: moodStr = u"great \ud83d\ude09"
        elif 0.8 > mood >= 0.6: moodStr = u"fantastic \ud83d\ude00"
        elif 1.0 > mood >= 0.8: moodStr = u"glorious \ud83d\ude1c"
        return u"feeling " + moodStr
    
def consume(parsedMessage, asker=u""):
    intents = []
    questionPackages = []
    for count, parsedSentence in enumerate(parsedMessage):
        print "Consuming sentence %d of %d..." % (count + 1, len(parsedMessage))

        pronouns.determine_references(parsedSentence)
        pronouns.flip_posessive_references(parsedSentence, asker)
        intent = parse.determine_intent(parsedSentence)
        if intent['interrogative'] == True:
            questionPackage = questionparser.read_question(parsedSentence)
            if questionPackage != None:
                questionPackages.append(questionparser.read_question(parsedSentence))
                print questionPackages
        else:
            parse.add_new_words(parsedSentence)
            associationtrainer.find_associations(parsedSentence)
        intents.append(intent)
        print "Sentence consumed."
    return intents, questionPackages

def reply_to_asks(askList):
    if len(askList) > 0:
        print "Fetched %d new asks." % len(askList)
        for askCount, ask in enumerate(askList):
            settings.load_settings()
            print "Reading ask no. %d of %d..." % (askCount + 1, len(askList))
            print Fore.BLUE + u"@" + ask['asker'] + u" >> " + ask['message']

            parsedAsk = parse.tokenize(ask['message'])
            intents, questionPackages = consume(parsedAsk, ask['asker'])
            understanding = utilities.pretty_print_understanding(parsedAsk, intents)

            reply = sentencebuilder.generate_sentence(parsedAsk, get_mood(update=True, text=ask['message'], expressAsText=False), intents, ask['asker'], questionPackages)

            if "%" not in reply:
                print Fore.BLUE + u"emma >> %s" % reply

                print "Posting reply..."
                print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + "@" + ask['asker'] + " >> " + ask['message'] + "\n\n" + "emma >> " + reply + "\n- - - - - - - - - - -\n" + get_mood(update=False, expressAsText=True) + "\n\n"
                body = "<a href=" + ask['asker'] + ".tumblr.com/>@" + ask['asker'] + "</a>" + cgi.escape(" >> ") + cgi.escape(ask['message']) + "\n\n" + cgi.escape("emma >> ") + cgi.escape(reply) + "\n<!-- more -->\n" + cgi.escape(understanding)
                tumblrclient.post(body.encode('utf-8'), ["dialogue", ask['asker'].encode('utf-8'), get_mood().encode('utf-8')])
            else:
                print Fore.YELLOW + "Reply generation failed."

            tumblrclient.delete_ask(ask['id'])

            if settings.option('general', 'enableSleep'):
                print "Sleeping for 3 minutes..."
                time.sleep(180)
            else:
                print Fore.YELLOW + "!!! Sleep disabled in settings -- execution will continue normally in 2 seconds..."
                time.sleep(2)

def reblog_post():
    settings.load_settings()
    with connection:
        cursor.execute("SELECT username FROM friends;")
        SQLReturn = cursor.fetchall()
    posts = tumblrclient.get_recent_posts(random.choice(SQLReturn)[0])

    if len(posts) > 0:
        print "Found %d rebloggable posts." % len(posts)
        while posts:
            post = random.choice(posts)
            posts.remove(post)

            mood = get_mood(update=True, text=post['body'])
            comment = sentencebuilder.generate_sentence(pattern.en.parse(post['body'], True, True, True, True, True).split(), mood)
            
            if "%" not in comment:
                print Fore.BLUE + u"Emma >> " + comment
                tumblrclient.reblog(post['id'], post['reblogKey'], comment.encode('utf-8'), ["reblog", post['blogName'].encode('utf-8'), mood.encode('utf-8')])
                break
            else: print Fore.YELLOW + "Reply generation failed."
    else: print Fore.YELLOW + "No rebloggable posts found."

def dream():
    settings.load_settings()
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_banned = 0 ORDER BY RANDOM() LIMIT 10;')
        SQLReturn = cursor.fetchall()
    dreamSeed = ' '.join(sentencebuilder.make_halo([random.choice(SQLReturn)[0]]))
    print "Dream seed: " + dreamSeed
    dream = sentencebuilder.generate_sentence(pattern.en.parse(dreamSeed, True, True, True, True, True).split(), get_mood(expressAsText=False))
    if "%" not in dream:
        print Fore.BLUE + u"emma >> " + dream
        tumblrclient.post(cgi.escape(dream.encode('utf-8')), ["dreams", get_mood(update=True, text=dream).encode('utf-8')])
    else: print Fore.YELLOW + "Dreamless sleep..."

def chat():
    print Fore.YELLOW + "!!! Chat mode enabled in settings. Press Control-C to exit."
    while settings.option('general', 'enableChatMode'):
        settings.load_settings()
        input = raw_input(Fore.BLUE + 'You >> ').decode('utf-8')
        tokenizedMessage = parse.tokenize(input)
        intents, questionPackages = consume(tokenizedMessage)
        # todo: do things with questionPackage in chat()
        
        reply = sentencebuilder.generate_sentence(tokenizedMessage, get_mood(update=True, text=input, expressAsText=False), intents)
        if "%" not in reply: print Fore.BLUE + u"emma >> " + reply
        else: print Fore.RED + u"Reply generation failed."

while True:
    settings.load_settings()
    # If we aren't in chat mode, every 15 minutes, try to make a post. Replying to asks is most likely, followed by dreams, and reblogging a post is the least likely
    if settings.option('general', 'enableChatMode'): chat()
    else:
        if settings.option('tumblr', 'fetchRealAsks'): askList = tumblrclient.get_asks()
        else: 
            print Fore.YELLOW + "!!! Real ask fetching disabled in settings. Using fake asks instead."
            askList = utilities.fakeAsks

        print "Choosing activity..."
        activities = []
        if settings.option('tumblr', 'enableReblogs'): activities.append('reblogPost')
        if settings.option('tumblr', 'enableDreams'): activities.extend(['dream'] * 2)
        if settings.option('tumblr', 'enableAskReplies') and askList != []: activities.extend(['replyToAsks'] * 3)

        activity = random.choice(activities)
        if activity == 'reblogPost':
            print "Reblogging a post..."
            reblog_post()
        elif activity == 'dream':
            print "Dreaming..."
            dream()
        elif activity == 'replyToAsks':
            print "Replying to asks in queue..."
            reply_to_asks(askList)
        
        if settings.option('general', 'enableSleep'):
            print "Sleeping for 15 minutes..."
            time.sleep(900)
        else:
            print Fore.YELLOW + "!!! Sleep disabled in settings -- execution will continue normally in 2 seconds..."
            time.sleep(2)