#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

import traceback

#from db_util import getDBConnectionByName, selectQuery, executeQuery
from url_parser import URLParser
from str_util import isNumStr
from log import getLogger

DEBUG=True

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

	def __init__(self, init_dic):
		self.info_dic = dict()
		self.logger = getLogger()
		if self.isValidInfo(init_dic):
			self.info_dic = init_dic
		else:
			self.logger.error("Invalid init information")
			exit(1)
		self.url_parser = URLParser()  # 가장 기본형태의 URL 파서

		self.pattern_dic = {"normal":dict(), "host_key":dict()}  # 모든 패턴정보를 담을 Dictionary
		# dic["normal" | "hostkey"][domain] = [(priority, URLData()), ...]

		self.build_pt_dic = dict()  # 추출해낸 예약어로 다른 원하는 여러가지의 URL을 만들어낼 수 있다.
		# dic[out_pt][build_url_name] = build_pattern

	def isValidInfo(self, init_dic):
		if ("db_info_key" in init_dic) and ("pattern_table" in init_dic):
			return True
		return False

	def initPatterns(self):
		# Keys of URLData
		# url_type, out_pattern, pattern_id
		select_query = "SELECT pattern_id, domain, priority, url_type, in_pattern, out_pattern FROM "+self.info_dic["pattern_table"]
		#db_cursor = getDBConnectionByName(self.info_dic["db_info_key"])
		#data_list = selectQuery(db_cursor, select_query)
		data_list = []
		for pattern_id, domain, priority, url_type, in_pattern, out_pattern in data_list:
			# 패턴 정보 초기화
			in_pt_data = self.url_parser.parse(in_pattern)
			out_pt_data = self.url_parser.parse(out_pattern)

			in_pt_data["pattern_id"] = pattern_id
			in_pt_data.domain = domain
			in_pt_data["priority"] = priority
			in_pt_data["url_type"] = url_type
			in_pt_data["out_pt_data"] = out_pt_data

			target_dic = self.pattern_dic["normal"]
			if domain == "ANYHOST" and in_pt_data.domain != "(ANYHOST)":
				target_dic = self.pattern_dic["host_key"]
			if domain not in target_dic:
				target_dic[domain] = list()
			target_dic[domain].append((priority, in_pt_data))


		# 모든 List element에 대하여 priority에 따라 sorting 필요
		for domain, pt_list in self.pattern_dic["normal"].items():
			pt_list.sort()
		for domain, pt_list in self.pattern_dic["normal"].items():
			pt_list.sort()

	def parseTest(self, url, in_pt, out_pt):
		url_data = self.url_parser.parse(url)
		in_pt_data = self.url_parser.parse(in_pt)
		if self.matchURLData(url_data, in_pt_data):
			out_pt_data = self.url_parser.parse(out_pt)
			self.makeURL(url_data, out_pt_data)
			return url_data
		else:
			return None

	def parse(self, url, host_key=""):
		url_data = self.url_parser.parse(url)

		if host_key:
			# 특정 Key에 대한 패턴만 매칭 (generator)
			pass
		else:
			# host 부분이 일치하는 패턴이 있을경우 먼저 매칭
			if url_data.domain in self.pattern_dic["normal"]:
				pattern_list = self.pattern_dic["normal"][url_data.domain]
				for priority, pt_url_data in pattern_list:
					if self.matchURLData(url_data, pt_url_data):
						return url_data
			else:
				pattern_list = self.pattern_dic["normal"]["ANYHOST"]
				for priority, pt_url_data in pattern_list:
					if self.matchURLData(url_data, pt_url_data):
						return url_data

	def matchURLData(self, url_data, pt_url_data):
		parse_dic = dict()

		try:
			if self.matchHost(url_data.domain, pt_url_data.domain, parse_dic):
				print "Host MATCHED : %s"%parse_dic
				if self.matchPath(url_data.path, pt_url_data.path, parse_dic):
					print "Path MATCHED : %s"%parse_dic
					if self.matchQuery(url_data.query_dic, pt_url_data.query_dic, parse_dic):
						print "Query MATCHED : %s"%parse_dic
						print "Data dic : %s"%url_data.data_dic
						url_data.data_dic.update(parse_dic)
						return True
		except Exception, msg:
			print traceback.format_exc()
			self.logger.error(traceback.format_exc())

		return False

	def matchHost(self, in_domain, pt_domain, parse_dic):
		if self.isKey(pt_domain):
			parse_dic[pt_domain[1:-1]] = in_domain
			return True
		elif in_domain == pt_domain:
			return True
		return False

	def matchPath(self, in_path, pt_path, parse_dic):
		anypath_pos = in_path.find("(ANYPATH)")
		if anypath_pos > 0:  # TODO ANYPATH 구현
			pass
		else:  # 일반적인 path 매칭(/ 단위 구분)
			in_path_arr = in_path.split("/")
			pt_path_arr = pt_path.split("/")
			arr_len = len(in_path_arr)

			if arr_len != len(pt_path_arr):
				return False

			for i in range(arr_len):
				in_path_elem = in_path_arr[i]
				pt_path_elem = pt_path_arr[i]

				if self.isKey(pt_path_elem):
					key = pt_path_elem[1:-1]
					if self.isValidKeyVal(key, in_path_elem):
						parse_dic[key] = in_path_elem
					else:
						return False

				elif in_path_elem != pt_path_elem:
					return False

			return True

	def matchQuery(self, in_query_dic, pt_query_dic, parse_dic):
		for in_key, in_val in in_query_dic.items():
			if in_key in pt_query_dic:
				if self.isKey(pt_query_dic[in_key]):
					key = pt_query_dic[in_key][1:-1]
					if self.isValidKeyVal(key, in_val):
						parse_dic[key] = in_val
					else:
						return False
				elif in_val != pt_query_dic[in_key]:
					return False
			else:  # 패턴 쿼리에 따로 지정하지 않은 key (그냥 놔둠)
				pass
		return True

	def isKey(self, s):
		# 예약어 형태인지 확인
		if s.startswith("(") and s.endswith(")"):
			return True
		else:
			return False

	def isValidKeyVal(self, key, val):
		# 예약어의 적합성 검증 - 숫자
		if key.startswith("INT_"):
			if not isNumStr(val):
				return False
		return True

	def makeURL(self, url_data, out_pt_data):
		pass


if __name__ == '__main__':

	# 시작 정보 입력
	init_info = {"db_info_key":"", "pattern_table":""}

	test_url = "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/?a=11&b=33"
	in_pattern = "https://(ANYHOST)/problems/(STR_ID)/?a=(INT_ID)"
	out_pattern = in_pattern
	psw_parser = PswURLParser(init_info)
	url_data = psw_parser.parseTest(test_url,in_pattern,out_pattern)
	print url_data

	#p = URLParser()
	#print p.parse(test_url)