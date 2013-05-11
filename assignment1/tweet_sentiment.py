import sys
import re
import unicodedata
import json
from collections import defaultdict


# A list of standard punctuation used as the default list of characters to
# delete from a text's text before calculating its sentiment score.
# The punctuation data structure must be a dict where each character
# is a key with a value of None. This is neccessary since the
# unicode version of the translate method doesn't actually support the
# deletechars keyword argument (as the ascii version does). Instead, it
# will remove characters from unicode string if the value for that
# character is None.
punctuation=dict.fromkeys([i for i in xrange(sys.maxunicode)
    if unicodedata.category(unichr(i)).startswith('P') and
    unichr(i) != u"'"])  # ignore apostrophes to allow contractions

def load_tweets(filename):
    """Loads the tweets file into a python list"""
    tweets = []
    with open(filename) as fin:
        tweets = [json.loads(line) for line in fin]
    return tweets

def load_sentiments(filename):
    """Loads the sentiments file into a python dict"""
    sentiments = defaultdict(float)
    with open(filename) as fin:
        for line in fin:
            word, sentiment = re.split('\t+', line)
            sentiments[word] = float(sentiment)
    return sentiments

def main(sentiment_filename, tweet_filename):
    sentiments = load_sentiments(sentiment_filename)
    tweets = load_tweets(tweet_filename)
    for tweet in tweets:
        # Remove the punctuation and split into words
        words = tweet.get('text', u'').translate(punctuation).split()
        score = sum(sentiments['word'] for word in words)
        print float(score)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >> sys.stderr, 'usage: %s <sentiment_file> <tweet_file>' % sys.argv[0]
        sys.exit(1)
    main(*sys.argv[1:])
