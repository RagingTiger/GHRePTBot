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
import re
import os
import sys
import fire
import json
import twitter
import termcolor
import slackclient

# globals
BANNER = '''
                _____  _   _ ______    ______ ___________       _
               |  __ \| | | || ___ \   | ___ \_   _| ___ \     | |
               | |  \/| |_| || |_/ /___| |_/ / | | | |_/ / ___ | |_
               | | __ |  _  ||    // _ \  __/  | | | ___ \/ _ \| __|
               | |_\ \| | | || |\ \  __/ |     | | | |_/ / (_) | |_
                \____/\_| |_/\_| \_\___\_|     \_/ \____/ \___/ \__|
'''
FILTER_CONFIG = '.filterconfig.json'
TW_TOKENS = '.twitter_tokens'
SLK_TOKENS = '.slack_tokens'
TSTRM_MSG = '{2}{0}Twitter Stream {1}{0}'.format(29*'-', '{0}', '{1}')
PST_FRMT_LNK = '{0} | From: {1}, Refs: {2}'
PST_FRMT_NOLNK = '{0} | From: {1}'


# utility funcs
def token_reader(token_file):
    """Utility function to read token files."""
    with open(token_file, 'r') as token:
        for line in token:
            tokenpair = line.split('=')
            os.environ[tokenpair[0]] = tokenpair[1].strip('\n')


def compile_regex(words):
    """Adds word boundaries and returns compiled regex."""
    blocks = [r'\b{0}\b'.format(w.encode('utf-8')) for w in words]
    return re.compile('|'.join(blocks), flags=re.I)


def colortxt(text, cval='yellow'):
    """Simple wrapper func for termcolor.colored() method."""
    print '{0}\n'.format(termcolor.colored(text, cval))


def warn(text, cval='red', exit=True):
    """Wrapper for printing error message to stdout and exiting."""
    # control flow
    if exit:
        sys.exit(termcolor.colored(text, cval))
    else:
        print termcolor.colored(text, cval)


# classes
class ConfigTwitterApp(object):
    pass


class ConfigSlackApp(object):
    pass


class ConfigFilter(object):
    """Configure your filter file (e.g. .filterconfig.json)."""
    def __init__(self, filterfile):
        pass


class TerminalOut(object):
    """Builds filter function for filtering tweets to stdout."""
    def __init__(self, match_words, debug):
        # store debug flag
        self.debug = debug

        # store match words to filter on
        self.mwords = match_words

        # get regex
        self.regex = compile_regex(match_words)

        # store user format string
        self._usr_frmt = 'twitter.com/{0}'

    def make_filter(self):
        """Return a custom filter function for stdout."""
        def match_word(tweet):
            # check if word in text
            if self.regex.search(tweet['text'].encode('utf-8')):
                self.terminal_outlet(tweet, self.mwords)
            elif self.debug:
                colortxt(tweet['text'].encode('utf-8'), 'white')
        # return wrapped matcher
        return match_word

    def terminal_outlet(self, tweet_obj, word_list):
        """Take in tweet object and prepare/format for terminal stdout."""
        # get text, username, and twitter links
        tw_text = self.tweet_highlight(tweet_obj['text'].encode('utf-8'),
                                       word_list)
        tw_user = tweet_obj['user']['screen_name'].encode('utf-8')
        tw_user = self._usr_frmt.format(tw_user)
        tw_urls = tweet_obj['entities']['urls']

        # get urls
        if tw_urls:
            # get urls
            tco_url = ''
            for url in tw_urls:
                try:
                    tco_url += url['url'].encode('utf-8') + ' '
                except AttributeError:
                    continue

            if tco_url:
                post = PST_FRMT_LNK.format(tw_text, tw_user, tco_url)
            else:
                post = PST_FRMT_NOLNK.format(tw_text, tw_user)

        else:
            # no links
            post = PST_FRMT_NOLNK.format(tw_text, tw_user)

        # print out post
        print '{0}\n'.format(termcolor.colored(post, 'yellow'))

    @staticmethod
    def tweet_highlight(text, word_list):
        """Takes in Tweet text and highlights the filtered word."""
        # lower, sort, and reverse word_list (for regex reasons)
        word_list = [w.lower() for w in word_list]
        word_list.sort(reverse=True)

        # get list of all matches
        match_exp = compile_regex(word_list)
        match_list = match_exp.findall(text)

        # loop over matches
        for match in match_list:
            # highlight words
            text = re.sub(r'\b{0}\b'.format(match),
                          '\x1b[31m{0}\x1b[33m'.format(match), text)

        # get http/https
        # links_exp = re.compile(r'\bhttp[s]?://[^ ]*', re.I)

        # get highlighted text
        return text


