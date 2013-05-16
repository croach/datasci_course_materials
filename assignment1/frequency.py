import sys
from collections import defaultdict

from utils import *


def main(tweet_filename):
    freqs = defaultdict(float)
    tweets = load_tweets(tweet_filename)
    for tweet in tweets:
        words = split_words(tweet)
        for word in words:
            freqs[word] += 1.0
    total_words = sum(freqs.values())

    for word, freq in freqs.iteritems():
        print word, freq/total_words


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, 'usage: %s <tweet_file>' % sys.argv[0]
        sys.exit(1)
    main(sys.argv[1])
