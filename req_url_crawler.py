#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

"""
컨텐츠 URL을 입력 받아 순차적으로 크롤하는 크롤러.
크롤한 URL들은 DB에 저장하거나 파일로 출력할 수 있다.
input_dic에 입력가능한 크롤정보를 입력한다.

< 크롤 정보 지정 >
db_info_key :
url_table :
request_urls :

< 크롤 방식 >
1. 크롤할 URL을 직접 지정한다.
2. 크롤 URL을 LOAD 할 테이블을 지정한다.

< 크롤 URL LOAD 테이블 모델 >

CREATE TABLE `request_urls` (
	`url_md5` CHAR(32) NOT NULL,
	`request_url` VARCHAR(1024) NOT NULL,
	`visited` CHAR(1) NOT NULL DEFAULT 'N',
	`request_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`crawl_time` TIMESTAMP NULL DEFAULT NULL,
	`state_msg` VARCHAR(255) NOT NULL DEFAULT '',
	PRIMARY KEY (`url_md5`)
)
ENGINE=InnoDB
;

"""

import os
import time
import sys
from heapq import heappush, heappop

from model.common import URLData
from db_util import getDBConnectionByName, selectQuery, executeQuery
from log import getLogger, Log
from hasher import Hasher
from http_client import downloadPage
from utils.xml_producer import XMLPrinter

LOG_PATH = "/home/user/logs"
OUTPUT_PATH = "/home/output/xml"
CRAWL_DELAY = 3  # sec


class RequestURLCrawler:
	def __init__(self, init_dic):
		self.logger = getLogger()
		if not self.__isValidInfo(init_dic):
			self.logger.error("Failed to init RequestURLCrawler : Invalid input information")
			exit(1)

		self.info_dic = init_dic
		self.cursor = None
		self.req_url_queue = []  # unvisited seeds (minimum heap ordered by page no.)
		# heappush(req_url_queue, (guid_hash, url_data))
		self.url_data_dic = dict()  # visited + fully parsed data, dic[view_guid_hash] = URLData()
		self.hasher = Hasher()
		self.url_factory = None
		self.html_parser = None
		self.xml_producer = XMLPrinter(OUTPUT_PATH)

	def __isValidInfo(self, init_dic):
		"""
		크롤에 필요한 모든 정보가 들어왔는지 유효성 체크
		:param init_dic: 크롤 정보
		:return: valid 여부
		"""
		if "request_urls" in input_dic:
			if input_dic["request_urls"]:
				return True
		elif ("url_table" in input_dic) and ("db_info_key" in input_dic):
			return True

		return False

	def run(self, _cursor=None):
		""" 크롤러를 처음 동작시키는 entry point """
		self.cursor = _cursor
		if not self.cursor:
			self.cursor = getDBConnectionByName(self.info_dic["db_info_key"])

		self.logger.info("Start RequestURLCrawler crawler!")

		self.loadRequestURLs()  # 일정량만큼의 Request URL 추출
		while self.req_url_queue:
			self.logger.info("Loaded [%s] view URLs", len(self.req_url_queue))

			crawl_count = self.startCrawl()  # req_url_queue 안의 URL 소모
			self.logger.info("Crawled [%s] view URLs"%crawl_count)

			save_count = self.saveURLData()  # 크롤한 View URL 전체 저장 + URL상태변경
			self.logger.info("Saved [%s] view URLs", save_count)

			self.loadRequestURLs()

		self.logger.info("Finished total crawler!")

		if not _cursor:
			self.cursor.close()

	def loadRequestURLs(self, load_count=1000):

		""" 요청 URL을 일정량만큼 LOAD 하여 Queue에 채운다. """

		if "request_urls" in input_dic:
			count = 0
			while count <= load_count:
				req_url = input_dic["request_urls"].pop()
				url_info = self.url_factory.getGuid(req_url)  # url_info 는 dict 타입
				if url_info:
					if url_info["url_type"] == "view":
						guid_hash = self.hasher.md5(url_info["guid"])
						url_data = URLData(guid_hash)
						url_data.data_dic.update(url_info)
						heappush(self.req_url_queue, (guid_hash, url_data))
						count += 1
		else:
			query = "SELECT url_md5, request_url FROM "+self.info_dic["url_table"]+" WHERE visited = 'N' ORDER BY request_time LIMIT %s"%load_count
			data_list = selectQuery(self.cursor, query, [self.info_dic["domain_id"], "N"])
			for no, video_url, insert_time in data_list:
				url_info = self.url_factory.getGuid(video_url)
				if url_info:
					if url_info["url_type"] == "view":
						guid_hash = self.hasher.md5(url_info["guid"])
						url_data = URLData(guid_hash)
						url_data.data_dic.update(url_info)
						heappush(self.req_url_queue, (guid_hash, url_data))

	def startCrawl(self):
		""" queue의 URL을 하나씩 소모하며 파싱된 최종데이터 추출 """

		count = 0
		while self.req_url_queue:
			guid_hash, url_data = heappop(self.req_url_queue)
			self.visitURL(url_data)
			self.url_data_dic[guid_hash] = url_data
			count += 1
			time.sleep(CRAWL_DELAY)

		return count

	def visitURL(self, url_data):
		"""  URL 방문, 파싱하여 URL 데이터 생성 """

		down_url = url_data["url_info"]["down_url"]
		down_data = downloadPage(down_url)

		if down_data:
			http_header, http_content, real_URL = down_data
			parse_result = self.html_parser.parse(http_header, http_content, real_URL)
			crawl_data_count = len(parse_result)
			if parse_result:
				url_data.data_dic.update(parse_result)
			self.logger.info("	Crawled URL [%s] data from URL [%s]"%(crawl_data_count, down_url))

	def saveURLData(self):
		""" 추출한 View URL을 DB 및 File로 출력 """

		# 1. Update flag from load table
		update_query = "UPDATE "+self.info_dic["url_table"]+" SET visited = 'Y' WHERE url_md5 = %s"
		save_count = 0
		document_dic_list = []
		for guid_hash, url_data in self.url_data_dic.items():
			try:
				ret = executeQuery(self.cursor, update_query, [url_data.id])
				document_dic_list.append(url_data.data_dic)
				save_count += 1
				self.logger.info("	Updated URL %s : %s"%(ret, url_data.get("guid")))
			except Exception, msg:
				self.logger.error("	Update Failed : %s : %s", url_data.get("guid"), msg)

		# 2. Save data into XML file
		self.xml_producer.printXML(document_dic_list)

		return save_count

def setLogger():
	log_format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
	date_format = "%y-%m-%d %H:%M:%S"
	YMD = time.strftime("%Y%m%d")
	program_name = sys.argv[0]
	cur = program_name.rfind("/")
	if cur >= 0:
		program_name = program_name[cur+1:]
	log_file = LOG_PATH+"%s/%s_%s.log"%(YMD, program_name, os.getpid())
	root_logger = Log(filename=log_file, format=log_format, datefmt=date_format)

if __name__ == '__main__':

	# 로깅
	setLogger()

	# 크롤 조건 지정
	input_dic = dict()

	# TABLE 로드 방식
	input_dic["db_info_key"] = ""  # DB 정보 (config/db_info.py에 입력되어 있어야 함)
	input_dic["url_table"] = ""  # 크롤할 URL을 불러오고 작업이 끝났을 시, 상태를 갱신할 Table

	# 크롤 URL 직접 지정 방식
	input_dic["request_urls"] = []  # 지정한 seed를 init seed로 사용

	# Optional
	input_dic[""] = ""

	# 크롤러 START
	crawler = RequestURLCrawler(input_dic)
	crawler.run()
