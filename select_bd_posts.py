# 1) posts in BD subreddits
# subreddit_type based on categorisation here: https://github.com/glorisonne/reddit_bd_mood_posting_mh/blob/main/data/subreddit_topics.csv
# (Fourth level = "bipolar")
#posts = pd.read_csv(c.data + "posts_meta.csv", usecols=["id", "user_id", "subreddit_name", "text_wordcount", "mentions_bd",
#                                                        "subreddit_type"])

#posts = posts[posts.subreddit_type == "bd"]
#print("Posts in BD subreddits:\nPosts: %d\nWords: %d\nUsers: %d" %(len(posts), posts.text_wordcount.sum(),
#                                                                    posts.user_id.nunique()))

# 2) posts that mention BD -- refer to BD terms list https://github.com/glorisonne/reddit_bd_user_characteristics/blob/master/disclosure-patterns/condition-terms/bipolar-filter-terms.txt
#posts = posts[posts.mentions_bd]
#print("Posts that mention BD:\nPosts: %d\nWords: %d\nUsers: %d" %(len(posts), posts.text_wordcount.sum(),
#                                                                    posts.user_id.nunique()))

# 3) posts with at least 94 words, duplicates (same text by same user) removed
#posts = posts[posts.text_wordcount > 93]

# add post texts - read post_text csv in two batches as the file is very large and the code migth therefore fail on
# machines with less RAM
#posts_text_0 = pd.read_csv(c.data + "posts_text.csv", nrows=10000000)
#posts_text_0 = posts_text_0[posts_text_0.id.isin(posts.id)]
#posts_text_1 = pd.read_csv(c.data + "posts_text.csv", skiprows=10000000, header=None, names=["id", "text"])
#posts_text_1 = posts_text_1[posts_text_1.id.isin(posts.id)]
#posts_text = pd.concat([posts_text_0, posts_text_1])

#posts = posts.merge(posts_text, left_on="id", right_on="id")

#del(posts_text_0, posts_text_1, posts_text)

#posts.drop_duplicates(subset=["text", "user_id"], keep = "last", inplace=True)
#print("Posts with at least 94 words, duplicates removed:\nPosts: %d\nWords: %d\nUsers: %d" %(len(posts), posts.text_wordcount.sum(),
#                                                                    posts.user_id.nunique()))
posts.to_csv(c.data_local + "posts_bd.csv")