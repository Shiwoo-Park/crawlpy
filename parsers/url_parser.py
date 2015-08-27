#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

import os
import sys
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )

from model.common import URLData
from urlparse import urlparse
from utils.str_util import isNumStr

TLDs = ["com","net","org","edu","int","biz","info","name","pro","museum","gov","mil","art","aero","coop","co","mobi","asia","travel","jobs"]
ccTLDs = ["bn","mm","li","pt","gb","jo","es","py","ki","ne","ar","tg","bf","mu","la","lv","ro","fm","cc","tw","im","me","rw","pl","tn","kz","sy","gs","mz","ir","vn","ie","ga","ml","pr","au","bv","kh","tc","lr","bo","td","cr","ci","er","gi","mt","jp","nf","do","tt","vg","si","il","md","az","to","ru","pe","gr","cz","??.ac","ky","id","no","cy","at","gy","bh","mo","am","nr","eu","ch","ua","kw","bw","lt","ng","pk","np","io","ee","kp","kg","bg","tl","fo","ca","it","gq","hm","mg","ae","ht","aw","tz","cx","sb","co","nu","bi","gg","mn","al","de","et","sn","ph","wf","re","pm","fi","cg","mw","uy","gh","sa","tr","lu","vi","sg","in","mf","ad","tm","hu","ug","kn","us","gp","nz","cn","ao","gf","rs","na","cw","pa","sm","bq","bj","mq","sj","fj","om","cf","vc","ke","ba","mv","hk","ma","dm","eg","hr","ag","tj","ni","km","by","gw","cm","uz","um","bz","st","aq","cv","su","dz","ge","mp","an","br","sl","gn","dj","se","bb","my","fr","tk","iq","tp","mh","af","ss","gu","eh","bl","cu","pg","qa","va","cl","ms","lc","ai","gd","nc","ve","sk","bs","bd","mc","dk","pf","je","ws","fk","vu","gm","mx","so","uk","sh","sd","mk","lk","th","jm","ps","sr","gt","bm","ls","ck","sx","pn","bt","ly","as","tf","ec","kr","be","mr","ax","tv","cd","sz","hn","gl","lb","sv","sc","pw","nl","is"]
SLDs = ["co","go","ac","nm","ne","or","re","kg","es","ms","hs","sc","pe"]


class URLParser:

	def parse(self, url):
		"""
		:param url: url to parse
		:return: URLData object
		"""
		url_obj = urlparse(url)
		url_data = URLData(url)

		url_data.org_domain = url_obj.netloc
		url_data.domain = url_obj.netloc
		if url_obj.netloc.startswith("www."):
			url_data.domain = url_obj.netloc[4:]
		top_domain = self.getTopDomain(url_obj.netloc)
		if top_domain:
			url_data.top_domain = top_domain
		url_data.path = url_obj.path
		url_data.query_dic = self.__getQueryDic(url_obj.query)
		return url_data

	def getTopDomain(self, domain):

		pieces = domain.split(".")
		if len(pieces) < 2:
			return None
		elif len(pieces) == 2:
			if pieces[1] in TLDs:
				return domain
			elif pieces[1] == "kr":
				if pieces[0] in SLDs:
					return None
				else:
					return domain
		else:
			if len(pieces) == 4:
				try:
					k = int(pieces[-1])
					return None
				except Exception, msg:
					pass

			if pieces[-1] in TLDs:
				return ".".join(pieces[-2:])
			elif pieces[-1] in ccTLDs:
				if pieces[-2] in SLDs:
					return ".".join(pieces[-3:])
				else:
					return ".".join(pieces[-2:])
			else:
				return ".".join(pieces[-3:])

	def __getQueryDic(self, query):
		ret = dict()
		kv_list = query.split("&")
		for kv in kv_list:
			kv_arr = kv.split("=")
			if len(kv_arr) == 2:
				ret[kv_arr[0]] = kv_arr[1]
		return ret

	def extractByURL(self, urlpt, url):
		urlpt_data = self.parse(urlpt)
		url_data = self.parse(url)
		return self.extractByURLData(urlpt_data, url_data)

	def extractByURLData(self, urlpt_data, url_data):
		ret_dic = dict()
		matched = False

		print urlpt_data
		print url_data

		if self.__matchDomain(urlpt_data.domain, url_data.domain, ret_dic):
			if self.__matchPath(urlpt_data.path, url_data.path):
				if self.__matchQuery(urlpt_data.query_dic, url_data.query_dic):
					matched = True
		if matched:
			return ret_dic
		else:
			return dict()

	def __matchDomain(self, urlpt_domain, url_domain, ret_dic):
		if not urlpt_domain or not url_domain:
			return False

		if urlpt_domain == "(ANYHOST)":
			ret_dic["ANYHOST"] = url_domain
			return True
		elif self.__isKey(urlpt_domain):
			ret_dic[urlpt_domain[1:-1]] = url_domain
			return True
		elif url_domain == urlpt_domain:
			return True

		return False

	def __matchPath(self, urlpt_path, url_path, ret_dic):
		anypath_pos = url_path.find("(ANYPATH)")
		if anypath_pos > 0:  # TODO ANYPATH 구현
			front_path = url_path[0:anypath_pos]
			back_path = url_path[anypath_pos+]
			pass
		else:  # 일반적인 path 매칭(/ 단위 구분)
			in_path_arr = url_path.split("/")
			pt_path_arr = urlpt_path.split("/")
			arr_len = len(in_path_arr)

			if arr_len != len(pt_path_arr):
				return False

			for i in range(arr_len):
				in_path_elem = in_path_arr[i]
				pt_path_elem = pt_path_arr[i]

				if self.__isKey(pt_path_elem):
					key = pt_path_elem[1:-1]
					if self.__isValidKeyVal(key, in_path_elem):
						ret_dic[key] = in_path_elem
					else:
						return False

				elif in_path_elem != pt_path_elem:
					return False

			return True
		pass

	def __matchQuery(self, urlpt_query_dic, url_query_dic):
		pass

	def __isKey(self, s): # 예약어 형태인지 확인
		if s.startswith("(") and s.endswith(")"):
			return True
		else:
			return False

	def __isValidKeyVal(self, key, val):
		# 예약어의 적합성 검증 - 숫자
		if key.startswith("INT_"):
			if not isNumStr(val):
				return False
		return True


if __name__ == '__main__':
	url = "http://news.abc.co.kr/web/game/view.php?a=1&b=2&c=3"
	url2 = "http://news.efg.co.kr/web/game/view.php?a=11&b=22&c=33"
	url3 = "http://www.efg.co.kr/web/game/view.php?a=11&b=22&c=33"
	urlpt = "http://(ANYHOST)/web/(BOARD)/view.php?a=(A)&b=(B)&c=3"
	parser = URLParser()

	"""
	url_data = parser.parse(url)
	url_data["age"] = "22"

	url_data2 = parser.parse(url)
	url_data2["name"] = "shiwoo"
	url_data.update(url_data2)
	"""
	url_data = parser.extract(urlpt, url2)

	print url_data