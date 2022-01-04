#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import time
import subprocess
import sys
import getopt
from twython import Twython
import json


# def register(oauth_token, oauth_token_secret)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

twitter = Twython(
    app_key = os.environ['GPMF_APP_KEY'],
    app_secret = os.environ['GPMF_APP_SECRET'],
    oauth_token = os.environ['GPMF_OAUTH_TOKEN'],
    oauth_token_secret = os.environ['GPMF_OAUTH_TOKEN_SECRET']
)


verbose = False

def spotify():
    # for applescript editor
    #set json to "{\"artist\":\"" & theArtist & "\", \"track\":\"" & theTrack & "\", \"http_link\": \"" & httpLink & "\"}
    osascript = """osascript<<END
    if application "Spotify" is running then
        tell application "Spotify"
            set theTrack to name of the current track
            set theArtist to artist of the current track
            set spotifyUrl to spotify url of the current track

            if player state is paused then
                return "{}"
            end if
        end tell

        set httpLink to ""
        if spotifyUrl contains "track" then
            set httpLink to (characters 15 thru 36 of spotifyUrl) as string
            set httpLink to "http://open.spotify.com/track/" & httpLink
        end if
        set json to "{\\"artist\\":\\"\" & theArtist & \"\\", \\"track\\":\\"\" & theTrack & \"\\", \\"http_link\\": \\"\" & httpLink & \"\\"}"
        return json
    else
        return "{}"
    end if
    END"""

    p = subprocess.Popen(osascript, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    song = {}
    if not err:
        song = json.loads(out)
    return song

def tweet(image, status=None):
    if image is None and status is not None:
        twitter.update_status(status)
        msg = 'update Twitter status'
    elif image is not None:
        image_file = open(image, 'rb')
        twitter.update_status_with_media(media=image_file, status=status)
        msg = 'update Twitter status with a image'

    if verbose:
        print(msg)


def get_devices():
    devices = subprocess.run(['imagesnap', '-l'], capture_output=True, text=True)
    return devices.stdout.split('\n')[1:-1]

def is_lid_opened():
    lid = subprocess.run('ioreg -r -k AppleClamshellState -d 4 | grep AppleClamshellState | head -1', shell=True, capture_output=True, text=True)
    return "No" in lid.stdout

def can_run():
    return not (len(get_devices()) == 1 and not is_lid_opened())

def photo():
    timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
    filename = '/Users/ben/.gitshots/%s.jpg' % timestamp
    devices = get_devices()
    if verbose:
        print(devices)
    arg = ''
    if len(devices) > 1:
        arg = ' -d "%s"' % devices[0]
    cmd = 'imagesnap -w 2 -q %s' + arg
    subprocess.call(cmd % filename, shell=True)
    return filename

def git_message():
    message = subprocess.Popen('git log --pretty=oneline --abbrev-commit -1 HEAD | cut -f 1 -d " "', shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    message = message.communicate()[0]
    if verbose:
        print('last commit: %s' % message)
    return message

def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, _ = getopt.getopt(argv[1:], "histv", ["help", "image", "status", "tweet", "spotify"])
        except getopt.error as msg:
            raise Usage(msg)

        if not can_run():
            raise Usage('can\'t run')

        image = None
        status = ''
        msg = {}
        tweeter = False

        try:
            for o, a in opts:
                if o in ('-i', '--image'):
                    image = photo()
                elif o in ('-s', '--status'):
                    msg['git'] = git_message()
                elif o in ('-h', '--help'):
                    pass
                elif o in ('-v', '--verbose'):
                    verbose = True
                elif o in ('--spotify'):
                    song = spotify()
                    if song:
                        msg['spotify'] = u"\u266B %s by %s %s" % (song['track'], song['artist'], song['http_link'])
                elif o in ('-t', '--tweet'):
                    tweeter = True

            for key in ['git', 'spotify']:
                if key in msg:
                    status += msg[key] + ' '

            if tweeter:
                tweet(image, status)
            else:
                print(image, status)

        except Exception as err:
            raise Usage(err)

    except Usage as err:
        #print >>sys.stderr, err.msg
        #print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
