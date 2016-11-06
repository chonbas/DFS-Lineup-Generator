import csv
import argparse
import sys
import os
import pandas as pd
import numpy as np
import boto3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.ensemble import GradientBoostingClassifier as gb_clf
from sklearn.ensemble import RandomForestClassifier as rf_clf
from sklearn.externals import joblib
from sklearn import cross_validation
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from scipy.sparse import coo_matrix, hstack
from nltk.tokenize import TweetTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8') #cause ascii - utf8 errors get old

#Load file into a Pandas dataframe
def load_train_file(path, s3):
    df = pd.read_csv(path, encoding="utf-8")
    if s3:
        raw_data = df[df.columns[0]].values
        target = df[df.columns[1]].values
        is_twitter = df[df.columns[2]].values
    else:
        raw_data = df['body'].values
        target = df['is_harassment'].values
        is_twitter = df['is_twitter'].values
    raw_data = [{'comment':raw_data[i], 'is_twitter':is_twitter[i]} for i in xrange(len(raw_data))]
    num_harass = len([x for x in target if x == 1])
    num_tweets = len([x for x in is_twitter if x == 1])
    print("Loading " + str(len(raw_data)) + " documents for training...")
    print("------------------------------------------------------------")
    print("Found %d harassing comments, %d non-harassing comments") %(num_harass, len(raw_data)-num_harass)
    print("%d of the comments are from Twitter, %d are from Reddit or the Guardian") %(num_tweets, len(raw_data) - num_tweets)
    return raw_data, target
        
#Compute additional features for the data
#currently its sentiment from NLTK's VADER and token count
def compute_add_features(raw_data, raw_is_twitter, sid,verbose_flag):
    if verbose_flag:
        print("Computing token counts, and sentiment-------------")
    tknzr = TweetTokenizer()
        
    num_docs =  len(raw_data)
    token_counts = np.zeros((num_docs, 1), dtype=np.int)
    neg_sentiments = np.zeros((num_docs, 1), dtype=np.int)
    neu_sentiments = np.zeros((num_docs, 1), dtype=np.int)
    pos_sentiments = np.zeros((num_docs, 1), dtype=np.int)
    is_twitters = np.zeros((num_docs,1), dtype=np.int)
    for i in range(0, num_docs):
        line = raw_data[i]
        try:
            tokens = tknzr.tokenize(line)
            token_count = len(tokens)
            sentiment_aggregate = sid.polarity_scores(line) 
            neg_sentiment = sentiment_aggregate['neg']
            pos_sentiment = sentiment_aggregate['pos']
            neu_sentiment = sentiment_aggregate['neu']
        except(TypeError): # in event line is nan (likely due to clrf to rf switches)
            token_count = neg_sentiment = pos_sentiment = neu_sentiment =0
            raw_data[i] = ""
        neg_sentiments[i] = neg_sentiment
        neu_sentiments[i] = neu_sentiment
        pos_sentiments[i] = pos_sentiment
        token_counts[i] = token_count
        is_twitters[i] = raw_is_twitter[i]
    negative_sent = coo_matrix(neg_sentiments)
    neutral_sent = coo_matrix(neu_sentiments)
    positive_sent = coo_matrix(pos_sentiments)
    tokens = coo_matrix(token_counts)
    twitters = coo_matrix(is_twitters)
    return raw_data, twitters, hstack([tokens, negative_sent, neutral_sent, positive_sent])

#Compute TFIDF for the raw data
def compute_tfidf(raw_data, verbose_flag):
    if verbose_flag:
        print("Encoding tf-idf---------------------------------------------")
        print("TF-IDF: Encoding unigram and bigrams........................")

    word_vectorizer = TfidfVectorizer(encoding='utf-8', decode_error='replace', analyzer='word',
                                    use_idf=True, sublinear_tf=True, norm='l2', ngram_range=(1, 2))
    word_tfidf_data = word_vectorizer.fit_transform(raw_data)
    
    if verbose_flag:
        print("TF-IDF: Encoding character ngrams...........................")

    char_vectorizer = TfidfVectorizer(encoding='utf-8', decode_error='replace',
                                      analyzer='char', use_idf=True,
                                      sublinear_tf=True, norm='l2',
                                      ngram_range=(3,6))
    char_tfidf_data = char_vectorizer.fit_transform(raw_data)

    return word_tfidf_data, word_vectorizer, char_tfidf_data, char_vectorizer

#Use Chi-2 to select best K features
def compute_chi2(tfidf_data, target, num_feats, verbose_flag):
    if verbose_flag:
        print("Selecting %d features with chi2---------------------------") % num_feats
    selector = SelectKBest(chi2, k=num_feats)
    ch2 = selector.fit_transform(tfidf_data, target)
    return ch2, selector

