import pandas as pd
import sys

post_id_mapping = pd.read_csv("/mnt/dhr/datasets/reddit-bipolar-diagnosis/posts/post_id_mapping.csv")
post_id_map = dict(zip(post_id_mapping.original_id, post_id_mapping.id))

fname = sys.argv[1] # "posts_users.pkl"

fname_base = fname.split(".")[0]
fname_type = fname.split(".")[1]

print(fname_base, fname_type)

if fname_type == "pkl":
    posts = pd.read_pickle(fname)
elif fname_type == "csv":
    posts = pd.pread_csv(fname)

posts["id"] = posts.id.map(post_id_map)

posts.to_csv(fname_base + ".csv", index=False)