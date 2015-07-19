#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

from db_util import getDBConnectionByName, selectQuery, executeQuery
from model.common import URLData
from url_parser import URLParser
from str_util import isNumStr
from log import getLogger

"""
URL 패턴 지정 Rule에 의해
URL 인식과  Normalizing을 지원하고,
특정 부분을 파싱하여 원하는 K,V형태로 제공하는 모듈

< URL패턴 정의 테이블 스키마 >

CREATE TABLE `url_patterns` (
	`pattern_id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	`domain` VARCHAR(255) NOT NULL,
	`priority` INT(10) NULL DEFAULT NULL,
	`url_type` VARCHAR(50) NULL DEFAULT 'undefined',
	`in_pattern` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8_bin',
	`out_pattern` VARCHAR(255) NULL DEFAULT NULL,
	PRIMARY KEY (`patterin_id`),
	UNIQUE INDEX `uniq_in_pattern` (`in_pattern`),
	INDEX `idx_domain` (`domain`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
ROW_FORMAT=COMPACT
;



1. 기능
- 숫자 문자열 구분
- HOST KEY 별 패턴매칭
- 날짜값 파싱
- URL 타입
"""

class PswURLParser:
	def __init__(self, init_dic=None):
		self.info_dic = dict()
		self.logger = getLogger()
		if self.isValidInfo(init_dic):
			self.info_dic = init_dic
		else:
			self.logger.error("Invalid init information")
			exit(1)
		self.url_parser = URLParser()
		self.pattern_dic = {"normal":dict(), "host_key":dict()}  # 모든 패턴정보를 담을 Dictionary
		# dic["normal" | "hostkey"][domain] = [(priority, URLData()), ...]

	def isValidInfo(self, init_dic):
		if ("db_info_key" in init_dic) and ("pattern_table" in init_dic):
			return True
		return False

	def initPatterns(self):
		# Keys of URLData
		# url_type, out_pattern, pattern_id
		select_query = "SELECT pattern_id, domain, priority, url_type, in_pattern, out_pattern FROM "+self.info_dic["pattern_table"]
		db_cursor = getDBConnectionByName(self.info_dic["db_info_key"])
		data_list = selectQuery(db_cursor, select_query)
		for pattern_id, domain, priority, url_type, in_pattern, out_pattern in data_list:
			url_data = self.url_parser.parse(in_pattern)
			pass


		# 모든 List element에 대하여 priority에 따라 sorting 필요
		#for

	def parseTest(self, url, in_pt, out_pt):
		url_data = self.url_parser.parse(url)
		in_pt_data = self.url_parser.parse(in_pt)
		if self.matchURLData(url_data, in_pt_data):
			out_pt_data = self.url_parser.parse(out_pt)
			self.makeURL(url_data, out_pt_data)
			return
		else:
			return None

	def parse(self, url, host_key=""):
		url_data = self.url_parser.parse(url)

		if host_key:
			# 특정 Key에 대한 패턴만 매칭 (generator)
			pass
		else:
			# host 부분이 일치하는 패턴이 있을경우 먼저 매칭
			matched = False
			if url_data.domain in self.pattern_dic["normal"]:
				pattern_list = self.pattern_dic["normal"][url_data.domain]
				for priority, pt_url_data in pattern_list:
					if self.matchURLData(url_data, pt_url_data):
						return url_data

	def matchURLData(self, url_data, pt_url_data):
		if self.matchHost(url_data.domain, pt_url_data.domain):
			if self.matchPath(url_data.path, pt_url_data.path):
				if self.matchQuery(url_data.query_dic, pt_url_data.query_dic):
					return True
		return False

	def matchHost(self, in_domain, pt_domain):
		pass

	def matchPath(self, in_path, pt_path):
		pass

	def matchQuery(self, in_query_dic, pt_query_dic):
		pass

	def isKey(self, s):
		if s.startswith("(") and s.endswith(")"):
			return s[1:-1]
		else:
			return ""

	def makeURL(self, url_data, out_pt_data):
		pass


if __name__ == '__main__':
	# 시작 정보 입력
	init_info = {"db_info_key":"", "pattern_table":""}

	test_url = "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/"
	in_pattern = "https://leetcode.com/problems/(STR_ID)/"
	out_pattern = in_pattern
	psw_parser = PswURLParser()
	url_data = psw_parser.parseTest(test_url,in_pattern,out_pattern)
	#print url_data

	p = URLParser()
	print p.parse(test_url)