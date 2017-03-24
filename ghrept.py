#!/usr/bin/env python

"""
Author: John D. Anderson
Email: jander43@vols.utk.edu
Description: "grep"-ing for GitHub Repos Posted on Twitter
Usage:
    ghrept
    ghrept filter
    ghrept configure
    ghrept test-twitter-api
    ghrept test-slack-api
"""

# libs
import os
import sys
import fire
import json
import twitter
import termcolor
import slackclient

# globals
FILTER_CONFIG = '.filterconfig.json'


# funcs
def highlight(text, word, hval='red'):
    """Takes in Tweet text and highlights the filtered word."""
    # color paragraphs
    colored_text = termcolor.colored(text, 'yellow')

    # highlight
    return colored_text.format('\x1b[31m{0}\x1b[33m'.format(word))


def colortxt(text, cval='yellow'):
    """Simple wrapper func for termcolor.colored() method."""
    print '{0}\n'.format(termcolor.colored(text, cval))


def filter_wrap(func_list):
    """Wrapper func for list of functions to be used on Tweet filtering."""
    def wrapped_func(data):
        for func in func_list:
            func(data)

    # get new func
    return wrapped_func


# classes
class FilterConfig(object):
    """Class to implement reading of FILTER_CONFIG file."""
    def __init__(self, config):
        # read in config file
        self.dict = self._read_config(config)

    def _read_config(self, infile):
        """Method to read in config file."""
        # try reading
        try:
            with open(infile, 'r') as configfile:
                output = json.loads(configfile.read())
        except IOError:
            output = None

        # finish
        return output


class SlackGHRePT(object):
    """Class to implement a basic Slack client for use with GHRePTBot."""
    def __init__(self):
        # get token
        slk_token = self._slack_token()

        # get Slack instance
        self._slk_instance = slackclient.SlackClient(slk_token)

    def _slack_token(self):
        """Authorize bot to access Slack team."""
        return os.environ.get('SLACK_API_TOKEN')

    def post_msg(self, msg, channel):
        """Post msg to a Slack channel."""
        # send message
        self._slk_instance.api_call('chat.postMessage', as_user='true',
                                    channel='#{0}'.format(channel), text=msg)


class TwitterGHRePT(object):
    """Class to implement a basic Twitter client for use with GHRePTBot."""
    def __init__(self):
        # get OAuth
        oauth = self._twitter_oauth()

        # set domain
        domain = 'userstream.twitter.com'

        # get Twitter instance
        self._tw_instance = twitter.TwitterStream(auth=oauth, domain=domain)

    def _twitter_oauth(self):
        """Creating dict of environment variables for Twitter OAuth."""
        # env variables
        envd = {
                    'TCK': 'TWITTER_CONSUMER_KEY',
                    'TCS': 'TWITTER_CONSUMER_SECRET',
                    'TAT': 'TWITTER_ACCESS_TOKEN',
                    'TATS': 'TWITTER_ACCESS_TOKEN_SECRET'
        }

        # dict comp
        toked = {key: os.environ.get(value) for key, value in envd.iteritems()}

        # return OAuth
        return twitter.OAuth(toked['TAT'], toked['TATS'], toked['TCK'],
                             toked['TCS'])

    def tweet_text_stream(self, func=colortxt):
        """Get the actual content of the tweet, and no meta info."""
        # loop
        try:
            # announce start
            colortxt('Twitter Stream Started :)', 'green')
            # loop over stream
            for tweet in self._tw_instance.user():
                try:
                    func(tweet['text'].encode('utf-8'))
                except KeyError:
                    colortxt('Data {0} Skipped'.format(tweet.keys()), 'green')
        # exit on Ctrl-C
        except KeyboardInterrupt:
            sys.exit(colortxt('\n\nHalting Twitter Stream :(', 'red'))


class GHRePTBot(object):
    """Class to implement GHRePT methods for CLI and automation."""
    def __init__(self):
        # get twitter client
        self._twitter_feed = None

        # get slack client
        self._slack_feed = None

    def help(self, slack=None, twitter=None, stdout=None):
        """Help method for GHRePTBot. Prints usage on default."""
        pass

    def filter(self, configfile=FILTER_CONFIG):
        """Simple method to filter and post tweets."""
        # get twitter auth
        self._twitter_feed = TwitterGHRePT()

        # get config file
        filter_config = FilterConfig(configfile)

        if 'slack' in filter_config.dict:
            # # get slack auth
            # self._slack_feed = SlackGHRePT()
            # TODO

            # try to load it
            print filter_config.dict['slack']

        if 'twitter' in filter_config.dict:
            # print
            print filter_config.dict['twitter']

        # # dict of filter functions
        # tweet_filters = {}
        #
        # # TODO
        # pass

    def configure(self):
        """Method to configure tokens or filter settings."""
        # TODO
        pass

    def test_twitter_api(self):
        """Get tweets from home timeline stream."""
        # start client
        TwitterGHRePT().tweet_text_stream()

    def test_slack_api(self, msg="GHRePTBot Test Message", channel='general'):
        """Post test message to Slack."""
        # post
        SlackGHRePT().post_msg(msg, channel)


# executable
if __name__ == '__main__':

    # get fire instance
    fire.Fire(GHRePTBot)
