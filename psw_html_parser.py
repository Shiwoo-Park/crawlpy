#!/usr/bin/env python
#coding: utf8

import re
from urlparse import urlparse
from HTMLParser import HTMLParser
from log import getLogger
from http_client import downloadPage, getEncoding
from io_util import saveIntoFile, readFile
from str_util import guessEncoding

def getFinalCharset(charset):
	charset = charset.lower()
	if charset in ["ms949", "ks_c_5601-1987"]:
		return "cp949"
	return charset

class HtmlNode:

	def __init__(self):
		self.id = -1
		self.depth = -1
		self.tag = None
		self.parent = None
		self.is_leaf = False
		self.children = None
		self.attr_dic = None
		self.text = ""

	def __str__(self):
		return self.getDesc()

	def getDesc(self, charset="utf-8"):
		indent = ""
		for i in range(self.depth):
			indent += " "

		attr_txt = ""
		if self.attr_dic:
			attr_txt = str(self.attr_dic)

		data_txt = ""
		if self.text:
			if charset == "utf-8":
				data_txt = self.text
			else:
				data_txt = (self.text).decode(charset).encode("utf-8")

		ret = "%s%s  <%s>  %s  %s  %s"%(indent, str(self.depth), self.tag, attr_txt, data_txt, str(self.id))
		return ret


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


