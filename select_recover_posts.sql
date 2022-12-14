\echo "Posts that mention *recover*"
/*
DROP VIEW recovery_posts;
CREATE VIEW recovery_posts AS
select posts.id, posts.text, posts.user_id, users.name, posts.subreddit_name, posts.created_at, posts.lang,
 posts.text_wordcount
from reddit_posts posts, reddit_dataset_post_ids dataset_posts, reddit_users users
where dataset_posts.id = posts.id AND
	  posts.user_id = users.id AND
LOWER(posts.text) LIKE '%recover%'; -- use "LOWER" on the text to ignore the case '(R|r)ecovery'
*/
\copy (SELECT id, text FROM recovery_posts) to 'data/posts_recover_text.csv' csv delimiter ',' header;

\copy (SELECT id, user_id, name, subreddit_name, created_at, lang, text_wordcount FROM recovery_posts) to
 'data/posts_recover_meta.csv' csv delimiter ';' header;