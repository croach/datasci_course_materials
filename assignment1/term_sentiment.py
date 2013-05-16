import sys

from utils import *


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
        scores = [(word, sentiments.get(word, None)) for word in words]
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
            if word not in sentiments:
                try:
                    print word, missing_sentiments[word]
                except UnicodeEncodeError:
                    print word.encode('utf-8'), missing_sentiments[word]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >> sys.stderr, 'usage: %s <sentiment_file> <tweet_file>' % sys.argv[0]
        sys.exit(1)
    main(*sys.argv[1:])
