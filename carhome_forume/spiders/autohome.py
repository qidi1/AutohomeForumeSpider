from carhome_forume.AutoHome_Font import get_new_font_dict
import os
import re
from carhome_forume.items import BBSItem, CommentItem, ReplyCommentItem, TopicItem, word_format, word_regular
from scrapy import spiders
import json
import scrapy
from scrapy.loader import ItemLoader
import requests
import random
class AutohomeSpider(spiders.Spider):
    ttfPath = "./carhome_forume/font/temp"
    standPath="./carhome_forume/font/standardFont.ttf"
    name = 'autohome'
    # the temp file name are using
    using_name_set={'0'}
    start_urls=[
        # "https://club.autohome.com.cn/frontapi/bbs/getSeriesByLetter?firstLetter"
    ]
    base_url="https://club.autohome.com.cn/frontapi/data/page/club_get_topics_list?page_num=^&page_size=100&club_bbs_type=c&club_bbs_id=*&club_order_type=1"
    comment_url="https://club.autohome.com.cn/frontapi/comment/getcommentwithpagination?"
    def start_requests(self):
    #   yield scrapy.Request(url="https://club.autohome.com.cn/frontapi/comment/getcommentwithpagination?topicId=9518685&replyId=1345277286&pageIndex=1&pageSize=10",callback=self.comment_comment_parse,meta={'comment_id':121})
    #    yield scrapy.Request(url="https://club.autohome.com.cn/bbs/thread/3faa9b1329a1a50b/95188254-1.html",callback=self.comment_parse,meta={'bbs_id':121})
       yield scrapy.Request(url="https://club.autohome.com.cn/bbs/thread/24b5a3af21113b67/83773698-1.html",callback=self.comment_parse,meta={'bbs_id':121})
    #    yield scrapy.Request(url="https://club.autohome.com.cn/",callback=self.hot_club_parse)

    #  analyse forume id from start urls
    def hot_club_parse(self, responses):
        bbs_list=responses.css("div#tab-hot-cont li")
        for bbs in bbs_list:
            loader=ItemLoader(BBSItem(),bbs)
            loader.add_css("bbs_name","a::attr(title)")
            bbs_url=bbs.css("a::attr(href)").extract_first()
            if bbs_url==None:
                break
            bbs_url="http://"+bbs_url
            bbs_id=int(re.findall(r"\d+\.?\d+",bbs_url.split(r'/')[-1])[0])
            loader.add_value("bbs_id",bbs_id)
            yield loader.load_item()
            url=self.set_url(bbs_id,1)
            yield scrapy.Request(url, callback=self.bbs_parse,meta={'bbs_id':bbs_id,'page_num':1})

    def all_club_parse(self, response):
        rs=json.loads(response.text)
        letter_list=rs["result"]
        for letter in letter_list:
            brand_list=letter["bbsBrand"]
            for brand in brand_list:
                for bbs in brand["bbsList"]:
                    loader=ItemLoader(BBSItem())
                    loader.add_value("bbs_id",bbs["bbsId"])
                    loader.add_value("bbs_name",bbs["bbsName"])
                    yield loader.load_item()
                    url=self.set_url(bbs["bbsId"],1)
                    yield scrapy.Request(url, callback=self.bbs_parse,meta={'bbs_id':bbs["bbsId"],'page_num':1})

    # Extract the URL of forum post 
    def bbs_parse(self,response):
        rs=json.loads(response.text)
        # if out of limit return
        if response.meta["page_num"]>100:
            return 
        if "result" not in rs:
            return
        items=rs["result"]["items"]
        url=self.set_url(response.meta["bbs_id"],response.meta["page_num"]+1)
        for item in items:
            yield scrapy.Request(url=item["pc_url"],callback=self.comment_parse,meta={'bbs_id':response.meta["bbs_id"]})
        #analyse next page 
        yield scrapy.Request(url,callback=self.bbs_parse,meta={'bbs_id':response.meta["bbs_id"],'page_num':response.meta["page_num"]+1})

    # Extract the title of forum post and content of the first floor 
    # Extract post comments
    def comment_parse(self,response):
        # if no response retrun
        if len(response.css('.js-reply-floor-container'))==0:
            return
        floor_replyId=[]
        try:
            if response.meta["floor_replyId"]!=None:
                floor_replyId=response.meta["floor_replyId"]
        except:
            floor_replyId=[]
        ttfUrl = re.findall(',url\(\'//(.*ttf)',response.text)[0]
        ttfRes = requests.get("https://" + ttfUrl)
        name=0
        while name in self.using_name_set:
            name=random.randint(0,90000)
        ttfPath=self.ttfPath+str(name)+".ttf"
        print(os.getcwd())
        os.mknod(ttfPath)   
        with open(ttfPath, 'wb') as fw:
            fw.write(ttfRes.content)
        bbs_id=response.meta["bbs_id"]
        loader=ItemLoader(TopicItem(),response)
        loader.add_css('title','title::text')
        line=response.css('div.tz-paragraph *::text').extract()
        line=word_regular(line=line)
        font_dict = get_new_font_dict(self.standPath,ttfPath)
        line=word_format(line=line,font_dict=font_dict)
        loader.add_value("content",line)
        url=response.request.url
        nums=re.findall(r"\d+",url.split(r'/')[-1])
        topic_id=int(nums[0])
        next_page_num=int(nums[1])+1
        next_page_url=url.replace("-"+nums[1],"-"+str(next_page_num))
        loader.add_value('topic_id',topic_id)
        loader.add_value('bbs_id',bbs_id)
        # yield loader.load_item()
        for reply in response.css('.js-reply-floor-container'):
            if len(reply.css('.relyhfcon'))!=0:
                reply_url=reply.css('.relyhfcon ::attr(href)').extract()[1]
                index=int(reply_url.split('#')[-1])
                print(index)
                replyloader=ItemLoader(ReplyCommentItem(),reply)
                replyloader.add_value("reply_comment_id",floor_replyId[index-1])
                line=reply.css('.yy_reply_cont *::text').extract()
            else:
               replyloader=ItemLoader(CommentItem(),reply)
               replyloader.add_value("topic_id",topic_id)
               if len(reply.css('.reply-detail-deleted'))!=0:
                   floor_replyId.append(-1)
                   continue
               line=reply.css('.reply-detail *::text').extract()
            comment_id=reply.css('.js-reply-floor-container ::attr(data-reply-id)').get()
            floor_replyId.append(comment_id)
            line=word_regular(line=line)
            line=word_format(line=line,font_dict=font_dict)
            replyloader.add_value("content",line)
            replyloader.add_value("comment_id",comment_id)
            url=self.comment_url
            url+="topicId="+str(topic_id)+"&replyId="+str(comment_id)
            yield replyloader.load_item()
            if len(reply.css('.reply-comment'))!=0:
                yield scrapy.FormRequest(url=url,callback=self.comment_comment_parse,meta={"comment_id":comment_id,"floor_replyId":floor_replyId})
        os.remove(ttfPath)
        self.using_name_set.remove(name)
        yield scrapy.FormRequest(url=next_page_url,callback=self.comment_parse,meta={"bbs_id":bbs_id,"floor_replyId":floor_replyId})
    # Extract post comment`s comment
    def comment_comment_parse(self,response):
        rs=json.loads(response.text)
        comment_id=response.meta["comment_id"]
        comment_list=rs["result"]["list"]
        # if no comment return
        if comment_list==None:
            return
        for comment in comment_list:
            reply=ItemLoader(ReplyCommentItem())
            content=comment["content"][0]["content"]
            targetCommentId=comment["targetCommentId"]
            if targetCommentId==0:
                targetCommentId=comment_id
            reply.add_value("comment_id",comment["commentId"])
            reply.add_value("content",content)
            reply.add_value("reply_comment_id",targetCommentId)
            yield reply.load_item()
    def set_url(self,bbs_id,page_num):
        return self.base_url.replace("*",str(bbs_id)).replace("^",str(page_num))
