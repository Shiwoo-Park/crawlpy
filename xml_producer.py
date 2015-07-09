#/usr/bin/env python
# coding: utf8

# type 이 SC를 정하니 그때그때 맞춰서 프린트 하는걸로.
# Dir 없으면 자동생성 (입력한 Path자체를 무조건 가능하게)

import os
from datetime import datetime
from config import PY_LIB_PATH

sys.path.insert(0, PY_LIB_PATH)
from log import getLogger

"""
Module to make XML file

Made by. shiwoo park (silva23@naver.com)
Created on 2015. 3. 23.
"""

class XMLPrinter():
	''' Make XML file by input parse result dictionary
		SC category decides XML Fields
	'''

	def __init__(self, _outputDirPath=os.getcwd(), _documentCountLimit=1000):
		self.fieldListDic = dict()
		self.outputDirPath = _outputDirPath
		self.documentCountLimit = _documentCountLimit
		self.logger = getLogger()
		self.setupOutputDir()
		self.initSCFieldListDic()

	def initSCFieldListDic(self):
		self.fieldListDic["NEWS"]         = ["mode", "type", "guid", "crawlTime","channelIdentifier","channelName", "channelType", "createTime","originLink", "webLink", "mobileLink", "title", "subTitle", "body", "bodyHtml", "documentCategory", "imageList", "imageThumbnail78x78", "imageThumbnail126x126", "imageThumbnailSignature", "imageCount", "videoCount", "authorName", "authorEmail", "headlineType"]
		self.fieldListDic["BLOG_POST"]    = ["mode", "type", "guid", "registrationTime", "crawlTime", "channelIdentifier", "createTime", "updateTime", "channelTitle", "channelLink", "wClickLink", "wViewLink", "mClickLink", "mViewLink", "title", "body", "bodyExtension", "htmlTitle", "metaTitle", "metaKeywords","metaDescription", "postTags", "postCategory", "postCoordinates", "replyCount", "recommendCount", "outLinks", "iframeLinks", "embedLinks", "trackbackList", "fileList", "imageList","imageMD5List", "imageThumbnail78x78", "imageThumbnail126x126", "imageThumbnailList80x54", "sourceType"]
		self.fieldListDic["BLOG_CHANNEL"] = ["mode", "type", "guid", "registrationTime", "crawlTime", "channelIdentifier", "createTime", "updateTime", "siteIdentifier", "siteName", "channelTitle", "channelLink", "author", "image", "description", "language","generator", "sourceType"]
		self.fieldListDic["KNOW"]         = ["mode", "type", "guid", "crawlTime", "channelIdentifier", "channelName", "createTime", "webLink", "mobileLink", "title", "body", "bodyHtml", "documentCategoryName", "imageCount", "answerCount", "answerRecommendCount", "readCount", "recommendCount", "linkCount", "isSolved", "isGoods"]
		self.fieldListDic["VIDEO"]        = ["mode", "type", "guid", "crawlTime", "channelIdentifier", "channelName", "createTime", "webLink", "mobileLink", "clickLink", "title", "body", "bodyHtml", "imageThumbnailDefault", "imageThumbnail80x60", "imageThumbnail130x102", "authorName", "previewJumpurlList", "previewTimeList", "previewThumbnailList", "runningTime", "resolution", "playCount", "playCount", "viewCount", "isCharged", "isHD", "isAdult"]
		self.fieldListDic["BBS"]          = ["mode", "type", "guid", "crawlTime", "channelIdentifier", "channelName", "createTime", "webLink", "mobileLink", "title", "body", "bodyHtml", "metaTitle", "metaKeywords", "metaDescription", "outLinks", "redirectedUrl", "imageCount", "videoCount", "recommendCount", "readCount", "replyCount"]
		self.fieldListDic["TEST1"] = ["downloadURL", "parser_id", "title", "body", "authorText", "authorName", "authorEmail", "createTimeText", "createTime"]

	def setupOutputDir(self):
		if not os.path.exists(self.outputDirPath) :
			os.makedirs(self.outputDirPath)
			self.logger.info("Made Dir :%s"%self.outputDirPath)

	def getOutputDir(self):
		return self.outputDirPath.replace("//", "/")

	def getXMLStr(self, document_data):
		keyList = None
		if "type" in document_data:
			scType = document_data["type"]
			if scType in self.fieldListDic:
				keyList = self.fieldListDic[scType]
		ret_xml = ""
		contents_xml = ""
		if keyList:  # 필드명 지정
			for field in keyList:
				if field in document_data:
					contents_xml += "		<%s><![CDATA[%s]]></%s>\n"%(field, document_data[field], field)
		else:  # 필드명 미지정(모두출력)
			for key,val in document_data.items():
				contents_xml += "		<%s><![CDATA[%s]]></%s>\n"%(key, val, key)

		if len(contents_xml) > 0:
			ret_xml = "	<DOCUMENT>\n"
			ret_xml += contents_xml
			ret_xml += "	</DOCUMENT>\n"

		return ret_xml

	def printXML(self, dataDicList, fileName=None):
		if not fileName:
			nowDate = datetime.now()
			fileName = nowDate.strftime('document_%Y%m%d_%H%M%S')

		counter = 0
		xmlFile = None
		dataCount = len(dataDicList)
		fileName = self.outputDirPath +"/"+ fileName
		fileName = fileName.replace("//", "/")

		for i in range(0, dataCount):

			dataDic = dataDicList[i]
			if (i % self.documentCountLimit) == 0:  # Data limit 도달
				if xmlFile:
					xmlFile.write("</DOCUMENTS>")
					xmlFile.close()
					self.logger.info("Write [%s] finished"%xmlFile.name)
					xmlFile = None

				if counter == 0:
					xmlFile = open(fileName+".xml", 'w')
					xmlFile.write("<DOCUMENTS>\n")
				else:
					xmlFile = open(fileName+"_%s.xml"%counter, 'w')
					xmlFile.write("<DOCUMENTS>\n")

				counter += 1
			doc_xml = self.getXMLStr(dataDic)
			xmlFile.write(doc_xml)

		if xmlFile:
			xmlFile.write("</DOCUMENTS>")
			xmlFile.close()
			self.logger.info("Write [%s] finished"%xmlFile.name)