class SlackOut(object):
    """Builds filter function for filtering tweets to Slack."""
    def __init__(self, fwords, debug):
        # store slack app
        self.slack_app = SlackApp()

        # store debug flag
        self.debug = debug

        # get keys from dict
        self.regexdict = {k: compile_regex(v) for k, v in fwords.iteritems()}

        # store ref format
        self._ref_frmt = '<{0}|{1}>'
        self._usr_frmt = '<https://twitter.com/{0}|@{0}>'

    def make_filter(self):
        """Return a custom filter function for stdout."""
        def match_word(tweet):
            # set flag
            match = False

            # get text from tweet
            tw_text = tweet['text'].encode('utf-8')

            # iterate through channel/regex pairs
            for channel, regex in self.regexdict.iteritems():
                # check if word in text
                if regex.search(tw_text):
                    self.slack_app.post_msg(self.format_post(tweet), channel)
                    match = True

            # debug
            if self.debug and not match:
                self.slack_app.post_msg(tw_text, 'debug')

        # return wrapped matcher
        return match_word

    def format_post(self, tweet_obj):
        """Format tweet to post to Slack."""
        # get text, username, and twitter links
        tw_text = tweet_obj['text'].encode('utf-8')
        tw_user = tweet_obj['user']['screen_name'].encode('utf-8')
        tw_user = self._usr_frmt.format(tw_user)
        tw_urls = tweet_obj['entities']['urls']

        # get urls
        if tw_urls:
            # get urls
            src_url = ''
            for i, url in enumerate(tw_urls):
                try:
                    link = url['expanded_url'].encode('utf-8')
                    src_url += self._ref_frmt.format(link, i+1) + ' '
                except AttributeError:
                    continue

            if src_url:
                post = PST_FRMT_LNK.format(tw_text, tw_user, src_url)
            else:
                # no urls in list, so no links
                post = PST_FRMT_NOLNK.format(tw_text, tw_user)

        else:
            # no links
            post = PST_FRMT_NOLNK.format(tw_text, tw_user)

        # print out post
        return post


class TwitterOut(object):
    pass


class TwitterStreamFilter(object):
    """Class to implement filtering of Twitter stream"""
    def __init__(self, config, filterflags):
        # store filterflags
        self._fflags = filterflags

        # get twitter client
        self._twitter_feed = None

        # get slack client
        self._slack_feed = None

        # read in config file
        self.filter_config = self._read_config(config)

    def _read_config(self, infile):
        """Method to read in config file."""
        # try reading
        try:
            with open(infile, 'r') as configfile:
                output = json.loads(configfile.read())
        except IOError:
            warn('File {0} not found\n'.format(infile))
        except ValueError:
            warn('Format error in filter config file\n')

        # finish
        return output

    def _twitter_filters(self, func_list):
        """Wrapper func for list of functions to be used on Tweet filtering."""
        def wrapped_func(tweet):
            for func in func_list:
                func(tweet)

        # get new func
        return wrapped_func

    def _setup_filters(self):
        """Get list of all the filter functions you will be using."""
        # list of filters
        filter_list = []

        # set initial debugmode
        debugmode = False

        # check loaded file
        if 'twitter' in self.filter_config and self._fflags['twitter']:
            # # make sure entry for stdout is type dict
            # fwords = filter_config['twitter']
            # if type(fwords) is dict:
            # TODO
            print self.filter_config['twitter']

        if 'stdout' in self.filter_config and self._fflags['stdout']:
            # make sure entry for stdout is type list
            fwords = self.filter_config['stdout']
            if type(fwords) is list:
                # check debug
                debug = True if self._fflags['stdout'] == 'debug' else False

                # set debug mode
                debugmode = debugmode or debug

                # get stdout filter
                stdout_filter = TerminalOut(fwords, debug)

                # get match func
                filter_list.append(stdout_filter.make_filter())

        if 'slack' in self.filter_config and self._fflags['slack']:
            # makae sure entry for slack is type dict
            fwords_dict = self.filter_config['slack']
            if type(fwords_dict) is dict:
                # check debug
                debug = True if self._fflags['slack'] == 'debug' else False

                # set debug mode
                debugmode = debugmode or debug

                # get slack filter
                slack_filter = SlackOut(fwords_dict, debug)

                # add to func list
                filter_list.append(slack_filter.make_filter())

        # start up Twitter OAuth
        self._twitter_feed = TwitterApp(debugmode)

        # return list of filter funcs
        return filter_list

    def filter_tweets(self):
        """Startup Twitter stream and filter."""
        # get list of filter functions from filter config file
        filter_funcs = self._twitter_filters(self._setup_filters())

        # pass filters func to Twitter stream
        self._twitter_feed.tweet_text_stream(filter_funcs)


