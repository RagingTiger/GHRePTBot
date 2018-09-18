## About
_**G**it**H**ub **Re**pos**P**osted on **T**witter_ (i.e. **GHRePT**) is a
simple _Twitter bot_. It was originaly designed to _greps tweets_ for the mention of **GitHub**. Why?
Because I wanted a way to _filter my Twitter_ for all the **GitHub** repos
being posted, and what better inspiration for such a tool than [grep](https://en.wikipedia.org/wiki/Grep). 

After accomplishing the "grep"-ing of GitHub-related tweets, I realized I could just as easily abstract it to other keywords
(but the name stuck because I like the way it sound).

## Install
First download the repo, `cd` into it, and setup the virtual environment:

```
git clone https://github.com/RagingTiger/GHRePTBot && cd GHRePTBot
virtualenv venv
```

Now with `venv/` setup, activate it and install the requirements:

```
source venv/bin/activate
pip install -r requirements.txt
```

Finally you will need to get your access tokens:

```
./tokens.py
```

Executing this script will open up your web browser to `aps.twitter.com` and
start an interactive prompt in the terminal to **copy and paste** the tokens
found on the Twitter Apps webpage into the terminal.

First you will need to **create an app**. There should be a button for this in
the top right corner. After clicking this, you will need to give your **app**
a name, description, and URL (i.e. ragingtiger.github.io/GHRePTBot). Once
finished, click the **Create Your Twitter application** button at the bottom.

Once on the page of your new **Twitter app**, click the tab for **Keys and
Access Tokens**. In here you will find all the tokens you need. At the top are
the tokens for **consumer key** and **consumer secret**. At the bottom, you
must click the **generate access token** button to generate tokens for the
**access token** and **access token secret**.

Once these are all located and filled in according to the interactive prompt at
the terminal and the script has finished, you should see a new file:

```
$ ls .twitter_tokens
.twitter_tokens
```

You will need to source this to export your tokens so that the ghrept command
can find them:

```
source .twitter_tokens
```

Now you should be ready to launch the **Twitter client**:

```
./ghrept.py test-twitter-api
```
