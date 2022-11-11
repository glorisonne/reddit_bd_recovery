import pandas as pd
import sys
import re
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config as c

# read spacy output and concatenate texts to tokenised version
def read_posts(posts_file_spacy):
    if posts_file_spacy.endswith(".csv"):
        posts = pd.read_csv(posts_file_spacy, keep_default_na=False, na_values=[])
    else:
        posts = pd.read_pickle(posts_file_spacy)
    # posts["lemma"].fillna("", inplace=True)
    # posts.lemma = posts.lemma.to_string()
    tokenised_posts = posts.groupby("post_id")["lemma"].apply(lambda x: " ".join(x)).reset_index(). \
        rename(columns={"lemma": "text"})
    # lowercase all posts
    tokenised_posts["text"] = tokenised_posts.text.str.lower()

    # test posts
    # tokenised_posts = pd.DataFrame(data={'post_id': [1, 2, 3], 'text': ["Mental health awareness week today !", "Just a test",
    #                                                                 "You will follow through ."]})
    # print(tokenised_posts)
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

def score_posts(posts, terms_file, text_col):
    vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split())

    # test posts
    # posts = pd.DataFrame(data={'post_id': [1, 2, 3], 'text': ["mental_health_awareness week today !", "today a test",
    #                                                                 "you will follow_through ."]})
    post_vectors = to_tfidf(posts[text_col], vectorizer)
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

##### main ####

posts_file = c.data_local + "posts_bd_spacy.csv"

#posts_file = sys.argv[1]
PR_terms_file = c.data_local + "PR_terms.csv"

text_col = "text_with_phrases"
process_spacy_output = True

filename = posts_file.split(".")[0]

# identify multiword phrases in lemmatised posts
if process_spacy_output:
    tokenised_posts = identify_PR_phrases(read_posts(posts_file), PR_terms_file)
    print("Concatenated lemmas of %d posts" %len(tokenised_posts))
    tokenised_posts_file = filename + "_phrases.pkl"
    print("Writing posts to %s" %tokenised_posts_file)
    tokenised_posts.to_pickle(tokenised_posts_file)

# already concatenated spacy lemmas
else:
    if posts_file.endswith(".csv"):
        tokenised_posts = pd.read_csv(posts_file, keep_default_na=False, na_values=[])
    else:
        tokenised_posts = pd.read_pickle(posts_file)

posts_PR_scored = score_posts(tokenised_posts, PR_terms_file, text_col)
print("Finished scoring, writing to %s" %(filename + "_PR_scored.csv"))
posts_PR_scored.sort_values(by="PR", ascending=False).to_csv(filename + "_PR_scored.csv")