class SlackApp(object):
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
        # check for pound char
        if len(channel.split('#')) == 2:
            channel = channel.split('#')[1]

        # send message
        self._slk_instance.api_call('chat.postMessage', as_user='true',
                                    channel='#{0}'.format(channel), text=msg)


class TwitterApp(object):
    """Class to implement a basic Twitter client for use with GHRePTBot."""
    def __init__(self, debug):
        # set debugmode
        self.debugmode = debug

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
            colortxt(TSTRM_MSG.format('Started', ''), 'green')
            # loop over stream
            for tweet in self._tw_instance.user():
                try:
                    func(tweet)
                except KeyError:
                    if self.debugmode:
                        warn('Data {0} Skipped\n'.format(tweet.keys()),
                             'green', False)
        # exit on Ctrl-C
        except KeyboardInterrupt:
            warn(TSTRM_MSG.format('Stopped', '\n\n'))


class GHRePTBot(object):
    """Class to implement GHRePT methods for CLI and automation."""
    def __init__(self):
        # TODO
        colortxt(BANNER, 'green')

    def _setenv(self, twitter_token=TW_TOKENS, slack_token=SLK_TOKENS):
        """Export necessary tokens to run GHRePTBot."""
        # first read twitter token
        try:
            token_reader(twitter_token)
        except IOError:
            warn('Twitter token file not found. Check name/path of file.')

        # second read slack_token
        try:
            token_reader(slack_token)
        except IOError:
            warn('Slack token file not found. Check name/path of file.')

    def help(self, slack=None, twitter=None, stdout=None):
        """Help method for GHRePTBot. Prints usage on default."""
        pass

    def filter(self, configfile=FILTER_CONFIG, slack=None, twitter=None,
               stdout=None, env=None):
        """Simple method to filter and post tweets."""
        # set environment
        if not env:
            self._setenv()

        # create filterflags dict
        fflags = {'slack': slack, 'twitter': twitter, 'stdout': stdout}

        # check flags
        if not any(fflags.values()):
            # warn user
            warn('Defaulting to stdout: '
                 'run \'ghrept help --filter\' for more info\n', exit=False)

            # stdout is on by default
            fflags['stdout'] = True

        # load config file and setup sh*t
        ghrept_filter = TwitterStreamFilter(configfile, fflags)

        # run
        ghrept_filter.filter_tweets()

    def configure(self, filterconfig=None, twitter=None, slack=None):
        """Method to configure tokens or filter settings."""
        # # control flow on config
        # if filterconfig:
        #     # call filterconfig
        #     ConfigFilter(FILTER_CONFIG if filterconfig == '' else filterconfig)
        #
        # if twitter:
        #     ConfigTwitterApp(TW_TOKENS if twitter == '' else twitter)
        #
        # if slack:
        #     ConfigSlackApp(SLK_TOKENS if slack == '' else slack)
        pass

    def setup(self):
        """Walkthrough setup process for Twitter/Slack."""
        pass

    def test_twitter_api(self):
        """Get tweets from home timeline stream."""
        # start client
        TwitterApp().tweet_text_stream()

    def test_slack_api(self, msg="GHRePTBot Test Message", channel='debug'):
        """Post test message to Slack."""
        # post
        SlackApp().post_msg(msg, channel)

    def test_highlight(self, text):
        # words to match
        words = ["at", "the", "he", "she", "a", "in", "on", "with", "is",
                 "what", "you", "about"]

        # highlight
        print TerminalOut.tweet_highlight(text, words)

    def test_matcher(self, text):
        # words to match
        words = ["at", "the", "he", "she", "a", "in", "on", "with", "is"]

        # get matcher
        regex = compile_regex(words)

        # create matcher
        matcher = match_wrapper(regex, words, tweet_highlight, debug=True)

        # run matcher
        matcher(text)


# executable
if __name__ == '__main__':

    # get fire instance
    fire.Fire(GHRePTBot)
