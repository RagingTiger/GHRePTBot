#!/usr/bin/env python

"""
Author: John D. Anderson
Email: jander43@vols.utk.edu
Description: Script to obtain tokens for Twitter API
Usage: tokens
"""

# libs
import sys
import webbrowser


# globals
MSG_USER = '''
A webbrowser has been opened to the following address: apps.twitter.com. Please
check the README.md file for info on how to copy/paste tokens from the web page
to the terminal.
'''
TOKEN_FILE = './.twitter_tokens'
TOKEN_URL = 'http://apps.twitter.com'
TOKEN_NAMES = ('TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET',
               'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET')


# funcs
def get_tokens():
    # token dict
    tokens = {}

    # notify user
    print MSG_USER

    # get input
    try:
        for toke in TOKEN_NAMES:
            # prompt user
            tokens[toke] = raw_input('{0}: '.format(toke)).strip()
    except KeyboardInterrupt:
        sys.exit('\n\nAborting token file configuration\n')

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
