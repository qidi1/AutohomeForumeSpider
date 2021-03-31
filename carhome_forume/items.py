# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from carhome_forume.AutoHome_Font import get_new_font_dict
import scrapy



def word_regular(line,temp_font=None):
    if type(line)==list:
        result=""
        for l in line:
            result+=word_regular(l)
        return result
    line=str(line)
    return line
def word_format(line,font_dict):
    
    content=line.encode('unicode_escape')
    for key, value in font_dict.items():
        new_key = r"\u" + key[3:].lower()
        content=content.replace(str.encode(new_key), str.encode(value))
        line=content.decode('unicode_escape')
    line.replace(" ", "").replace("\n", "").replace("\xa0", "")
    return line

class BBSItem(scrapy.Item):
    bbs_id =scrapy.Field()
    bbs_name=scrapy.Field()
class TopicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    bbs_id=scrapy.Field()
    title=scrapy.Field()
    content=scrapy.Field()
    topic_id=scrapy.Field()
class CommentItem(scrapy.Item):
    content=scrapy.Field()
    topic_id=scrapy.Field()
    comment_id=scrapy.Field()
class ReplyCommentItem(scrapy.Item):
    content=scrapy.Field()
    reply_comment_id=scrapy.Field()
    comment_id=scrapy.Field()
