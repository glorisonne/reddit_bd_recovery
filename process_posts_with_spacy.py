# tokenise + lemmatise posts with spacy

import spacy
import pandas as pd

import sys

def nlp_preprocess_posts(fname):
    posts =  pd.read_csv(fname, usecols=["id", "text"])

    # expect 0 here
    print("%d posts do not have a text" %len(posts[posts.text.isna()]))

    posts["text"].fillna("", inplace=True)

    nlp = spacy.load('en_core_web_sm')
    headers = ['post_id', 'sentence_id', 'token_id', 'text', 'lemma', 'pos', 'tag', 'dep', 'shape', 'is_alpha', 'is_stop']
    batch_size = 250000

    # clear after every batch written to file
    processed_posts = []
    # fill up until the end
    # all_processed_posts = []
    counter = 0
    batch = 0
    for id, text in zip(posts["id"], posts["text"]):
        param = []
        try:
            # spacy sentence segmentation: https://spacy.io/usage/linguistic-features#sbd
            sentences = nlp(text).sents
            for s_id, sentence in enumerate(sentences):
                for t_id, token in enumerate(sentence):
                    param.append([id, s_id, t_id, token.text, token.lemma_, token.pos_,
                      token.tag_, token.dep_, token.shape_,
                      token.is_alpha, token.is_stop])

            #param = [[id, i, token.text, token.lemma_, token.pos_,
            #          token.tag_, token.dep_, token.shape_,
            #          token.is_alpha, token.is_stop] for i, token in enumerate(nlp(text))]
        # some posts don't have a text - are nan - catch these here - solved by "fillna("") above
        except:
            print(id, text)

        # print(param)
        processed_posts.extend(param)
        # all_processed_posts.extend(param)

        counter += 1
        if counter % batch_size == 0:
            print("Processed %d out of %d posts" %(counter, len(posts)))
            df = pd.DataFrame(processed_posts)
            # post id is same for every token in post
            # token id starts with 0 for every post
            df.columns = headers
            df.to_csv(fname + "_spacy_%d" %batch)
            processed_posts = []
            batch += 1

    # print(processed_posts)
    df = pd.DataFrame(processed_posts)
    # post id is same for every token in post
    # token id starts with 0 for every post
    df.columns = headers
    df.to_csv(fname + "_spacy_%d" %batch)

if __name__ == '__main__':
    posts_file = sys.argv[1] # csv file
    nlp_preprocess_posts(posts_file)
