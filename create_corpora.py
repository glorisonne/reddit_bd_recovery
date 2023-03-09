# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os
import shutil

import config as c
from select_posts_via_ids import select_posts

mode = sys.argv[1]

def write_corpora(PR, not_PR, cols_to_write):
    # important! Need to remove corpus folder with individual files for user if re-creating the corpus,
    # otherwise files of users that were in a previous corpus version but not in the current one remain in the folder
    PR_corpus_dir = c.data + "/PR-BD_corpus/"
    # removes the directory if it exists
    shutil.rmtree(PR_corpus_dir, ignore_errors=True)
    os.makedirs(PR_corpus_dir)

    PR[cols_to_write].to_csv(
        c.data + "PR-BD_Corpus.csv", index=False)

    # .txt file format for LancsBox - only the texts
    with open(c.data + "PR-BD_Corpus.txt", "w") as f:
        f.write("\n".join(PR.text.tolist()))

    # write one file per user to calculate dispersion in LancsBox
    users = PR.groupby("user_id")
    for user_id, posts in users:
        with open(PR_corpus_dir + "%s.txt" %user_id, "w") as f:
            f.write("\n".join(posts.text.tolist()))

    not_PR[cols_to_write].to_csv(
        c.data + "Reference_Corpus.csv", index=False)

    # .txt file format for LancsBox - only the texts
    with open(c.data + "Reference_Corpus.txt", "w") as f:
        f.write("\n".join(not_PR.text.tolist()))

if mode == "select":
    posts = pd.read_csv(c.data + "posts_bd_PR_scored.csv", keep_default_na=False, na_values=[])

    # 3) Select posts with at least 94 words, remove duplicates (same text by same user)
    posts = posts[posts.text_wordcount > 93]
    posts.drop_duplicates(subset=["text", "user_id"], keep = "last", inplace=True)
    print("Posts with at least 94 words, duplicates removed:\nPosts: %d\nWords: %d\nUsers: %d" %(len(posts), posts.text_wordcount.sum(),
                                                                       posts.user_id.nunique()))

    # 4.1) Select posts for PR-BD corpus
    PR = posts[posts.PR > 0.025]
    print("PR-BD Corpus:\nPosts: %d\nWords: %d\nUsers: %d" %(len(PR), PR.text_wordcount.sum(), PR.user_id.nunique()))

    # 4.2) Select posts for Reference corpus
    not_PR = posts[posts.PR < 0.013]
    print("Reference Corpus:\nPosts: %d\nWords: %d\nUsers: %d" %(len(not_PR), not_PR.text_wordcount.sum(), not_PR.user_id.nunique()))

    write_corpora(PR, not_PR,
                  cols_to_write=['id', 'user_id', 'subreddit_name', 'text_wordcount', 'text', 'text_with_phrases', 'PR'])

elif mode == "ids":
    select_posts("PR-BD_Corpus_post_ids.csv")
    select_posts("Reference_Corpus_post_ids.csv")
    PR = pd.read_csv(c.data + "PR-BD_Corpus.csv")
    PR_scores = pd.read_csv(c.post_ids + "PR-BD_Corpus_post_ids.csv")
    PR = PR.merge(PR_scores, left_on="id", right_on="id")
    not_PR = pd.read_csv(c.data + "Reference_Corpus.csv")
    PR_scores = pd.read_csv(c.post_ids + "Reference_Corpus_post_ids.csv")
    not_PR = not_PR.merge(PR_scores, left_on="id", right_on="id")

    write_corpora(PR, not_PR, cols_to_write=['id', 'user_id', 'subreddit_name', 'text_wordcount', 'text', 'PR'])