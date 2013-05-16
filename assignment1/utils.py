import sys
import re
import unicodedata
from collections import defaultdict

try:
    import simplejson as json
except ImportError:
    import json


def split_words(tweet):
    """Splits the text for the given tweet into a list of words

    This function will first remove all of the punctuation in the text before
    splitting the text into a list of words.

    """
    # The punctuation data structure must be a dict where each character
    # is a key with a value of None. This is neccessary since the
    # unicode version of the translate method doesn't actually support the
    # deletechars keyword argument (as the ascii version does). Instead, it
    # will remove characters from unicode string if the value for that
    # character is None.
    #
    # The punctuation dict is cached on the function object since its creation
    # can be expensive when done repeatedly for every tweet.
    punctuation = getattr(split_words, "_punctuation", None)
    if punctuation is None:
        punctuation = dict.fromkeys([i for i in xrange(sys.maxunicode)
            if unicodedata.category(unichr(i)).startswith('P') and
            unichr(i) != u"'"])  # ignore apostrophes to allow contractions
        setattr(split_words, "_punctuation", punctuation)

    text = tweet.get('text', u'')
    text = unicode(text) if not isinstance(text, unicode) else text

    return text.lower().translate(punctuation).split()


def load_tweets(filename):
    """Loads the tweets file into a python list"""
    tweets = []
    with open(filename) as fin:
        tweets = [json.loads(line) for line in fin]
    return tweets


def load_sentiments(filename):
    """Loads the sentiments file into a python dict"""
    sentiments = {}
    with open(filename) as fin:
        for line in fin:
            # Skip commented out lines
            if line.strip().startswith('#'):
                continue
            word, sentiment = re.split('\t+', line)
            sentiments[word] = float(sentiment)
    return sentiments
