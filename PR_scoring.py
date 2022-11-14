import pandas as pd
import sys
import re
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config as c

# read spacy output and concatenate texts to tokenised version
def read_posts(posts_file_spacy):
    posts = pd.read_csv(posts_file_spacy, keep_default_na=False, na_values=[])

    # posts["lemma"].fillna("", inplace=True)
    # posts.lemma = posts.lemma.to_string()
    tokenised_posts = posts.groupby("post_id")["lemma"].apply(lambda x: " ".join(x)).reset_index(). \
        rename(columns={"lemma": "text"})
    # lowercase all posts
    tokenised_posts["text"] = tokenised_posts.text.str.lower()

    return tokenised_posts

# identify PR phrases in lemmatised posts
def identify_PR_phrases(tokenised_posts, PR_terms):
    PR_terms = pd.read_csv(PR_terms_file)

    def replace_phrases(text, terms):
        for term, replacement in zip(terms.term, terms.replacement):
            # only match single terms, do not need re.IGNORECASE because lowercased both the post and the terms
            text = re.sub(r"\b%s(?!\S)" % re.escape(term), replacement, text)
        # print(text)
        return text
    tokenised_posts["text_with_phrases"] = tokenised_posts.text.apply(lambda x: replace_phrases(x, PR_terms))
    return tokenised_posts

def process_spacy_output(posts_file, PR_terms_file, outfile):
    tokenised_posts = identify_PR_phrases(read_posts(posts_file), PR_terms_file)
    print("Concatenated lemmas and identified PR term phrases in %d posts\nNow writing to %s" % (len(tokenised_posts), outfile))
    tokenised_posts.to_csv(outfile)
    return tokenised_posts

def to_tfidf(series, vectorizer):
    # print(df["lemma"])

    # default analyzer splits at space and only retains tokens of at least 2 characters
    # instead use nltk tweet tokenizer

    vectors = vectorizer.fit_transform(series)
    print("Number of posts x vocabulary size", vectors.shape)
    # tuple (post_id, vocabulary_item_id) - score,
    # sparse representation: only lists for each post the vocabulary items that appear (where score is > 0)
    # print(vectors)

    # feature_names = vectorizer.get_feature_names()
    # print("Vocabulary size: %d" %len(feature_names))

    # dense matrices too large
    # dense = vectors.todense()
    # denselist = dense.tolist()
    # df_tfidf = pd.DataFrame(denselist, columns=feature_names)
    # print(df_tfidf)
    # return df_tfidf

    return vectors

def score_posts(posts, terms_file):
    vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split())

    post_vectors = to_tfidf(posts["text_with_phrases"], vectorizer)
    print("Vectorised posts to shape", post_vectors.shape)

    PR_terms = pd.read_csv(terms_file, usecols=["replacement"])
    # print(PR_terms)

    # I want single score for all PR terms, so need to concate the terms into one string
    PR_vector = vectorizer.transform([" ".join(PR_terms.replacement.to_list())])
    print("Created term vector with shape", PR_vector.shape)
    # print("PR vector\n", PR_vector)

    post_PR_scores = cosine_similarity(PR_vector, post_vectors)
    print("Calculated cosine similarity between posts and term vector")
    # print("post_PR_scores\n", post_PR_scores)

    # get dataframe with post indices as rows and PR scores as columns
    post_PR_scores_df = pd.DataFrame(post_PR_scores.T, columns=["PR"])
    print(post_PR_scores_df.describe())
    print("%d posts have non-zero PR score" %len(post_PR_scores_df[post_PR_scores_df.PR > 0]))

    # add in the texts
    posts_PR_scored = pd.concat([posts, post_PR_scores_df], axis=1)
    return posts_PR_scored

if __name__ == '__main__':
    posts_file = c.data_local + "posts_bd_spacy.csv"
    PR_terms_file = c.data_local + "PR_terms.csv"
    filename_posts_with_PR_phrases = c.data_local + "posts_bd_spacy_phrases.csv"
    filename_posts_scored = c.data_local + "posts_bd_PR_scored.csv"

    # identify multiword phrases in lemmatised posts, write to filename_posts_with_PR_phrases
    tokenised_posts = process_spacy_output(posts_file, PR_terms_file, filename_posts_with_PR_phrases)

    # already concatenated spacy lemmas
    # tokenised_posts = pd.read_csv(filename_posts_with_PR_phrases, keep_default_na=False, na_values=[])

    posts_PR_scored = score_posts(tokenised_posts, PR_terms_file)
    print("Finished scoring, writing to %s" %(filename_posts_scored))
    posts_PR_scored.sort_values(by="PR", ascending=False).to_csv(filename_posts_scored)