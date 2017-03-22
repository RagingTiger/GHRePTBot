#!/usr/bin/env python

"""
Author: John D. Anderson
Email: jander43@vols.utk.edu
Description: Script to obtain tokens for Twitter API
Usage: tokens
"""

# libs
import webbrowser


# globals
TOKEN_FILE = './.twitter_tokens'
TOKEN_URL = 'http://apps.twitter.com'
TOKEN_NAMES = ('TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET',
               'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET')


# funcs
def get_tokens():
    # token dict
    tokens = {}

    # get input
    for toke in TOKEN_NAMES:
        # prompt user
        tokens[toke] = raw_input('{0}: '.format(toke)).strip()

    # return tokens
    return tokens


def write_token_file(token_dict):
    # write token file
    with open(TOKEN_FILE, 'w') as tokefile:
        for key, value in token_dict.iteritems():
            tokefile.write('export {0}={1}\n'.format(key, value))


def main():
    # open webbrowser
    webbrowser.open(TOKEN_URL)

    # get keys
    token_values = get_tokens()

    # write token file
    write_token_file(token_values)


# executable
if __name__ == '__main__':

    main()
