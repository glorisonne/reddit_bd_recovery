\echo "Posts that mention *recover*"

CREATE VIEW recovery_posts AS
select posts.id, texts.text, posts.user_id, users.name, posts.subreddit_name, posts.created_at, posts.lang,
 posts.text_wordcount
from posts_meta posts, posts_text texts, reddit_users users
where posts.id = texts.id AND
	  posts.user_id = users.id AND
	  posts.lang = "en" AND
LOWER(texts.text) LIKE '%recover%'; -- use "LOWER" on the text to ignore the case '(R|r)ecovery'

\copy (SELECT id, text FROM recovery_posts) to 'data/posts_recover_text.csv' csv delimiter ',' header;

\copy (SELECT id, user_id, name, subreddit_name, created_at, lang, text_wordcount FROM recovery_posts) to
 'data/posts_recover_meta.csv' csv delimiter ';' header;