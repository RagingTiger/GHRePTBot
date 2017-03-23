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
import twitter
import termcolor
import slackclient


# funcs
def colortxt(cval, text):
    """Simple wrapper func for termcolor.colored() method."""
    return '{0}\n'.format(termcolor.colored(text, cval))


# classes
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

    def tweet_text_stream(self):
        """Get the actual content of the tweet, and no meta info."""
        # loop
        try:
            for tweet in self._tw_instance.user():
                try:
                    print colortxt('yellow', tweet['text'].encode('utf-8'))
                except KeyError:
                    print colortxt('green', 'Skipping Header Info')
        except KeyboardInterrupt:
            sys.exit(colortxt('red', '\n\nHalting Twitter Stream :)'))


class GHRePTBot(object):
    """Class to implement GHRePT methods for CLI and automation."""
    def __init__(self):
        # get twitter client
        self._twitter_feed = TwitterGHRePT()

        # get slack client
    def test_twitter_api(self):
        """Get tweets from home timeline stream."""
        # print
        self._twitter_feed.tweet_text_stream()


# executable
if __name__ == '__main__':

    # get fire instance
    fire.Fire(GHRePTBot)
