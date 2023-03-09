# -*- coding: utf-8 -*-

import pandas as pd
import sys

import config as c

def select_posts(post_ids_file):
    post_ids = pd.read_csv("post_ids/" + post_ids_file)
    print("Read in ids of %d posts" %len(post_ids))

    posts_text = pd.read_csv(c.data + "posts_text.csv", nrows=10000000)
    posts = posts_text[posts_text.id.isin(post_ids.id)]
    posts_text_1 = pd.read_csv(c.data + "posts_text.csv", skiprows=10000000, header=None, names=["id", "text"])
    posts_text_1 = posts_text_1[posts_text_1.id.isin(post_ids.id)]

    posts = pd.concat([posts, posts_text_1])

    del(posts_text_1)

    posts_meta = pd.read_csv(c.data + "posts_meta.csv")

    posts = posts.merge(posts_meta, left_on="id", right_on="id", how="left")

    print("Selected %d posts from %d ids" %(len(posts), len(post_ids)))

    # remove "post_ids" from filename
    posts.to_csv(c.data + "_".join(post_ids_file.split("_")[:-2])+ ".csv", index=False)

    return posts

if __name__ == '__main__':
    post_ids_file = sys.argv[1]
    select_posts(post_ids_file)