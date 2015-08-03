#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
from crawl_utils.xml_parser import XmlParser
from crawl_utils.http_client import downloadPage
from crawl_utils.str_util import printDic, extractStr

if __name__ == '__main__':

	ret_dic = dict()
	video_url = "http://blog.naver.com/MultimediaFLVPlayer.nhn?blogId=ryu_black&logNo=80196848315&vid=6609703DDBE52161ACBA985614D63D9D88FC&width=720&height=438&ispublic=true"
	downData = downloadPage(video_url)
	vid = ""
	in_key = ""
	width = ""
	height = ""
	if downData:
		vid = extractStr(downData["content"], """qsParam.vid = '****';""")
		in_key = extractStr(downData["content"], """qsParam.inKey = '****';""")
		width = extractStr(downData["content"], """layout.width = '****';""")
		height = extractStr(downData["content"], """layout.height = '****';""")

	if vid and in_key:

		# 모든 정보를 가진 XML URL생성
		video_info_url = "http://serviceapi.nmv.naver.com/flash/videoInfo.nhn?vid=%s&inKey=%s"%(vid, in_key)
		print "VISIT : ", video_info_url
		downData = downloadPage(video_info_url)
		xml_parser = XmlParser(downData["content"])
		data_dic = xml_parser.getItemDic(is_recursive=True)

		ret_dic["mode"] = "N"
		ret_dic["type"] = "VIDEO"
		ret_dic["guid"] = ""  # TODO
		ret_dic["crawlTime"] = int(time.time())
		ret_dic["channelIdentifier"] = "http://blog.naver.com"
		ret_dic["channelName"] = "네이버 블로그"
		ret_dic["createTimeText"] = data_dic["WriteDate"]
		ret_dic["webLink"] = data_dic["Link"]
		m = re.match("http://blog\.naver\.com/([\w\-]+)/([0-9]*).*", data_dic["Link"])
		if m:
			ret_dic["blog_id"] = m.group(1)
			ret_dic["post_id"] = m.group(2)
			ret_dic["clickLink"] = "http://blog.naver.com/PostView.nhn?blogId=%s&logNo=%s"%(ret_dic["blog_id"], ret_dic["post_id"])
		ret_dic["title"] = data_dic["Subject"]
		ret_dic["imageThumbnailDefault"] = data_dic["CoverImage"]
		tmp_list = data_dic["Thumbnails"].split()
		previewThumbnailList = []
		previewTimeList = []
		for elem in tmp_list:
			if elem:
				if elem.startswith("http"):
					previewThumbnailList.append(elem)
				else:
					previewTimeList.append(elem.split(".")[0])
		ret_dic["previewThumbnailList"] = "\t".join(previewThumbnailList)
		ret_dic["previewTimeList"] = "\t".join(previewTimeList)
		ret_dic["authorName"] = data_dic["WriterName"]
		ret_dic["runningTime"] = data_dic["PlayTime"]
		if width and height:
			if int(width) > 720:
				ret_dic["isHD"] = 1
			ret_dic["resolution"] = int(width) * int(height)
		ret_dic["playCount"] = data_dic["PlayCount"]
		previewJumpurlList = []
		if ("blog_id" in ret_dic) and ("post_id" in ret_dic) and ("blog_id" in ret_dic):
			for previewTime in previewTimeList:
				previewJumpurlList.append("http://blog.naver.com/%s?Redirect=Log&logNo=%s&beginTime=%s&jumpingVid=%s"%(ret_dic["blog_id"], ret_dic["post_id"], previewTime, vid))
			ret_dic["previewJumpurlList"] = "\t".join(previewJumpurlList)

		print "====== XML RESULT ==================================="
		printDic(data_dic)
	print "======== PARSE RESULT ================================="
	printDic(ret_dic)