def train(path_to_train_data, eval_flag, verbose_flag, num_estimators, prob_threshold,n_folds,s3dump, chi2denom):
    if path_to_train_data == 'S3':
        s3_client = boto3.client('s3')
        s3_client.download_file('hh-model-training-bucket', 'data/data.csv', 'data.csv')
        raw_data, target = load_train_file('data.csv', True)
        os.remove('data.csv')
    else:
        raw_data, target = load_train_file(path_to_train_data, False)

    clf = rf_clf(n_estimators=num_estimators, n_jobs=4, max_depth=None,
                 max_features='sqrt',min_samples_split=6, bootstrap=False,class_weight={0:1, 1:2},random_state=1337)
                 

    sid = SentimentIntensityAnalyzer()

    if (eval_flag):
        if verbose_flag:
            print("Evaluating with %d folds-------------------------------------") %(n_folds)
        total_accuracy = 0.0
        for i in xrange(0, n_folds):
            print("Fold no. %d..................................................") %(i+1)
            print("Pre-processing----------------------------------------------")
            if verbose_flag:
                print("Separating hold out data------------------------------------")
            test_size = 0.2
            data_train, data_test, target_train, target_test = cross_validation.train_test_split(raw_data, target, test_size=test_size, random_state=42)

            if verbose_flag:
                print("Featurizing training data-----------------------------------")
            comments_train = [x['comment'] for x in data_train]
            is_twitter_train = [x['is_twitter'] for x in data_train]

            cleaned_data_train, twitters_train, add_feats_train = compute_add_features(comments_train, is_twitter_train, sid, verbose_flag)

            word_tfidf_train, word_vectorizer, char_tfidf_train, char_vectorizer = compute_tfidf(cleaned_data_train, verbose_flag)
            train_feats = hstack([word_tfidf_train, char_tfidf_train,add_feats_train])

            if verbose_flag:
                print("Shape of feature matrix.....................................")
                print(train_feats.shape)

	        n_feats = int(train_feats.shape[1]/chi2denom)
            ch2_train, selector = compute_chi2(train_feats, target_train, n_feats, verbose_flag)

            if verbose_flag:
                print("Featurizing hold-out data-----------------------------------")
            
            comments_test = [x['comment'] for x in data_test]
            is_twitter_test = [x['is_twitter'] for x in data_test]

            cleaned_data_test, twitters_test, add_feats_test = compute_add_features(comments_test, is_twitter_test, sid, verbose_flag)
            if verbose_flag:
                print("Transforming hold-out for tf-idf----------------------------")
            word_tfidf_test = word_vectorizer.transform(cleaned_data_test)
            char_tfidf_test = char_vectorizer.transform(cleaned_data_test)
            test_feats = hstack([word_tfidf_test, char_tfidf_test, add_feats_test])
            if verbose_flag:
                print("Transforming hold-out with chi2 feature selector------------")
            ch2_test = selector.transform(test_feats)

            print("Training----------------------------------------------------")
            clf.fit(hstack([ch2_train, twitters_train]), target_train)

            print("Evaluating--------------------------------------------------")
            
            predicted_probs = clf.predict_proba(hstack([ch2_test, twitters_test]))
            
            print("Evaluating with harassment probability threshold at %f") %(prob_threshold)
            predicted = []
            for probs in predicted_probs:
                if probs[1] >= prob_threshold:
                    predicted.append(1)
                else:
                    predicted.append(0)
            total_accuracy += evaluate_model(target_test, predicted, verbose_flag)
        print("Average accuracy across %d folds-------------------------")
        print(total_accuracy / float(n_folds))

    else:
        print("Pre-processing----------------------------------------------")

        if verbose_flag:
            print("Featurizing data--------------------------------------------")
        
        comments_train = [x['comment'] for x in raw_data]
        is_twitter_train = [x['is_twitter'] for x in raw_data]

        cleaned_data, twitters, add_feats = compute_add_features(comments_train, is_twitter_train, sid, verbose_flag)
        word_tfidf, word_vectorizer, char_tfidf, char_vectorizer = compute_tfidf(cleaned_data, verbose_flag)
        train_feats = hstack([word_tfidf, char_tfidf,add_feats])

        n_feats = int(train_feats.shape[1]/chi2denom)
        if verbose_flag:
            print("Shape of feature matrix.....................................")
            print(train_feats.shape)
        ch2_train, selector = compute_chi2(train_feats, target, n_feats, verbose_flag)
        ch2 = hstack([ch2_train, twitters])

        print("Training----------------------------------------------------")
        clf.fit(ch2, target)

        print("Writing model to file---------------------------------------")
        write_model_to_file(clf, word_vectorizer, char_vectorizer, selector, sid, verbose_flag, s3dump)

