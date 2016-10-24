'''
Send messages from received emails filtered by procmail to a Cisco Spark room
Syntax is mailtospark2.py -r 'name of the spark room to send to' -m 'name of the local mail directory to send messages from'
-b 'bearer key or leave blank and enter a default in the argparse list'
Requires email messages to be in seperate files e.g. similar to how procmail filters incoming mail.
'''

__author__ = 'Harry Watson'

import glob
import re, os
from shutil import move
import requests
import json
import time
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-b", "--bearer",
                    help="Authorization Bearer (normally the bot's key)",
                    default="bots key goes in here")
parser.add_argument("-r", "--room",
                    default="default room for posts",
                    help="Name of the Spark room to post to, case sensitive")
parser.add_argument("-m", "--mail",
                    help="Name of the mail folder to check")
args = parser.parse_args()

# Global Vars
working_dir = "/Maildir/%s/" %args.mail
roomid = None
tmp_dir = "/tmp" #Directory to place processed emails into after sending to Spark
roomurl = 'https://api.ciscospark.com/v1/rooms/'
messageurl = 'https://api.ciscospark.com/v1/messages'
headers = {'Authorization': 'Bearer '+args.bearer,'Content-type': 'application/json'}

def read_file(filename):
    """read a file and return as single string"""
    f = open(filename, 'r')
    return f.read()

# Collect all roomids the bot belongs to
r = requests.get(roomurl, headers=headers)
parsed = json.loads(r.text)
for rooms in parsed['items']:
    # look for the room id based on room name sent in the arguments
    if args.room == rooms['title']:
        roomid=rooms['id']
        #print (args.room+" uses roomid" + roomid)


if roomid:
    #Collect all messages from the mail directory specified and 
    file_list = filter(os.path.isfile, glob.glob(working_dir + "msg*"))
    file_list.sort(key=lambda x: os.path.getmtime(x))
    #print "heres the files ",file_list

    for f in file_list:
        #print "processing %s" % f
        data = read_file(f)
        date = re.findall(r'Date:\s(.*)', data)[0]
        detail = re.findall(r'Subject:\s(.*)', data)[0]
        messagecontent = {'roomId': roomid,'text':detail}
        r = requests.post(messageurl, data=json.dumps(messagecontent), headers=headers)
        #move the processed mails to the tmp dir for storage or later removal
        move(f, tmp_dir)
