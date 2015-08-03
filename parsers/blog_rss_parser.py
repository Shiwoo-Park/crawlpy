#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from parsers.xml_parser import FeedParser


class BlogFeedParser(FeedParser):
	"""
	각종 블로그의 RSS를 파싱하여 동일한 형태의 데이터로 제공하는 모듈

	<channel>
	required = ["title", "link", "description"]
	oprional = ["generator", "pubDate", "lastBuildDate", "link", "ttl", "webMaster", "webmaster", "managingEditor", "language", "copyright", "docs", "category"]
	others = ["image"]
	"""
	def __init__(self, xml_content=""):
		FeedParser.__init__(self, xml_content)
		self.channel_score = -1
		self.initGeneratorMatchDic()

	def initGeneratorMatchDic(self):
		"""
		크롤된 <generator> 내부의 값을 통일시켜 사용할 수 있도록 하기위한 dictionary 정보생성
		dic[최종Generator값] = [generator태그 안에 들어갈수 있는 인식 텍스트(모두 소문자)]
		"""
		self.gen_match_dic = dict()
		self.gen_match_dic["blog.naver.com"] = ["naver"]
		self.gen_match_dic["tistory.com"] = ["tistory"]
		self.gen_match_dic["blog.daum.net"] = ["daum"]
		self.gen_match_dic["egloos.com"] = ["egloos"]
		self.gen_match_dic["blogspot.com"] = ["blogger","blogspot"]
		self.gen_match_dic["wordpress.org"] = ["wordpress.org"]
		self.gen_match_dic["xpressengine.com"] = ["xpressengine"]
		self.gen_match_dic["wordpress.com"] = ["wordpress.com"]

	def getChannelScore(self):
		"""
		정규 필드를 가지고 있을 시, Score가 부여된다.
		필수 필드 : 2점
		옵션 필드 : 1점
		"""
		if self.channel_score >= 0:
			return self.channel_score
		self.channel_score = 0
		ch_data = self.getChannelData()
		for rf in self.feed_required_fields:
			if ch_data[rf]:
				self.channel_score += 2
		for of in self.feed_optional_fields:
			if ch_data[of]:
				self.channel_score += 1
		return self.channel_score

	def getGenerator(self, parsed_gen):
		for generator, txt_list in self.gen_match_dic.items():
			for clue_text in txt_list:
				if clue_text in parsed_gen:
					return generator
		return ""

	def getChannelData(self):
		ch_data = FeedParser.getChannelData(self)
		ch_data["generator"] = self.getGenerator(ch_data["generator"].lower())
		return ch_data

