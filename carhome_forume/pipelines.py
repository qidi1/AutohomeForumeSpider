# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from carhome_forume.items import BBSItem, CommentItem, ReplyCommentItem, TopicItem
import pymysql
class CarhomeForumePipeline:
    def process_item(self, item, spider):
        return item
class CommentPipeline(object):
    def open_spider(self,spider):
        db = spider.settings.get('MYSQL_DB_NAME')
        host = spider.settings.get('MYSQL_HOST')
        port = spider.settings.get('MYSQL_PORT')
        user = spider.settings.get('MYSQL_USER')
        passwd = spider.settings.get('MYSQL_PASSWORD')
        self.db_conn =pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8mb4')
        self.db_cur = self.db_conn.cursor()
        self.call={
                   BBSItem:self.insert_BBS,
                   TopicItem:self.insert_topic,
                   CommentItem:self.insert_comment,
                   ReplyCommentItem:self.insert_replyComment
                }
    def process_item(self,item,spider):
        self.call[type(item)](item)
        self.db_conn.commit()
        return item
    def insert_BBS(self,item):
        values=(
            item['bbs_id'][0],
            item['bbs_name'][0]
        )
        sql = 'INSERT INTO bbs_ (bbsId_,bbsName_) VALUES(%s,%s)'
        self.db_cur.execute(sql, values)
    def insert_topic(self,item):
        values=(
            item['bbs_id'][0],
            item['topic_id'][0],
            item['title'][0],
            item['content'][0]
        )
        sql = 'INSERT INTO topic_ (bbsId_,topicId_,title_,content_) VALUES(%s,%s,%s,%s)'
        self.db_cur.execute(sql, values)

    def insert_comment(self,item):
        values=(
            item['topic_id'][0],
            item['comment_id'][0],
            item['content'][0]
        )
        sql = 'INSERT INTO comment_ (topicId_,commentId_,content_) VALUES(%s,%s,%s)'
        self.db_cur.execute(sql, values)

    def insert_replyComment(self,item):
        values=(
            item['reply_comment_id'][0],
            item['comment_id'][0],
            item['content'][0]
        )
        sql = 'INSERT INTO replyComment_ (replyCommentId_,commentId_,content_)VALUES(%s,%s,%s)'
        self.db_cur.execute(sql, values)

    def close_spider(self,spider):
       self.db_conn.commit()
       self.db_conn.close()