class PswHtmlParser(HTMLParser):

	def parse(self, url, html):
		self.pageInfo.url = url
		self.feed(html)

	def __init__(self):
		HTMLParser.__init__(self)
		self.reset()  # super모듈 - HTMLParser 초기화

		self.logger = getLogger("PswHtmlParser")
		self.clsDict = dict()  # K="class", V="Node ID List"  ex. {'clsName': [13,24,35], ...}
		self.idDict = dict()   # K="id", V="Node ID"  ex. {'idName': 25, 'idName2': 60, ...}
		self.nodeDict = dict()  # K="NodeID", V="HTMLNode Object"
		self.textList = list()  # 텍스트만 순서대로 저장
		self.robotDenyPatternStr = ".*(nofollow)|(noarchive)|(noindex).*"
		self.linkPattern = "https?://[\w\-\%\.\?\=가-힣]+"

		# Page Info
		self.pageInfo = HtmlPageInfo()

		# Clean html
		self.unpairedTagList = ["BR", "HR", "INPUT", "IMG", "META", "LINK"]  # Pair가 아닌 단독으로 사용되는 TAG
		self.skipTagList = ["FONT", "HR", "INPUT"]        # 해당 노드만 무시
		self.ignoreTagList = ["STYLE", "SCRIPT", "FORM"]  # 예하 노드 전체 무시
		self.rmClsList = list()   # basic remove class list
		self.ignoreTag = None

		# Tree 생성관련
		self.parentDepth = 0
		self.nodeIdCounter = 0
		self.textIdCounter = 0
		self.tree = HtmlNode()
		self.nodeStack = []  # DOM을 구성하는 Stack
		# 파싱이 끝났을때 ['ROOT'] 상태가 아니면 invalid tree

		# Init tree
		root = self.tree
		root.id = self.nodeIdCounter
		root.depth = len(self.nodeStack)
		root.tag = "ROOT"
		self.nodeStack.append(root)
		self.treeText = ""

		# tree file output
		self.savepath = "tree.out"

	###### PARSING FUNCTIONS #####

	def handle_starttag(self, tag, attrs):
		tag = tag.upper()
		if self.ignoreTag:
			return
		if tag in self.skipTagList or "_" in tag:
			# tag명에 '_' 포함된 것도 무시 ex) B_LMENU, B_CONT_TOP
			return
		if tag in self.ignoreTagList:
			self.ignoreTag = tag
			return

		#print "handle_starttag: ",tag

		parentNode = self.nodeStack[-1]
		nNode = HtmlNode()
		nNode.parent = parentNode
		nNode.tag = tag.lower()
		if attrs:
			dic = dict()
			for k,v in attrs:
				dic[k] = v
			nNode.attr_dic = dic
		nNode.depth = len(self.nodeStack)
		self.nodeIdCounter += 1
		nNode.id = self.nodeIdCounter
		if parentNode.children is None:
			parentNode.children = list()
		parentNode.children.append(nNode)
		self.nodeDict[nNode.id] = nNode
		if tag not in self.unpairedTagList:
			self.nodeStack.append(nNode)

		# Node 내용 파일에 기록 - tag부분
		#saveIntoFile(nNode.getDesc(self.pageInfo.charset), self.savepath)
		saveIntoFile(nNode.getDesc(), self.savepath)
		self.treeText += "\n"+nNode.getDesc()

		# Handle Tags
		if tag == "META":
			self.handle_meta_attrs(attrs)
		# TODO 메타태그 전부 보기
		#print "META: ",attrs

		if tag == "LINK":
			self.handle_link_attrs(attrs)

		if tag == "IMG":
			src = self.getAttr("src", attrs)
			if src:
				if src not in self.pageInfo.imgs:
					self.pageInfo.imgs[src] = nNode.id

		link_url = None
		if tag == "A":
			link_url = self.getAttr("href", attrs)
		if tag == "IFRAME":
			link_url = self.getAttr("src", attrs)
		if tag == "FRAME":
			link_url = self.getAttr("src", attrs)

		if link_url:
			if link_url.startswith("/"):
				urlObj = urlparse(self.pageInfo.url)
				link_url = "http://" + urlObj.hostname + link_url
			m = re.match(self.linkPattern, link_url)
			if m:
				if link_url not in self.pageInfo.links:
					self.pageInfo.links[link_url] = nNode.id

		if tag == "TITLE":
			if not self.pageInfo.title:
				self.pageInfo.title = int(nNode.id)

		# Handle Attributes
		for attr in attrs:
			if attr[0].upper() == "CLASS":
				if len(attr[1].strip()) != 0:
					if attr[1] not in self.clsDict:
						self.clsDict[attr[1]] = list()
					self.clsDict[attr[1]].append(nNode.id)

			if attr[0].upper() == "ID":
				if len(attr[1].strip()) != 0:
					self.idDict[attr[1]] = nNode.id

	def handle_meta_attrs(self, attrs):
		name=""     # name
		prop = ""   # property
		httpEquiv = ""  # http-equiv
		for key, val in attrs:

			key = key.upper()
			if key == "NAME":
				name = val.upper()
			if key == "PROPERTY":
				prop = val.upper()
			if key == "HTTP-EQUIV":
				httpEquiv = val.upper()
			if key == "CHATSET":
				self.pageInfo.charset = getFinalCharset(val)

			if key == "CONTENT":
				# charset
				patternStr = ".*charset=([\-\w]+).*"
				matchObj = re.match(patternStr, val)
				if matchObj:
					self.pageInfo.charset = getFinalCharset(matchObj.group(1))

				# name에 대한 처리
				if name == "ROBOTS":  # robotdeny
					matchObj = re.match(self.robotDenyPatternStr, val)
					if matchObj:
						self.pageInfo.robotDeny = True
				if name == "GENERATOR":
					self.pageInfo.generator = val

				if name in ["TITLE", "AUTHOR", "KEYWORDS", "DESCRIPTION"]:
					self.pageInfo.metaInfo[name] = val

				if prop in ["OG:URL","OG:TYPE","OG:TITLE","OG:SITE_NAME","OG:DESCRIPTION","OG:IMAGE"]:
					self.pageInfo.metaInfo[prop] = val
				# 기타 property: OG:ARTICLE:AUTHOR, ARTICLE:SECTION

				if httpEquiv in ["CONTENT-TYPE"]:
					self.pageInfo.metaInfo[httpEquiv] = val

	def handle_link_attrs(self,attrs):
		typeAttr = ""
		badFeedStrList = ["댓글","response","reply","comment"]  # 우리가 원하는 피드가 아닌경우
		for key, val in attrs:
			key = key.upper()
			if key == "TYPE":
				typeAttr = val
			if key == "TITLE":
				if typeAttr.lower() == "application/rss+xml":
					for badStr in badFeedStrList:
						if badStr in val.lower():
							typeAttr = ""
			if key == "HREF":
				if typeAttr.lower() == "application/rss+xml":
					self.pageInfo.metaInfo["FEED"] = val

	def handle_endtag(self, tag):
		tag = tag.upper()
		if self.ignoreTag:
			if tag == self.ignoreTag:
				self.ignoreTag = None
			return
		if tag in self.skipTagList:
			return
		if tag in self.unpairedTagList:
			return
		if "_" in tag:
			return

		if tag == "TITLE":
			if isinstance(self.pageInfo.title, type(0)):
				#self.pageInfo.title = self.pageInfo.setTitle(self.getTextByNodeID(self.pageInfo.title))
				self.pageInfo.title = self.getTextByNodeID(self.pageInfo.title)

		#print "handle_endtag: ",tag
		if tag.lower() == self.nodeStack[-1].tag:
			lastNode = self.nodeStack.pop()

		"""
		self.printNodeStack()
		print "Removed end tag:", lastNode.tag
		if self.nodeIdCounter >= 30:
			exit()
		"""

	""" 함부로 구현했다가는 피볼듯..
	def handle_startendtag(self, tag, attrs):
		print "START-END TAG: "+tag
		# hr, br 등의 tag는 그냥 pass
		pass
	"""

	def handle_data(self, data):
		if self.ignoreTag:
			return

		#print "handle data:", data

		" ".join(data.strip())  # 공백 통일
		if data.strip() != "":
			parentNode = self.nodeStack[-1]
			tNode = HtmlNode()
			tNode.tag = "text"
			tNode.parent = parentNode
			tNode.is_leaf = True
			tNode.depth = len(self.nodeStack)
			self.nodeIdCounter += 1
			tNode.id = self.nodeIdCounter
			tNode.text = data.strip()

			self.nodeDict[tNode.id] = tNode
			self.textList.append(data)
			if parentNode.children is None:
				parentNode.children = list()
			parentNode.children.append(tNode)

			# Node 내용 파일에 기록 - text 부분
			#saveIntoFile(tNode.getDesc(self.pageInfo.charset), self.savepath)
			saveIntoFile(tNode.getDesc(), self.savepath)
			self.treeText += "\n"+tNode.getDesc()

	########## DEBUG FUNC ##########
	def printNodeStack(self):
		nodeList = []
		stackSize = len(self.nodeStack)
		for i in range(0,stackSize):
			nodeList.append(self.nodeStack[i].tag)
		print "nodeStack: ", nodeList


	########## RETRIEVE DATA FUNC ##########

	def getAttr(self, key, attrs):
		key = key.upper()
		for k, v in attrs:
			k = k.upper()
			if k == key:
				return v.strip()
		return None

	def getNthValInDic(self, key, dic, option=""):
		if option == "":
			try:
				return [ dic[key] ]
			except:
				return []

		retList = []
		for k,v in dic.items():
			if option == "prefix" and k.startswith(key):
				retList.append(v)
			if option == "contain" and (key in k):
				retList.append(v)

		return retList

	def getTextByNodeID(self, nodeID):
		""" 해당 nodeID 노드의 모든 Children 텍스트 취합 """
		node = self.nodeDict[nodeID]
		retText = self.collectTextsUnderNode(node,"")
		return retText

	def collectTextsUnderNode(self, node, retText, isExt=False):
		if node.is_leaf:
			return node.text.strip()
		else:
			childText = ""
			if isExt:
				if node.tag == "br":
					childText += "\n"
				if node.tag == "p":
					childText += "\n\n"

			if node.children:
				for child in node.children:
					childText += self.collectTextsUnderNode(child, "")
				retText += childText

			return retText

	# Node ID를 찾아주는 다양한 함수 들
	def getNodeIDByID(self, idName, option="", nth=0):
		""" html의 해당 id를 가진 Element 이하 텍스트 취합 """
		retList = self.getNthValInDic(idName, self.idDict, option)
		if len(retList) > 0:
			return retList[nth]
		else:
			return None

	def getNodeIDByClassNth(self, className, option="", nth=0):
		# TODO options 기능
		""" html의 해당 class를 가진 N번째 Element 이하 텍스트 취합 """
		className = className.strip()
		retList = self.getNthValInDic(className, self.clsDict, option)
		if len(retList) == 0:
			return None
		counter = 0
		for nidList in retList:
			for nid in nidList:
				counter += 1
				if counter > nth:
					return nid

	def getNodeIDByImg(self, _src, option=""):
		# 첫번째 매칭되는것: nth = 1
		_src = _src.strip()
		imgs = self.pageInfo.imgs
		for src, nid in imgs.items():
			if option == "contain":
				if _src in src:
					return nid
			elif option == "prefix":
				if src.startswith(_src):
					return nid
			elif src == _src:
				return nid
		return None

	def getNodeIDByLink(self, _href, option=""):
		# 첫번째 매칭되는것: nth = 1
		_href = _href.strip()
		links = self.pageInfo.links
		for href, nid in links.items():
			if option == "contain":
				if _href in href:
					return nid
			elif option == "prefix":
				if href.startswith(_href):
					return nid
			elif _href == href:
				return nid
		return None

	def getTextFromTextList(self, clueText, nthMatch, offset):
		"""
		clueText = 찾고자 하는 텍스트
		nthMatch = 해당 텍스트가 몇번째에 매칭 되었는지 (첫번째  = 1)
		offset = clueText로부터 최종 얻고자 하는 텍스트의 상대주소
		ex) ["작성자","홍길동"] 의 경우 홍길동을 얻고 싶다면,  args = ("작성자",1)
		"""
		retText = None
		matchCount = 0
		for i in range(0,len(self.textList)):
			try:
				if clueText == self.textList[i]:
					matchCount += 1
					if matchCount == nthMatch:
						retText = self.textList[i+offset]
						break
			except Exception, msg:
				self.logger.error("[Error] getTextFromTextList: " + str(msg) )
		return retText

	def getEndNodeID(self, nodeID):
		node = self.nodeDict[nodeID]
		for child in node.parent.children:
			if child.id > nodeID:
				return child.id - 1

	def getDataByRange(self, sNodeID, eNodeID):
		"""
		dictionary 리턴
		text: 텍스트만 전부 붙여서 리턴
		extext: extension으로, <br>은 \n, <p>는 \n\n으로 바꿔서 리턴
		imgs: image tag의 src값 리스트
		imgs: a tag의 href값 리스트
		"""
		ret = dict()
		imgList = []

		for src, nid in self.pageInfo.imgs:
			if nid >= sNodeID and nid <= eNodeID:
				imgList.append(src)
		ret["imgs"] = imgList

		linkList = []
		for href, nid in self.pageInfo.links:
			if nid >= sNodeID and nid <= eNodeID:
				linkList.append(href)
		ret["links"] = linkList

		text = ""
		extText = ""
		for nid in range(sNodeID, eNodeID):
			node = self.nodeDict[nid]
			if node.is_leaf:
				text += " " + node.text.strip()
				extText += node.text.strip()
			if node.tag == "br":
				extText += "\n"
			if node.tag == "img":
				extText += "<img src=\""+self.getAttr("src", node.attrs)+"\" />"
			if node.tag == "p":
				extText += "\n\n"
		ret["text"] = text
		ret["extext"] = extText

		return ret


