# Name:             Input Parser
# Description:      Tokenizes input and adds new words and their information into brain.db/dictionary
# Section:          LEARNING
import re

import pattern.en
import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import utilities
from config import console, files

connection = sql.connect(files['dbPath'])
cursor = connection.cursor()

bannedWords = []
with connection:
    cursor.execute('SELECT word FROM dictionary WHERE is_banned = 1')
    for word in cursor.fetchall(): bannedWords.append(word[0])

def tokenize(text):
    if text[-1] not in [u"!", u"?", "."]: text += u"."
    text = translate_leetspeek(text)

    print "Tokenizing message..."
    if console['verboseLogging']: pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))
    taggedText = pattern.en.parse(text, True, True, True, True, True).split()
    
    parsedMessage = []
    for count, taggedSentence in enumerate(taggedText):
        if console['verboseLogging']: print "Packaging sentence no. %d..." % (count + 1)

        finalize_sentence(taggedSentence)

        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        subObj =[]
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
            subObj.append(taggedWord[4])
        parsedSentence = zip(lemmaSentence, posSentence, chunkSeries, subObj)
        for count, word in enumerate(parsedSentence):
            parsedSentence[count] = list(word)
        parsedMessage.append(parsedSentence)
    return parsedMessage

def translate_leetspeek(text):
    text = text.split(' ')
    for count, word in enumerate(text):
        if word in [u"im", u"Im"]:
            print Fore.GREEN + "Replacing \"im\" with \"I\'m\"..."
            text[count] = u"I'm"
        elif word == u"u":
            print Fore.GREEN + "Replacing \"u\" with \"you\"..."
            text[count] = u"you"
        elif word == u"r":
            print Fore.GREEN + "Replacing \"r\" with \"are\"..."
            text[count] = u"are"
        elif word == u"ur":
            print Fore.GREEN + "Replacing \"ur\" with \"your\"..."
            text[count] = u"your"
    return ' '.join(text)

def finalize_sentence(taggedSentence):
    rowsToRemove = []
    for count, taggedWord in enumerate(taggedSentence):
        if console['verboseLogging']: print "Checking for conjunctions and illegal characters..."
        if count != 0: prevWord = taggedSentence[count - 1]
        if count != len(taggedSentence) - 1: nextWord = taggedSentence[count + 1]
        
        # todo: this splits up the word "can't" incorrectly. Fix
        if taggedWord[5] in [u"n\'t", u"n\u2019t", u"n\u2018t"]:
            print Fore.GREEN + "Replacing \"n\'t\" with \"not\"..."
            taggedWord[5] = u"not"
        elif taggedWord[5] in [u"\'", u"\u2019", u"\u2018"] and prevWord and nextWord:
            print Fore.GREEN + "Joining \"%s\" and \"%s\"..." % (prevWord[5], nextWord[0])
            prevWord[5] = prevWord[5] + "\'" + nextWord[0]
            rowsToRemove.append(taggedWord)
            rowsToRemove.append(nextWord)
        elif taggedWord[5] in [u"\'s'", u"\u2019s", u"\u2018s"] or taggedWord[1] == "POS" and prevWord:
            print Fore.GREEN + "Appending \"\'s\" to \"%s\"..." % prevWord[5]
            prevWord[5] = prevWord[5] + u"\'s"
            rowsToRemove.append(taggedWord)
        elif taggedWord[1] == u"\"" or taggedWord[5] in [u",", u"\u007c", u"\u2015", u"#", u"[", u"]", u"(", u")", u"{", u"}" u"\u2026", u"<", u">"]:
            rowsToRemove.append(taggedWord)
        elif taggedWord[5] in pattern.en.wordlist.PROFANITY or taggedWord[5] in bannedWords:
            rowsToRemove.append(taggedWord)

    if rowsToRemove:
        print Fore.GREEN + "Tidying up..."
        for row in rowsToRemove:
            if row in taggedSentence: taggedSentence.remove(row)

    return taggedSentence

def add_new_words(parsedSentence):
    with connection:
        cursor.execute('SELECT * FROM dictionary;')
        SQLReturn = cursor.fetchall()

    storedLemata = []
    for row in SQLReturn:
        lemma = row[0]
        storedLemata.append(lemma)

    addedWords = []
    for count, item in enumerate(parsedSentence):
        lemma = item[0]
        pos = item[1]

        wordsLeft = parsedSentence[-(len(parsedSentence) - count):len(parsedSentence) - 1]

        if lemma not in storedLemata and lemma not in wordsLeft and lemma not in addedWords and lemma not in pattern.en.wordlist.PROFANITY and lemma.isnumeric() == False and pos != "FW":
            print Fore.MAGENTA + u"Learned new word: \'%s\'!" % lemma
            addedWords.append(lemma)
            with connection:
                cursor.execute("INSERT INTO dictionary VALUES (\"%s\", \"%s\", 1, 0);" % (re.escape(lemma), pos))

greetingTerms = [[u'what\'s', u'up'], [u'hi'], [u'hiya'], [u'hello'], [u'what', u'up'], [u'wassup'], [u'what', u'is', u'up'], [u'what\'s', u'going', u'on'], [u'how', u'are', u'you'], [u'howdy'], [u'hey'], [u'good', u'morning'], [u'good', u'evening'], [u'good', u'afternoon']]
def determine_intent(parsedSentence):
    intent = {'declarative': False, 'interrogative': False, 'greeting', False}      # todo: 'imperative'
    message = []
    for word in parsedSentence: message.append(word[0])

    for greeting in greetingTerms:
        match = re.match(' '.join(greeting), ' '.join(message[0:3]))
        if match: intent['greeting'] = True

    if parsedSentence[0][1] in ("WDT", "WP", "WP$", "WRB") or parsedSentence[1][1] in (u'be') or parsedSentence[-1][0] == "?": intent['interrogative'] = True
    else: intent['declarative'] = True

    return intent

# todo: write a function that can take a given sentence and its intent and break it down into its domains (if possible) for easier parsing