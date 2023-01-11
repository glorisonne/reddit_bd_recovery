# -*- coding: utf-8 -*-

import pandas as pd
import re2

import config as c


def get_dataset_stats(df):
    print("%d posts by %d users in %d subreddits, %d sentences with %d tokens" %(df.id.nunique(), df.user_id.nunique(),\
                                                                                 df.subreddit_name.nunique(),\
                                                                                 df.unique_sentence_id.nunique(),\
                                                                                 len(df)))

# Step 1: Identify all posts with at least one word that matches *recover*
# load posts_meta.csv, posts_text.csv and users.csv into an SQL database
# then run select_recover_posts.sql -> this produces data/posts_recover_text.csv and data/posts_recover_meta.csv
# post_ids/posts_contain_recover_post_ids.csv

# Step 2a: Automatically identify *recover* matches that are urls
# process with spacy to tokenize
# ToDo
# regex that matches *recover* tokens (not case-sensitive)
regex_recover = re.compile(r'(.*)recover(.*)', re.IGNORECASE)

tokens = pd.read_csv(c.data + "posts_recover_text_spacy.csv", keep_default_na=False, na_filter=False)
terms_recover = tokens[tokens.text.str.match(regex_recover)]


# source: https://gist.github.com/gruber/249502?permalink_comment_id=6465#gistcomment-6465
GRUBER_URLINTEXT_PAT = re2.compile(r'(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))')

# cannot use re2 with pandas natively https://stackoverflow.com/questions/62929644/can-i-use-re2-library-with-pandas
# ToDo check if this works
terms_recover[terms_recover.term.apply(lambda x: bool(re2.match(GRUBER_URLINTEXT_PAT, x)))].to_csv(results_folder+ "terms_recover_url.csv")

# These terms were manually examined
terms_recover[~terms_recover.term.apply(lambda x: bool(re2.match(GRUBER_URLINTEXT_PAT, x)))].to_csv(results_folder+ "terms_recover_not_url.csv")

# Step 2b: Only select posts that contain a *recover* content term
recover_content_terms = pd.read_excel("recover_terms.xlsx", sheet_name="recover_content_term")
#tokens = pd.read_csv(data_folder + "posts_recover_text_spacy.csv", keep_default_na=False, na_filter=False)
recover_content_tokens = tokens[tokens.text.str.lower().isin(recover_content_terms.term)]
posts_with_recover_content_term = recover_content_tokens.post_id.unique()

# Don't need this? -> yes, for downsampling
#posts_recover = pd.read_pickle(data_folder + "posts_recover.pkl")
# posts_recover_content_term = posts_recover[posts_recover.id.isin(posts_with_recover_content_term)]
#posts_recover_content_term.to_pickle(data_folder + "posts_recover_content_term.pkl")

tokens_posts_recover_content_terms = tokens[tokens.post_id.isin(posts_with_recover_content_term)]

#tokens_posts_recover_content_terms.to_csv(data_folder + "posts_recover_content_term_text_spacy.csv")

# Step 3: Downsample user with disproportionally many posts
#ToDo identify user by id instead of name
#posts = pd.read_pickle(data_folder + "posts_recover_content_term.pkl")
#posts_superuser = posts[posts.user_name == "coolcrosby"].sample(n=550, replace=False)
posts_downsampled = pd.concat([posts[posts.user_name != "coolcrosby"], posts_superuser])
posts_downsampled.to_pickle(data_folder + "posts_recover_content_term_superuser_downsampled.pkl")

# Step 4: Keep only English posts, replace urls with placeholder --> *recover* corpus
# r_posts = pd.read_pickle(data_folder + "posts_recover_content_term_superuser_downsampled.pkl")
r_posts = r_posts[r_posts.lang == "en"]

#ToDo OneNote "Posts that contain *recover*" (14.6.21)
# select texts with urls replaced with subURLaddress - do this on UCREL VM, then copy recover_corpus_id_text.csv over to local
# 	- Get texts for these posts with the same preprocessing as the reference corpus (replaced urls):
# 		○ Copy post ids posts_recover_content_term_superuser_downsampled_en_id.txt to /mnt/dhr/datasets/reddit-bipolar-diagnosis/recovery
# 		○ posts_text = pd.read_csv("/mnt/dhr/datasets/reddit-bipolar-diagnosis/posts/posts_id_text.csv", header=None, names=["id", "text"])
# 		○ Save with header: posts_text.to_csv("/mnt/dhr/datasets/reddit-bipolar-diagnosis/posts/posts_id_text.csv", index=False)
# 		○ corpus_ids = pd.read_csv("posts_recover_content_term_superuser_downsampled_en_id.txt")
# 		○ posts_texts[posts_texts.id.isin(corpus_ids.id)].to_csv("recover_corpus_id_text.csv", index=False)
# 	- Add the posts with subURLaddress to the pickle file: jupyter notebook "# select texts with urls replaced with subURLaddress" - posts_recover_content_term_superuser_downsampled_en.pkl
# Preprocess with spacy: /mnt/dhr/datasets/reddit-bipolar-diagnosis/recovery$ nohup python3 -u /mnt/dhr/code/social-media-data-collection/paper4-analysis/process_posts_with_spacy.py recover_corpus_id_text.csv &> spacy_recover_corpus.log &