if __name__ == '__main__':
	# 예제 데이터 생성
	dataList = []
	dic = dict()
	dic["mode"] = "N"
	dic["type"] = "BLOG_POST"
	dic["guid"] = "http://abc.com?a=1&seconed=3"
	dic["registrationTime"] = "1004246518"
	dic["sourceType"] = "lalalala"
	dic["channelIdentifier"] = "blog.naver.com"
	dic["channelType"] = "economy"
	dic["authorEmail"] = "silva23@naver.com"
	dic["name"] = "shiwoo"
	dataList.append(dic)

	dic2 = dict()
	dic2["mode"] = "N"
	dic2["type"] = "NEWS"
	dic2["guid"] = "http://abc.com?a=1&seconed=3"
	dic2["registrationTime"] = "1004246518"
	dic2["sourceType"] = "lalalala"
	dic2["channelIdentifier"] = "blog.naver.com"
	dic2["channelType"] = "economy"
	dic2["authorEmail"] = "silva23@naver.com"
	dic2["name"] = "shiwoo"
	dataList.append(dic2)

	dic3 = dict()
	dic3["mode"] = "N"
	dic3["type"] = "NEWS"
	dic3["guid"] = "http://abc.com?a=1&seconed=3"
	dic3["registrationTime"] = "1004246518"
	dataList.append(dic3)

	dic4 = dict()
	dic4["mode"] = "N"
	dic4["type"] = "NEWS"
	dic4["guid"] = "http://abc.com?a=1&seconed=3"
	dic4["registrationTime"] = "1004246518"
	dataList.append(dic4)

	dic5 = dict()
	dic5["mode"] = "N"
	dic5["type"] = "NEWS"
	dic5["guid"] = "http://abc.com?a=1&seconed=3"
	dic5["registrationTime"] = "1004246518"
	dataList.append(dic5)


	# 데이터 SC 구분하여 출력
	#dirPath = "C:\\Users\\jsilva\\data_produce_test\\output"
	dirPath = "C:/Users/jsilva/data_produce_test/output"
	dirPath = "/home/moon/tmp/"
	printer = XMLPrinter(dirPath, 2)
	printer.printXML(dataList, "testXmlData")
