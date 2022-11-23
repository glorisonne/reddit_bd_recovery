import pandas as pd
import os
import shutil

import config as c

posts = pd.read_csv(c.data_local + "posts_bd_PR_scored.csv", keep_default_na=False, na_values=[])

posts = posts[posts.text_wordcount > 93]
posts.drop_duplicates(subset=["text", "user_id"], keep = "last", inplace=True)

PR = posts[posts.PR > 0.025]
print("PR-BD Corpus:\nPosts: %d\nWords: %d\nUsers: %d" %(len(PR), PR.text_wordcount.sum(), PR.user_id.nunique()))

not_PR = posts[posts.PR < 0.013]
print("Reference Corpus:\nPosts: %d\nWords: %d\nUsers: %d" %(len(not_PR), not_PR.text_wordcount.sum(), not_PR.user_id.nunique()))

def write_corpora(PR, not_PR):
    # important! Need to remove corpus folder with individual files for user if re-creating the corpus,
    # otherwise files of users that were in a previous corpus version but not in the current one remain in the folder
    PR_corpus_dir = c.data_local + "/PR-BD_corpus/"
    # removes the directory if it exists
    shutil.rmtree(PR_corpus_dir, ignore_errors=True)
    os.makedirs(PR_corpus_dir)

    PR.to_csv(c.data_local + "PR-BD_Corpus.csv")

    # .txt file format for LancsBox - only the texts
    with open(c.data_local + "PR-BD_Corpus.txt", "w") as f:
        f.write("\n".join(PR.text.tolist()))

    # write one file per user to calculate dispersion in LancsBox
    users = PR.groupby("user_id")
    for user_id, posts in users:
        with open(PR_corpus_dir + "%s.txt" %user_id, "w") as f:
            f.write("\n".join(posts.text.tolist()))

    not_PR.to_csv(c.data_local + "Reference_Corpus.csv")

    # .txt file format for LancsBox - only the texts
    with open(c.data_local + "Reference_Corpus.txt", "w") as f:
        f.write("\n".join(not_PR.text.tolist()))