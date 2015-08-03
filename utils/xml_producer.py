#/usr/bin/env python
# coding: utf8

import os
from datetime import datetime

from utils.log import getLogger

"""
Module to make XML file

Made by. shiwoo park (silva23@naver.com)
Created on 2015. 3. 23.
"""

class XMLPrinter():
	''' Make XML file by input parse result dictionary
		data["type"] decides fixed XML Fields
		if no 'type' key, all k,v will be printed
	'''

	def __init__(self, _outputDirPath=os.getcwd(), _documentCountLimit=1000):
		self.fieldListDic = dict()
		self.outputDirPath = _outputDirPath
		self.documentCountLimit = _documentCountLimit
		self.logger = getLogger()
		self.setupOutputDir()
		self.initSCFieldListDic()

	def initSCFieldListDic(self):
		self.fieldListDic["TEST1"] = ["fieldName1", "fieldName2", "fieldName3"]

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

	# type 지정한 경우
	dic = dict()
	dic["type"] = "TEST1"
	dic["fieldName1"] = "shiwoo_park"
	dic["fieldName2"] = "Korean"
	dic["fieldName3"] = "29 years old"
	dic["fieldName4"] = "likes English"
	dataList.append(dic)

	dic = dict()
	dic["fieldName1"] = "shiwoo_park"
	dic["fieldName2"] = "Korean"
	dic["fieldName3"] = "29 years old"
	dic["fieldName4"] = "likes English"
	dataList.append(dic)

	# 데이터 dictionary의 'type' KEY 구분하여 출력
	dirPath = "./data_produce_test/output"
	printer = XMLPrinter(dirPath, 2)
	printer.printXML(dataList, "testXmlData")
