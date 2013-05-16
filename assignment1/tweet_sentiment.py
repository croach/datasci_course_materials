import sys

from utils import *


def main(sentiment_filename, tweet_filename):
    sentiments = load_sentiments(sentiment_filename)
    tweets = load_tweets(tweet_filename)
    for tweet in tweets:
        # Remove the punctuation and split into words
        words = split_words(tweet)
        score = sum(sentiments.get(word, 0) for word in words)
        print float(score)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >> sys.stderr, 'usage: %s <sentiment_file> <tweet_file>' % sys.argv[0]
        sys.exit(1)
    main(*sys.argv[1:])
