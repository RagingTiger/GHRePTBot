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
import twitter
import fire

# constants
DOMAIN = 'userstream.twitter.com'


# classes
class GHRePT(object):
    """Class to implement GHRePT protocols."""
    def __init__(self):
        # get OAuth
        oauth = self._twitter_oauth()

        # get Twitter instance
        self._tw_instance = twitter.TwitterStream(auth=oauth, domain=DOMAIN)

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

    def _tweet_text_stream(self):
        """Get the actual content of the tweet, and no meta info."""
        # loop
        try:
            for tweet in self._tw_instance.user():
                try:
                    print '{0}\n'.format(tweet['text'].encode('utf-8'))
                except KeyError:
                    print 'Skipping Header Info'
                except:
                    print 'Error occured :|'
        except KeyboardInterrupt:
            sys.exit('\n\nHalting Twitter Stream :)\n')

    def test_api(self):
        """Get tweets from home timeline stream."""
        # print
        self._tweet_text_stream()


# executable
if __name__ == '__main__':

    # get fire instance
    fire.Fire(GHRePT)