#print(len(r_posts))
#texts = pd.read_csv(data_folder + "recover_corpus_id_text.csv")

#r_posts.drop(labels=["text"], axis=1, inplace=True)
#r_posts = r_posts.merge(texts, left_on="id", right_on="id")

#print(r_posts.columns)
#print(len(r_posts))

r_posts.to_pickle(data_folder + "posts_recover_content_term_superuser_downsampled_en.pkl")


# Random sample of 0.5% of posts for manual coding

# posts = pd.read_pickle(data_folder + "posts_recover_content_term_superuser_downsampled_en.pkl")
posts_to_code = posts.sample(frac=0.005, replace=False)

#posts_to_code = pd.read_csv(data_folder + "posts_id_recover_content_term_to_code.csv")
#posts_to_code = posts[posts.id.isin(posts_to_code.id)]

posts_spacy = pd.read_csv(data_folder + "recover_corpus_spacy.csv")
posts_spacy_to_code = posts_spacy[posts_spacy.post_id.isin(posts_to_code.id)]
posts_spacy_extra = posts_spacy[~posts_spacy.post_id.isin(posts_to_code.id)]

recovery_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "recovery"]
recover_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "recover"]
recovering_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "recovering"]
recovered_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "recovered"]
# low-frequency *recover* terms
# 6 instances --> ok
recovers_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "recovers"]
# only 3 instances
recoveries_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "recoveries"]
# only 1 instance
recoverable_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "recoverable"]
# 0 instances for unrecoverable, irrecoverable
unrecoverable_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "unrecoverable"]
irrecoverable_instances = posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == "irrecoverable"]

# upsample low-frequency *recover* terms to at least 5 instances
recoveries_instances_extra = posts_spacy_extra[posts_spacy_extra.text.str.lower() == "recoveries"].sample(n=2, replace=False)
recoverable_instances_extra = posts_spacy_extra[posts_spacy_extra.text.str.lower() == "recoverable"].sample(n=4, replace=False)
unrecoverable_instances_extra = posts_spacy_extra[posts_spacy_extra.text.str.lower() == "unrecoverable"].sample(n=5, replace=False)
irrecoverable_instances_extra = posts_spacy_extra[posts_spacy_extra.text.str.lower() == "irrecoverable"].sample(n=5, replace=False)

all_recover_instances = pd.concat([recovery_instances, recover_instances, recovering_instances, recovered_instances,
                                  recovers_instances, recoveries_instances, recoverable_instances, unrecoverable_instances,
                                  irrecoverable_instances])

# important to merge with right, because need to add posts of additionally sampled low-frequency
# recover variants to posts_spacy_to_code that are in all_recover_instances
posts_spacy_to_code = posts_spacy.merge(posts[posts.id.isin(all_recover_instances.post_id)]\
                     [["id", "subreddit_name", "text"]], left_on = "post_id", right_on="id", suffixes=("", "_full"),
                    how="right")

sentences = posts_spacy_to_code.groupby(["post_id", "sentence_id"]).text.apply(list).reset_index().rename(columns={"text": "sentence"})
sentences["sentence"] = sentences.sentence.apply(lambda s: " ".join([str(token) for token in s]))

posts_spacy_to_code = posts_spacy_to_code.merge(sentences,
                                                left_on=["post_id", "sentence_id"], right_on=["post_id", "sentence_id"])

for term in ["recovers", "recoveries", "recoverable", "unrecoverable", "irrecoverable"]:#["recovery", "recover", "recovering", "recovered"]:
    posts_spacy_to_code[posts_spacy_to_code.text.str.lower() == term]\
    [["post_id", "subreddit_name", "text", "token_id", "sentence", "text_full"]].to_csv(results_folder + "to_code_%s.csv" %term,
                                                                                        index=False)