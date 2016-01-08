#!/usr/bin/env python2.7

#IRC and yaml reading bot

import irc.client
import sys
import logging
import re
import yaml
import os
import time
import traceback
from Queue import Queue

#Setting the global logger to debug gets all sorts of irc debugging
logging.getLogger().setLevel(logging.WARNING)

def debug(msg):
    try:
        print msg
    except UnicodeEncodeError:
        pass
    
settingsFile = open("settings.yaml")
settings = yaml.load(settingsFile)
settingsFile.close()

IrcServer = settings.get('IrcServer', 'irc.freenode.net')
IrcNick = settings.get('IrcNick', 'TheAxeBot')
IrcPassword = settings.get('IrcPassword', None)
IrcChannel = settings.get('IrcChannel', '#tasbot')

#Number of lines to keep and submit
MaxChatLines = 7

class BrainAgeIrcBot(irc.client.SimpleIRCClient):
    def __init__(self, submissionManager):
        irc.client.SimpleIRCClient.__init__(self)
        
        self.submissionManager = submissionManager
        self.submissionQueue = submissionManager.submissionQueue
        self.lineCache = []
        
        self.badWords = self.getBadWords('bad-words.txt')
        #Precompiled tokenizing regex
        self.splitter = re.compile(r'[^\w]+')
        self.urlregex = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.otherbadregex = re.compile(r'\.((com)|(org)|(net))')
        self.nonPrintingChars = set([chr(i) for i in xrange(32)])
        self.nonPrintingChars.add(127)

    def sendMessage(self, msg):
        """Write to the channel for testing"""
        if msg.isspace():
            return
        self.connection.privmsg(IrcChannel, msg)

    def on_welcome(self, connection, event):
        print 'joining', IrcChannel
        connection.join(IrcChannel)

    def on_join(self, connection, event):
        """Fires on joining the channel.
           This is when the action starts.
        """
        if (event.source.find(IrcNick) != -1):
            print "I joined!"

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def naughtyMessage(self, sender, reason):
        #Be sure to get rid of the naughty message before the event!
        #An easy way is to just make this function a pass
        pass
        # self.connection.privmsg(IrcChannel, "Naughty %s (%s)" % (sender, reason))
        #print("Naughty %s (%s)" % (sender, reason))

    def on_pubmsg(self, connection, event):
        """Handle a message in chat"""
        #debug("pubmsg from %s: %s" % (event.source, event.arguments[0]))
        text = event.arguments[0]
        sender = event.source.split('!')[0]
        text = sender + ":" + text

        #Check for non-ascii characters
        try:
            text.decode('ascii')
        except (UnicodeDecodeError, UnicodeEncodeError):
            self.naughtyMessage(sender, "not ascii")
            return
        except Exception:
            #I am not sure what else can happen but just to be safe, reject on other errors
            return

        if self.urlregex.search(text):
            self.naughtyMessage(sender, "url")
            return

        if self.otherbadregex.search(text):
            self.naughtyMessage(sender, "url-like")
            return

        #We probably also want to filter some typically non-printing ascii chars:
        #[18:12] <@Ilari> Also, one might want to drop character codes 0-31 and 127. And then map the icons to some of those.
        if any(c in self.nonPrintingChars for c in text):
            self.naughtyMessage(sender, "non-printing chars")
            return

        text_lower = text.lower()
        for badword_regex in self.badWords:
            if badword_regex.search(text_lower):
                self.naughtyMessage(sender, "bad word: " + badword_regex.pattern)
                return

        #Passed all automatic checks. Add it to our cache.
        self.lineCache.append(text.rstrip("\n"))
        #Drop oldest line after cache is full
        if len(self.lineCache) > MaxChatLines:
            self.lineCache.pop(0)
            
        #If we have enough lines and the queue is empty then submit and restart our cache
        if len(self.lineCache) == MaxChatLines and self.submissionQueue.empty():
            #print "BrainAgeIrcBot submitted some chat lines: " + "".join(self.lineCache)
            self.submissionQueue.put("\n".join(self.lineCache), block=False)
            lineList = []
            
        #Check for submission manager exit - user types exit at prompt
        if not self.submissionManager.isAlive():
            self.connection.quit("User exited")

    def getBadWords(self, filename):
        #Make sure all the entries are lower case
        #We lower-case the incoming text to make the check case-insensitive
        badWords = open(filename)
        badWordList_strings = set([word.strip().lower() for word in badWords.readlines()])
        badWords.close()

        if '' in badWordList_strings:
            badWordList_strings.remove('')

        badWordList_regex_strings = []

        for word in badWordList_strings:
            word = re.sub(r'[sz]', '[s5z2$]', word)
            word = re.sub(r'a', '[a4]', word)
            word = re.sub(r'e', '[e3]', word)
            word = re.sub(r'i', '[i1]', word)
            word = re.sub(r'l', '[l1]', word)
            word = re.sub(r'o', '[o0]', word)
            word = re.sub(r't', '[t7]', word)
            word = re.sub(r'g', '[g6]', word)
            word = re.sub(r'b', '[b8]', word)
            word = re.sub(r'f', '(f|ph)', word)
            word = re.sub(r'(c|k)', '[ck]', word)
            badWordList_regex_strings.append(word)

        badWordList = []

        for word in badWordList_regex_strings:
            badWordList.append(re.compile(word))

        return badWordList


def main():
    if ':' in IrcServer:
        try:
            server, port = IrcServer.split(":")
            port = int(port)
        except Exception:
            print("Error: Bad server:port specified")
            sys.exit(1)
    else:
        server = IrcServer
        port = 6667

    from submission_manager import SubmissionManager
    submissionQueue = Queue()
    submissionManager = SubmissionManager(submissionQueue)
    
    #For testing make the human review default to accept after a short wait
    #submissionManager.humanReviewTime = 10.0
    #submissionManager.defaultHumanResponse = True
    
    #Note that starting the submission manager does not start desmume for that check
    submissionManager.start()
    ircBot = BrainAgeIrcBot(submissionManager)

    try:
        ircBot.connect(server, port, IrcNick, password=IrcPassword, username=IrcNick)
    except irc.client.ServerConnectionError as x:
        print(x)
        sys.exit(1)
    ircBot.start()

if __name__ == "__main__":
    main()