def write_model_to_file(clf, word_vectorizer, char_vectorizer, selector, sid, verbose_flag, s3dump):
    s3_client = None
    if s3dump:
        s3_client = boto3.client('s3')

    if verbose_flag:
        print("Writing model to file at 'pkl/model.gz'---------------------")
    joblib.dump(clf, 'pkl/model.gz', protocol=2, compress=3)
    if s3dump:
        if verbose_flag:
            print("Uploading model file to 's3://hh-model-training-bucket/pickles/model.gz'")
        s3_client.upload_file('pkl/model.gz', 'hh-model-training-bucket', 'pickles/model.gz')

    if verbose_flag:
        print("Writing ngram word vectorizer to file at 'pkl/wordvect.gz'--")
    joblib.dump(word_vectorizer, 'pkl/wordvect.gz', protocol=2, compress=3)
    if s3dump:
        if verbose_flag:
            print("Uploading wordvect file to 's3://hh-model-training-bucket/pickles/wordvect.gz'")
        s3_client.upload_file('pkl/wordvect.gz', 'hh-model-training-bucket', 'pickles/wordvect.gz')

    if verbose_flag:
        print("Writing char ngram vectorizer to file at 'pkl/charvect.gz'--")
    joblib.dump(char_vectorizer, 'pkl/charvect.gz', protocol=2, compress=3)
    if s3dump:
        if verbose_flag:
            print("Uploading char vect file to 's3://hh-model-training-bucket/pickles/charvect.gz'")
        s3_client.upload_file('pkl/charvect.gz', 'hh-model-training-bucket', 'pickles/charvect.gz')

    if verbose_flag:
        print("Writing feature selector to file at 'pkl/select.gz'---------")
    joblib.dump(selector, 'pkl/select.gz', protocol=2, compress=3)
    if s3dump:
        if verbose_flag:
            print("Uploading chi^2 feature selector file to 's3://hh-model-training-bucket/pickles/select.gz'")
        s3_client.upload_file('pkl/select.gz', 'hh-model-training-bucket', 'pickles/select.gz')

    if verbose_flag:
        print("Writing VADER sentiment analyzer at 'pkl/sent.gz'-----------")
    joblib.dump(sid, 'pkl/sent.gz', protocol=2, compress=3)
    if s3dump:
        if verbose_flag:
            print("Uploading VADER sentiment analyzer file to 's3://hh-model-trainig-bucket/pickles/sent.gz'")
        s3_client.upload_file('pkl/sent.gz', 'hh-model-training-bucket', 'pickles/sent.gz')

def evaluate_model(target_true,target_predicted, verbose_flag):
    print("-----------------------Evaluation---------------------------")
    print(classification_report(target_true,target_predicted))
    print("The accuracy score is {:.2%}".format(accuracy_score(target_true,target_predicted)))
    if verbose_flag:
        cm = confusion_matrix(target_true,target_predicted)
        np.set_printoptions(precision=2)
        print('Confusion matrix, without normalization')
        print(cm)
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print('Normalized confusion matrix')
        print(cm_normalized)
        print("\n\n")
    return accuracy_score(target_true, target_predicted)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, action="store", help="Path to the training data or S3 to load from s3", required = True)
    parser.add_argument("--eval", type=str, action="store", help="Evaluate with cross-validation or train on whole data? True/False", required=True)
    parser.add_argument("--s3dump", type=str, action="store", help="Upload pickled file to s3 - True/False", default='False')
    parser.add_argument("--verbose", type=str, action="store", help="Verbose flag? True/False", default='True')
    parser.add_argument("--n_trees", type=int, action="store",help="Number of trees to use in Random Forest", default=200)
    parser.add_argument("--threshold", type=float, action="store",help="Probability lower-bound for tagging as harassment", default=0.41)
    parser.add_argument("--n_folds", type=int, action="store", help="Number of folds to cross-validate with", default=1)
    parser.add_argument("--chi2_denom", type=float, action="store",help="Denominator to use when selecting features with chi-2; Ie: if 100 features, denominator 20, 100/20 = 5 features extracted", default=10)
    args = parser.parse_args()

    print("\n\n")
    print("------------------------------------------------------------")
    print("Training model with data from: " + args.data)
    print("------------------------------------------------------------")
    train(args.data, args.eval=="True", args.verbose =="True", args.n_trees, args.threshold, args.n_folds, args.s3dump=="True", args.chi2_denom)
    print("------------------------All Done----------------------------")
