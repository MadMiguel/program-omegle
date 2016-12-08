#!/usr/bin/python
"""
ProgramOMegle.py

a script to link up your Program-O installation with the Omegle random chat service

this script assumes you haven't modified the Program-O API and it can be accessed at the
default location - <YOUR.URL>/Program-O/chatbot/conversation_start.php

"""
import urllib2 as url
import urllib
import httplib as http

import json, requests, time, random

# the root of where your Program-O install is
# if your install is at www.mysite.com/Program-O/
# then _SERVER should be "http://www.mysite.com"
_SERVER = ""

# the bot_id for the bot you want the user to talk to
_BOT_ID = "1"

def start_convo(bot_id):
    """
    starts a conversation with the given bot and returns the convo_id
    """
    _START_URL = _SERVER+"/Program-O/chatbot/conversation_start.php?say=hello&bot_id="+bot_id+"&format=json"
    try:
        req = requests.get(_START_URL)
    except requests.exceptions.ConnectionError as ce:
        print "ConnectionError:\n", ce
        return False
    if req.status_code != 200:
        print "bad response code:", req.status_code
        return False
    res_json = json.loads(req.text)
    # print "res_json:\n", res_json
    cid = res_json['convo_id']
    print "started new conversation:", cid
    return cid

def get_response(bot_id, convo_id, human_input):
    """
    for continuing the conversation at convo_id
    sends the human input and returns the response as a string
    """
    _RESPONSE_URL = _SERVER+"/Program-O/chatbot/conversation_start.php?say="+human_input+"&bot_id="+bot_id+"&convo_id="+convo_id+"&format=json"
    try:
        req = requests.get(_RESPONSE_URL)
    except Exception as ex:
        print "Exception getting _RESPONSE_URL:\n", ex
        return False
    if req.status_code != 200:
        print "bad response code:", req.status_code
        return False
    res_json = json.loads(req.text)
    botMsg = res_json['botsay']
    return botMsg.lower()

#This simply cuts the extra characters to isolate the ID
def fmtId( string ):
    return string[1:len( string ) - 1]

#Talk to people
def talk(id,req,hMsg,convo_id):

    #Show the server that we're typing
    typing = url.urlopen('http://omegle.com/typing', '&id='+id)
    typing.close()

    #Show the user that we can write now
    # msg = str(raw_input('> '))
    # get it from the bot
    msg = get_response(bot_id=_BOT_ID, convo_id=convo_id, human_input=hMsg)
    time.sleep(random.randint(1, 3))
    print "Robot:", msg

    #Send the string to the stranger ID
    msgReq = url.urlopen('http://omegle.com/send', '&msg='+msg+'&id='+id)

    #Close the connection
    msgReq.close()


#This is where all the magic happens, we listen constantly to the page for events
def listenServer( id, req, cid ):

    while True:

        site = url.urlopen(req)

        #We read the HTTP output to get what's going on
        rec = site.read()

        connected = True

        if 'waiting' in rec:
            print("Looking for humans ...")

        elif 'connected' in rec and connected:
            # double connection thing. treat as dc
            print('Human has left')
            #We start the whole process again
            omegleConnect()

        elif 'connected' in rec:
            print('Found one')
            print(id)
            if 'gotMessage' in rec:
                humanMsg = rec[16:len( rec ) - 2]
                print "Human:", humanMsg
                talk(id,req,humanMsg,cid)
            else:
                #Since this isn't threaded yet, it executes the talk function (yeah, turn by turn)
                talk(id,req,"",cid)
            
        elif 'strangerDisconnected' in rec:
            print('Human has left')
            #We start the whole process again
            omegleConnect()
            
        elif 'typing' in rec:
            print("Human is typing something...")

        #When we receive a message, print it and execute the talk function            
        elif 'gotMessage' in rec:
            humanMsg = rec[16:len( rec ) - 2]
            print "Human:", humanMsg
            talk(id,req,humanMsg,cid)


#Here we listen to the start page to acquire the ID, then we "clean" the string to isolate the ID
def omegleConnect():
    site = url.urlopen('http://omegle.com/start','')
    id = fmtId( site.read() )
    print(id)
    req = url.Request('http://omegle.com/events', urllib.urlencode( {'id':id}))
    print('Starting search...')

    # start a conversation
    cid = start_convo(_BOT_ID)

    #Then we open our ears to the wonders of the events page, where we know if anything happens
    #We have to pass two arguments: the ID and the events page.
    listenServer(id,req,cid)


# I just didn't use the __init__ method    
omegleConnect()