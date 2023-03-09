# -*- coding: utf-8 -*-

# tokenise + lemmatise posts with spacy

import sys
import spacy
import pandas as pd

import config as c

def nlp_preprocess_posts(fname):
    posts = pd.read_csv(fname, usecols=["id", "text"])

    # expect 0 here
    print("%d posts do not have a text" %len(posts[posts.text.isna()]))
    posts["text"].fillna("", inplace=True)

    nlp = spacy.load('en_core_web_sm')
    headers = ['post_id', 'sentence_id', 'token_id', 'text', 'lemma', 'pos', 'tag', 'dep', 'shape', 'is_alpha', 'is_stop']

    processed_posts = []
    for id, text in zip(posts["id"], posts["text"]):
        param = []
        # spacy sentence segmentation: https://spacy.io/usage/linguistic-features#sbd
        sentences = nlp(text).sents
        for s_id, sentence in enumerate(sentences):
            for t_id, token in enumerate(sentence):
                param.append([id, s_id, t_id, token.text, token.lemma_, token.pos_,
                  token.tag_, token.dep_, token.shape_,
                  token.is_alpha, token.is_stop])

        processed_posts.extend(param)

    # print(processed_posts)
    df = pd.DataFrame(processed_posts)
    # post id is same for every token in post
    # token id starts with 0 for every post
    df.columns = headers
    df.to_csv(fname.split(".")[0] + "_spacy.csv")

if __name__ == '__main__':
    posts_file = sys.argv[1] # c.data + "posts_bd.csv"
    nlp_preprocess_posts(posts_file)
