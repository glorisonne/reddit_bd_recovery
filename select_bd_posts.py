# -*- coding: utf-8 -*-
import pandas as pd

import config as c

# 1) Select posts in BD subreddits
# subreddit_type based on categorisation here: https://github.com/glorisonne/reddit_bd_mood_posting_mh/blob/main/data/subreddit_topics.csv
# (Fourth level = "bipolar")
posts = pd.read_csv(c.data + "posts_meta.csv", usecols=["id", "user_id", "subreddit_name", "text_wordcount", "mentions_bd",
                                                        "subreddit_type"])

# After completion of the research we detected a bug in this step: the bipolar-subreddits.txt list of BD subreddits
# used to select posts in BD subreddits contains three subreddits where the upper-/lowercasing differs from
# the casing in posts_meta.csv:
# bipolarSOs -> BipolarSOs, bipolarResources -> BipolarResources, bipolarpeersupport -> BipolarPeerSupport
# because the matching of subreddit names was case-sensitive, posts in these three subreddits were not matched
# for full reproducibility, this code uses the original (incomplete) matching
# to match all posts in a BD subreddit in the S-BiDD dataset, use the following command instead of line 24:
# posts = posts[posts.subreddit_type == "bd"]
# the subreddit_type column was populated using case-insensitive matching
# ToDo: mention subreddit_topics.csv shared for paper 3 and that it doesn't contain casing mistakes?
# ToDo mention how much of a difference correcting this bug makes?
bd_subreddits = pd.read_csv(c.data + "bipolar-subreddits.txt", header=None, names=["subreddit"]).squeeze(axis=0)

posts = posts[posts.subreddit_name.isin(bd_subreddits.subreddit)] #posts = posts[posts.subreddit_type == "bd"]
print("Posts in BD subreddits:\nPosts: %d\nWords: %d\nUsers: %d" %(len(posts), posts.text_wordcount.sum(),
                                                                    posts.user_id.nunique()))

# 2) Select posts that mention BD
# the column mentions_bd was populated using the list of synonyms for BD shared here:
# https://github.com/glorisonne/reddit_bd_user_characteristics/blob/master/disclosure-patterns/condition-terms/bipolar-filter-terms.txt
# see for details of how this list was created, see reference [2] in README.md
posts = posts[posts.mentions_bd]
print("Posts that mention BD:\nPosts: %d\nWords: %d\nUsers: %d" %(len(posts), posts.text_wordcount.sum(),
                                                                    posts.user_id.nunique()))

# add post texts - read post_text csv in two batches as the file is very large and the code might therefore fail on
# machines with less RAM
posts_text_0 = pd.read_csv(c.data + "posts_text.csv", nrows=10000000)
posts_text_0 = posts_text_0[posts_text_0.id.isin(posts.id)]
posts_text_1 = pd.read_csv(c.data + "posts_text.csv", skiprows=10000000, header=None, names=["id", "text"])
posts_text_1 = posts_text_1[posts_text_1.id.isin(posts.id)]
posts_text = pd.concat([posts_text_0, posts_text_1])

posts = posts.merge(posts_text, left_on="id", right_on="id")
# free up RAM again
del(posts_text_0, posts_text_1, posts_text)

posts.to_csv(c.data + "posts_bd.csv")