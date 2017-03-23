#!/usr/bin/env python

"""
Author: John D. Anderson
Email: jander43@vols.utk.edu
Description: "grep"-ing for GitHub Repos Posted on Twitter
Usage:
    ghrept
    ghrept test-api
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
        self.config_dict = self._read_config(config)

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
    pass


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
        self._twitter_feed = TwitterGHRePT()

        # get slack client
        self._slack = SlackGHRePT()

    def filter(self, configfile=FILTER_CONFIG):
        """Simple method to filter and post tweets."""
        # get config file
        filter_config = FilterConfig(configfile)

        if filter_config.config_dict:
            # try to load it
            print filter_config.config_dict
        else:
            # file was not found
            pass

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
        # print
        self._twitter_feed.tweet_text_stream()


# executable
if __name__ == '__main__':

    # get fire instance
    fire.Fire(GHRePTBot)
