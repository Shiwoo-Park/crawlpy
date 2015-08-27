#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-


class URLData:
	""" 기본적인 URL정보와 URL크롤+파싱으로 추가되는 모든 데이터를 들고있을 객체 """

	def __init__(self, url=""):
		self.original_url = url
		self.guid = ""
		self.org_domain = ""  # host 자체
		self.domain = ""      # org_domain 에서 www. 제거
		self.top_domain = ""  # 최상단 도메인 TLD 고려
		self.path = ""
		self.query_dic = dict()
		self.data_dic = dict()  # 기타 URL 의 관련 데이터가 들어갈 자료구조

	def __setitem__(self, key, value):
		self.data_dic[key] = value

	def __getitem__(self, item):
		if item in self.data_dic:
			return self.data_dic[item]
		else:
			return None

	def __str__(self):
		d = {"original_url": self.original_url, "guid": self.guid,
			"domain": self.domain, "top_domain": self.top_domain, "org_domain": self.org_domain,
			"path": self.path, "query_dic": self.query_dic, "data_dic": self.data_dic}
		return str(d)

	def __cmp__(self, other):
		if self.guid == other.guid:
			return True
		return False


class HtmlPageInfo:

	def __init__(self):
		self.url = ""
		self.charset = "utf-8"
		self.generator = None
		self.robotDeny = False
		self.title = None  # default: title 태그 값
		self.links = dict()  # {href:nodeID, ... }
		self.imgs = dict()  # {src:nodeID, ...}
		self.metaInfo = dict()  # key 는 모두 대문자
		self.dataDic = dict()   # 파싱 최종 결과를 담는 곳
		# dataDic의 기본 key: title, body_sid, body_eid, regdate

	def setTitle(self, text):
		self.title = text.decode(self.charset).encode("utf-8")

	def __str__(self):
		desc_arr = []
		desc = "URL \t: %s\nCHARSET \t: %s\nGENERATOR \t: %s\nROBOT_DENY \t: %s\nTITLE \t: %s\n\nMETA INFOS"\
			%(self.url, self.charset, self.generator, self.robotDeny, self.title)
		desc_arr.append(desc)

		for key, val in self.metaInfo.items():
			desc_arr.append("\n%s: %s"%(key, val))

		desc_arr.append("\n\nALL LINKS (%s)"%len(self.links))
		for link, nid in self.links.items():
			desc_arr.append("\nURL: %s \t(NodeID: %s)"%(link, nid))

		desc_arr.append("\n\nALL IMAGES (%s)"%len(self.imgs))
		for src, nid in self.imgs.items():
			desc_arr.append("\nURL: %s \t(NodeID: %s)"%(src, nid))

		desc_arr.append("\n\n##### DATA DIC #####")
		for key, val in self.dataDic.items():
			desc_arr.append("\n\nFIELD: %s \nVALUE: %s"%(key, val))

		return ''.join(desc_arr)


if __name__ == '__main__':
	pass

