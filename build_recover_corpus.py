#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import re
import plotly.express as px

import config as c
import select_posts_via_ids as sp
import process_posts_with_spacy as ps

# regex that matches *recover* tokens (not case-sensitive)
regex_recover = re.compile(r'(.*)recover(.*)', re.IGNORECASE)

def get_dataset_stats(df):
    print("%d posts by %d users in %d subreddits, %d sentences with %d tokens" %(df.id.nunique(), df.user_id.nunique(),\
                                                                                 df.subreddit_name.nunique(),\
                                                                                 df.sentence_id.nunique(),\
                                                                                 len(df)))

    tokens_recover = df[df.text.str.match(regex_recover)]
    terms_recover = tokens_recover.text.str.lower().value_counts().reset_index().rename(
        columns={"index": "term", "text": "frequency"})
    print("%d unique terms that match *recover*" % len(terms_recover))
    print(terms_recover[terms_recover.frequency >= 3])

def plot_posts_per_user(posts, outfile_name):
    # posts per user plot
    posts_per_user = posts.groupby("user_id").id.nunique().reset_index(). \
        rename(columns={"id": "posts (n)"}).sort_values("posts (n)", ascending=False)
    # convert id to text so the bars are not reordered on the x-axis according to the ids
    posts_per_user["user id"] = posts_per_user.user_id.astype(str)
    fig = px.bar(posts_per_user.head(n=30), x="user id", y="posts (n)", width=500)
    # need tickmode=linear to show all user ids
    fig.update_xaxes(showticklabels=True, type='category', tickmode='linear')
    # fig.show()
    print("Plot image to output/%s.png" %outfile_name)
    fig.write_image("output/%s.png" % outfile_name)

def select_tokenised_posts_via_ids(post_ids_file, tokenised_posts_file):
    post_ids_to_code = pd.read_csv("post_ids/%s" %post_ids_file)
    tokens = pd.read_csv(c.data + tokenised_posts_file, keep_default_na=False, na_filter=False)
    selected_posts = tokens[tokens.id.isin(post_ids_to_code.id)]
    selected_posts.to_csv(c.data + "_".join(post_ids_file.split("_")[:-2])+ ".csv", index=False)
    return selected_posts

def step_1():
    print("Step 1")
    # 1 Select English S-BiDD dataset posts with at least one token that matches *recover*
    # see select_recover_posts.sql
    # to skip this step, start with posts_contain_recover_post_ids.csv
    sp.select_posts("posts_contain_recover_post_ids.csv")

    # run spacy to tokenise
    ps.nlp_preprocess_posts(c.data + "posts_contain_recover.csv")

    tokens = pd.read_csv(c.data + "posts_contain_recover_spacy.csv", keep_default_na=False, na_filter=False,
                         usecols=["post_id", "sentence_id", "token_id", "text"])
    tokens.rename(columns={"post_id": "id"}, inplace=True)
    # make sentence_id unique within the dataset
    tokens["sentence_id"] = tokens.id.astype(str) + "_" + tokens.sentence_id.astype(str)
    posts = pd.read_csv(c.data + "posts_meta.csv", keep_default_na=False, na_filter=False,
                        usecols=["id", "user_id", "lang", "subreddit_name", "subreddit_type"])
    tokens = tokens.merge(posts, left_on="id", right_on="id", how="left")

    print("After Step 1:\nAll English S-BiDD dataset posts with at least one token that matches *recover*")
    get_dataset_stats(tokens)
    tokens.to_csv(c.data + "posts_contain_recover_tokenised.csv", index=False)

