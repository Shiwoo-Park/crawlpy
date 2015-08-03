#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from utils.log import getLogger
from resource.html_patterns import PATTERN_DATA

"""
HTML 에 등장하는 특정 문자열을 이용하여 해당 웹페이지의 속성을 파악하는 모듈
패턴은 DB로부터 읽어온다.

pattern_type : 패턴의 속성 대분류 (ex. dead, spam, generator)
pattern_data : 각 대분류 속성에 대한 소분류
pattern_string : 해당 속성을 결정짓기위해 html내에 존재해야하는 특정 string

String matching algorithm은 KMP를 사용한다.
"""

# Knuth-Morris-Pratt string matching
# David Eppstein, UC Irvine, 1 Mar 2002

def exists(text, pattern):

	""" Yields all starting positions of copies of the pattern in the text.
Calling conventions are similar to string.find, but its arguments can be
lists or iterators, not just strings, it returns all matches, not just
the first one, and it does not need the whole text in memory at once.
Whenever it yields, it will have read the text exactly up to and including
the match that caused the yield."""

	# allow indexing into pattern and protect against change during yield
	pattern = list(pattern)

	# build table of shift amounts
	shifts = [1] * (len(pattern) + 1)
	shift = 1
	for pos in range(len(pattern)):
		while shift <= pos and pattern[pos] != pattern[pos-shift]:
			shift += shifts[pos-shift]
		shifts[pos+1] = shift

	# do the actual search
	startPos = 0
	matchLen = 0
	for c in text:
		while matchLen == len(pattern) or \
				matchLen >= 0 and pattern[matchLen] != c:
			startPos += shifts[matchLen]
			matchLen -= shifts[matchLen]
		matchLen += 1
		if matchLen == len(pattern):
			return True
	return False


class HtmlData:
	def __init__(self, html):
		self.html = html
		self.size = len(html)
		self.data_dic = dict()
		"""
		self.data_dic (pattern_type : pattern_data)
		- generator : site generator
		- spam : adult, commercial ...
		- dead : expired, construction ...
		- category : shopping, news, ...
		"""

	def __str__(self):
		return str(self.data_dic)


class HtmlChecker:

	def __init__(self, html=None):
		self.logger = getLogger()
		self.pt_info = dict()
		self.__init_patterns()
		self.check(html)

	def __init_patterns(self):

		pt_data_list = self.__load_pattern_data()
		if not pt_data_list:
			self.logger.error("No pattern data loaded")
			return
		for pattern_type, pattern_data, pattern_string in pt_data_list:
			if pattern_type not in self.pt_info:
				self.pt_info[pattern_type] = dict()

			if pattern_data not in self.pt_info[pattern_type]:
				self.pt_info[pattern_type][pattern_data] = set()

			self.pt_info[pattern_type][pattern_data].add(pattern_string)

	def __load_pattern_data(self):
		pt_data_list = []
		lines = PATTERN_DATA.split("\n")
		for line in lines:
			line = line.strip()
			if line:
				pt_data_list.append(line.split("\t"))
		return pt_data_list

	def __check_html(self):

		keys = self.pt_info.keys()
		for key in keys:
			pt_info = self.pt_info[key]
			for pattern_data, pt_str_set in pt_info.items():
				if key in self.html_data.data_dic:
					break
				for pt_str in pt_str_set:
					if exists(self.html_data.html, pt_str):
						self.html_data.data_dic[key] = pattern_data
						break

	def check(self, html):
		"""
		:param html: html to check
		:return: HtmlData object, if html is empty, return None
		"""
		if html:
			self.html_data = HtmlData(html)
			self.__check_html()
			return self.html_data
		return None


if __name__ == "__main__":

	from utils.http_client import downloadPage
	import sys

	url = "http://www.brewology.com/?p=2217"
	url = "http://www.lifeformula.net/node/1414"
	url = "http://dsconsulting.kr/2015/07/10/cloud-computing-iaas-paas-saas/"
	url = "http://blog.naver.com/PostView.nhn?blogId=cherry3778&logNo=220398395551&redirect=Dlog&widgetTypeCall=true"
	if len(sys.argv) > 1:
		url = sys.argv[1]

	user_agent = "Mozilla/5.0"
	down_data = downloadPage(url, user_agent)
	html_checker = HtmlChecker()

	if "error" in down_data:
		print down_data["error"]
	else:
		html = down_data["content"]
		html_data = html_checker.check(html)
		print html_data