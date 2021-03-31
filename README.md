# AutohomeForumeSpider
爬取了汽车之家的论坛评论数据；使用docker配置的数据库进行连接，需要连接自己的数据库请更改setting.py，

1.bbs_表
  | 字段名      | 字段类型        | 字段说明 |
  |----------|-------------|------|
  | bbsId_   | Int         | 论坛id |
  | bbsName_ | Varchar(40) | 论坛名称 |
  
2.topic_表

| 字段名      | 字段类型         | 字段说明 |
|----------|--------------|------|
| bbsId_ | Int          | 论坛id |
| topicId_ Int          | 帖子id |
| title_   | Varchar(40)  | 帖子标题 |
| content_ | Varchar(250) | 帖子内容 |

3. comment_表

| 字段名       | 字段类型         | 字段说明      |
|-----------|--------------|-----------|
| topicId_| Int          | 评论回复的帖子id |
| comentId_ | Int          | 评论id      |
| content   | Varchar(250) | 回复内容      |

4. replyComment_表

| 字段名             | 字段类型         | 字段说明      |
|-----------------|--------------|-----------|
| replyCommentId_ | Int          | 评论回复的评论id |
| coment_id       | Int          | 评论id      |
| content         | Varchar(250) | 回复内容      |