if __name__ == '__main__':
	# instantiate the parser and fed it some HTML
	parser = PswHtmlParser()

	targetUrl = "http://blog.yes24.com/blog/blogMain.aspx?blogid=ture99&artSeqNo=7822516" #인코딩 에러
	targetUrl = "http://book.interpark.com/blog/postArticleView.rdo?blogName=orangenamu&postNo=3824516"
	targetUrl = "http://blog.moneta.co.kr/blog.log.view.screen?blogId=gk5253&logId=8019476"
	targetUrl = "http://blog.joins.com/media/folderlistslide.asp?uid=ksc8527&list_id=13519915"  #인코딩 에러
	targetUrl = "http://blog.dreamwiz.com/media/index.asp?uid=chae119&list_id=13998929"
	targetUrl = "http://oniondev.egloos.com/9603983"
	targetUrl = "http://blog.aladin.co.kr/788479165/7201321"
	targetUrl = "http://blog.aladin.co.kr/roadmovie?CommunityType=AllView&page=2&cnt=617"
	targetUrl = "http://blog.daum.net/mudoldol/689"
	targetUrl = "http://blog.donga.com/lake1379/archives/6558"
	targetUrl = "http://booklog.kyobobook.co.kr/sonmc/1395492"

	targetUrl = "http://blog.naver.com/PostView.nhn?blogId=ishine75&logNo=220152159716&redirect=Dlog&widgetTypeCall=true"
	targetUrl = "http://blog.daum.net/adelheimcom/660?t__nil_issue1=txt&nil_id=3"
	targetUrl = "http://blog.daum.net/_blog/BlogTypeView.do?blogid=0PEaN&articleno=2130"
	targetUrl = "http://jsilva.tistory.com/entry/%EC%A0%90-%EC%A0%9C%EA%B1%B0-%EC%8B%9C%EC%88%A0-%ED%9B%84-%EC%A3%BC%EC%9D%98%EC%82%AC%ED%95%AD"
	targetUrl = "http://www.todayhumor.co.kr/board/view.php?table=bestofbest&no=197445&s_no=197445&page=1"
	targetUrl = "http://www.likewind.net/1101"
	targetUrl = "http://blog.naver.com/ishine75/220152159716"
	targetUrl = "http://blog.naver.com/PostView.nhn?blogId=ishine75&logNo=220152159716&redirect=Dlog&widgetTypeCall=true"

	testHtml = readFile("D:\logs\\test.html")

	# DOWNLOAD AND PARSE
	if True:
		down_data = downloadPage(targetUrl)
		if "error" not in down_data:
			real_URL = down_data["url"]
			http_header = down_data["header"]
			http_content = down_data["content"]

			print "########## REQUEST INFO ##########"
			reqInfo = "\nURL: "+real_URL
			reqInfo += "\nHEADERS"+http_header
			print reqInfo

			parser.parse(real_URL, http_content)
		else:
			print down_data["error"]
	else:
		parser.parse("http://test.com", testHtml)

	# SET FILE OUTPUT
	savepath = "D:\logs\\tree.out"
	saveIntoFile(parser.treeText, savepath)

	# RESULT: BASIC INFO
	pageInfo = "\n########## PAGE INFO ##########\n"
	pageInfo += str(parser.pageInfo)
	print pageInfo

	print "\n########## PARSE TEST ##########"
	#sid = parser.getNodeIDByID("entry")
	sid = parser.getNodeIDByClassNth("entry")

	if sid:
		eid = parser.getEndNodeID(sid)
		#eid = parser.getNodeIDByID("entry")
		eid = parser.getNodeIDByClassNth("daum_like_wrapper")

		bodyData = parser.getDataByRange(sid, eid)
		keys = ["imgs","links","text","extext"]
		for key in keys:
			val = bodyData[key]
			print "%s: %s"%(key, val)

	"""
	print parser.getNodeIDByImg("http://ts.daumcdn.net/custom/blog/46/463909/skin/images/iconTag.gif", 0)
	print parser.getNodeIDByImg("63909/skin/images/iconTag.gif", 0, "contain")
	print parser.getNodeIDByImg("http://ts.daumcdn.net/custom/blog/46/463", 0, "prefix")

	print parser.getNodeIDByID("", "", 0)
	print parser.getNodeIDByClassNth("like_wrapper","contain")
	print parser.getNodeIDByClassNth("daum","prefix")
	print parser.getNodeIDByClassNth("cal_day","contain",4)
	#"""
############################# TODO 정리 #############################
"""
extension text 작업 진행
"""
 