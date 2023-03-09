# -*- coding: utf-8 -*-
import pandas as pd

import config as c
# select key lemmas from LancsBox output

# nead to read LancsBox output in as text files as they are not properly csv formatted (" not escaped)
def read_lacsbox_file(fname):
    lines = []
    with open(c.data + "%s" %fname) as f:
        # skip firs two lines
        f.readline()
        f.readline()
        for line in f:
            lines.append(line.strip().split("\t"))
    return lines

lines_LL = read_lacsbox_file("PR-BD_terms_LL.txt")
terms_LL = pd.DataFrame(lines_LL, columns=["term", "frequency", "dispersion", "frequency_ref", "dispersion_ref", "LL"])
terms_LR = pd.DataFrame(read_lacsbox_file("PR-BD_terms_LR.txt"),
                           columns=["term", "frequency_c", "dispersion_c", "frequency_ref", "dispersion_ref", "LR"])

# merge LR and LL scores
terms = terms_LL[["term", "frequency", "dispersion", "frequency_ref", "LL"]].\
                        merge(terms_LR[["term", "LR"]], left_on="term", right_on="term", how="left")

# preprocess lemmas: i|be_pron|v -> split at first "_", take only first part to remove POS, then replace | by " "
terms["lemma_pos"] = terms.term

def extract_lemma(term):
    return term.split("_")[0].replace("|", " ")

terms["term"] = terms.term.apply(extract_lemma)

# convert LancsBox statistics from str to float
for col in ["frequency", "dispersion", "frequency_ref", "LL", "LR"]:
    terms[col] = terms[col].astype(float)

key_lemmas = terms[(terms.LL > 15.13) & (terms.LR >= 1.0) & (terms.dispersion >= 5.0)]

print("Selected %d key lemmas with LL > 15.13 & LR >= 1.0 & dispersion >= 5.0" %len(key_lemmas))

terms.to_csv(c.data + "PR-BD_and_Reference Corpus_terms.csv", index=False)

key_lemmas.to_csv(c.data + "PR-BD Corpus_key_lemmas.csv", index=False)