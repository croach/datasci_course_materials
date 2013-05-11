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
# punctuation=dict.fromkeys([i for i in xrange(sys.maxunicode)
#     if unicodedata.category(unichr(i)).startswith('P') and
#     unichr(i) != u"'"])  # ignore apostrophes to allow contractions

def load_tweets(filename):
    """Loads the tweets file into a python list"""
    tweets = []
    with open(filename) as fin:
        tweets = [json.loads(line) for line in fin]
    return tweets

def load_sentiments(filename):
    """Loads the sentiments file into a python dict"""
    sentiments = defaultdict(lambda: None)
    with open(filename) as fin:
        for line in fin:
            word, sentiment = re.split('\t+', line)
            sentiments[word] = float(sentiment)
    return sentiments

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
        punctuation=dict.fromkeys([i for i in xrange(sys.maxunicode)
            if unicodedata.category(unichr(i)).startswith('P') and
            unichr(i) != u"'"])  # ignore apostrophes to allow contractions
        setattr(split_words, "_punctuation", punctuation)

    return tweet.get('text', u'').translate(punctuation).split()

def calculate_missing_sentiments(sentiments, tweets):
    """Calculates sentiment scores for words missing from the sentiments dict

    This function calculates the sentiment scores for all words in the given
    tweets list that cannot be found in the given sentiments dict. It does
    so by calculating the sentiment scores for all of the given tweets and
    then calculating a word's sentiment score based on the number of positive
    vs negative tweets that the word appears within. The scores are normalized
    on a [-5, 5] range to match the scores in the sentiments files used to
    construct the sentiments dict. It returns a dict mapping each of the
    missing words to their corresponding sentiment value.

    Arguments:
    sentiments -- a dict of sentiment scores
    tweets -- a list of tweets

    Returns:
    A dict mapping words to sentiment scores.
    """
    missing_scores = {}

    # For each tweet, calculate its sentiment score and then increment the
    # positive (or negative) count for the missing words in the tweet based
    # on the positive or negative outcome of the tweet itself.
    for tweet in tweets:
        words = split_words(tweet)
        scores = [(word, sentiments[word]) for word in words]
        score = sum(score for _, score in scores if score is not None)
        missing_words = [w for w, s in scores if s is None]
        for word in missing_words:
            if word not in missing_scores:
                missing_scores[word] = {
                    'positive': 0.0,
                    'negative': 0.0
                }

            if score > 0:
                missing_scores[word]['positive'] += 1.0
            elif score < 0:
                missing_scores[word]['negative'] += 1.0
            else:
                pass


    # Determine each missing words' sentiment (positive or negative) and value
    for word, data in missing_scores.items():
        positive = data['positive']
        negative = data['negative']
        if positive > negative:
            prob = positive/(positive + negative)
        elif positive < negative:
            prob = -1.0 * negative/(positive + negative)
        else:
            prob = 0.0
        score = round(prob * 5.0)
        missing_scores[word] = score

    return missing_scores

def main(sentiment_filename, tweet_filename):
    sentiments = load_sentiments(sentiment_filename)
    tweets = load_tweets(tweet_filename)
    missing_sentiments = calculate_missing_sentiments(sentiments, tweets)
    for tweet in tweets:
        words = split_words(tweet)
        for word in words:
            if sentiments[word] is None:
                try:
                    print word, missing_sentiments[word]
                except UnicodeEncodeError:
                    print word.encode('utf-8'), missing_sentiments[word]

# def main(sentiment_filename, tweet_filename):
#     sentiments = load_sentiments(sentiment_filename)
#     tweets = load_tweets(tweet_filename)
#     for tweet in tweets:
#         # Remove the punctuation and split into words
#         words = tweet.get('text', u'').translate(punctuation).split()
#         scores = [(word, sentiments[word]) for word in words]
#         positive_words = filter(lambda (_, s): s is not None and s > 0, scores)
#         negative_words = filter(lambda (_, s): s is not None and s < 0, scores)
#         missing_words = filter(lambda (_, s): s is None, scores)
#         score = sum(score for _, score in scores if score is not None)
#         total = lambda words: sum(float(s) for _, s in words)
#         if score > 0:
#             missing_score = round(total(positive_words)/len(positive_words))
#         elif score < 0:
#             missing_score = round(total(negative_words)/len(negative_words))
#         else:
#             missing_score = 0.0

#         for word, _ in missing_words:
#             try:
#                 print word, float(missing_score)
#             except UnicodeEncodeError:
#                 print word.encode('utf-8'), float(missing_score)

#         filter(lambda _, score: score is None, scores)
#         positive_words = sum([1 for score in filter(None, scores) if score > 0])
#         negative_words = sum([1 for score in filter(None, scores) if score < 0])
#          # = positive_words + negative_words

#         print float(score)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >> sys.stderr, 'usage: %s <sentiment_file> <tweet_file>' % sys.argv[0]
        sys.exit(1)
    main(*sys.argv[1:])