def step_2():
    print("Step 2")
    # 2 Select only posts that contain a *recover* content term
    recover_content_terms = pd.read_csv("exploratory_study_2/recover_content_terms.csv", keep_default_na=False, na_filter=False)
    print("Read in %d recover content terms" %len(recover_content_terms))

    tokens = pd.read_csv(c.data + "posts_contain_recover_tokenised.csv", keep_default_na=False, na_filter=False)
    recover_content_tokens = tokens[tokens.text.str.lower().isin(recover_content_terms.term.str.lower())]

    posts_with_recover_content_term = recover_content_tokens.id.unique()
    posts_contain_recover_content_term = tokens[tokens.id.isin(posts_with_recover_content_term)]

    print("After Step 2:\n After selecting only posts with at least one *recover* content term")
    get_dataset_stats(posts_contain_recover_content_term)

    plot_posts_per_user(posts_contain_recover_content_term, "posts_per_user_top30_contains_recover_content_term")

    posts_contain_recover_content_term.to_csv(c.data + "posts_contain_recover_content_term.csv", index=False)

def step_3():
    print("Step 3")
    # 3 Downsample number of posts for user with most posts
    # fix random seed for reproducibility - see here: https://stackoverflow.com/questions/52375356/is-there-a-way-to-set-random-state-for-all-pandas-function
    np.random.seed(0)

    tokens = pd.read_csv(c.data + "posts_contain_recover_content_term.csv", keep_default_na=False, na_filter=False)
    get_dataset_stats(tokens)
    posts_superuser = np.random.choice(tokens[tokens.user_id == 1629].id.unique(), size=540, replace=False)
    tokens_superuser = tokens[tokens.id.isin(posts_superuser)]
    recover_corpus = pd.concat([tokens[tokens.user_id != 1629], tokens_superuser])

    print("After Step 3\n*recover* corpus: after downsampling user with disproportionally many posts\n(Note that the "
          "corpus statistics may slightly differ from supplementary Table 4 due to random sampling.")
    get_dataset_stats(recover_corpus)

    recover_corpus.to_csv(c.data + "posts_recover_corpus_own_sampling.csv", index=False)

    recover_corpus = select_tokenised_posts_via_ids("posts_recover_corpus_post_ids.csv",
                                                   "posts_contain_recover_content_term.csv")
    print("After Step 3\n*recover* corpus as used in the paper reconstructed from the post ids")
    get_dataset_stats(recover_corpus)

    # number of posts per user
    plot_posts_per_user(recover_corpus, "posts_per_user_top30_recover_corpus")

    # subreddits with most posts in the *recover* corpus
    posts_per_subreddit = recover_corpus.groupby("subreddit_name").id.nunique().reset_index().\
        rename(columns={"id": "posts (n)"}).sort_values("posts (n)", ascending=False).head(n=10)

    posts = pd.read_csv(c.data + "posts_meta.csv", usecols=["id", "subreddit_name"])
    posts_per_subreddit_total = posts[posts.subreddit_name.isin(posts_per_subreddit.subreddit_name)].\
        groupby("subreddit_name").id.nunique().reset_index().rename(columns={"id": "posts (n)"})

    posts_per_subreddit = posts_per_subreddit.merge(posts_per_subreddit_total, left_on="subreddit_name",
                                            right_on="subreddit_name", how="left", suffixes=('_recover', '_total'))
    posts_per_subreddit["% total"] = posts_per_subreddit["posts (n)_recover"] / posts_per_subreddit["posts (n)_total"] * 100
    print(posts_per_subreddit)

def select_post_to_code():
    print("Select posts to code")
    # select posts to code
    # code for the random sampling of 0.5% of the posts + upsampling of posts to 50 posts in BD subreddits
    # and *recover* term instances to at least 5 instances not reproduced since the post distribution varies with the
    # random sampling
    posts_to_code = select_tokenised_posts_via_ids("posts_recover_corpus_to_code_post_ids.csv", "posts_recover_corpus.csv")
    print("Posts from *recover* corpus for manual coding of *recover* instances")
    get_dataset_stats(posts_to_code)

if __name__ == '__main__':
    print("Constructing *recover* corpus ...")
    step_1()
    step_2()
    step_3()
    select_post_to_code()

