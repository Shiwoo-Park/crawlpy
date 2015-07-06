#!/usr/bin/python2.7
#coding:utf-8

import re
import traceback
import urllib2
from xml.etree.ElementTree import fromstring

DEBUG = False

# =================== HTTP 관련 ===================
def downloadPage(url, _userAgent="zumbot", retry=1):
	"""
	:param url: 방문 URL
	:param _userAgent: zumbot | browswer | mobile | wget
	:param retry: 회수 지정
	:return: dictionary (key별 데이터 포함)
	- header : 반환 header (에러일시 에러 msg)
	- content : 반환 html (에러일시 에러 스택정보)
	- url : 반환 url (에러일시 없음)
	- code : 반환 httpcode (에러일시 None)
	"""
	url = urllib2.quote(url, safe=":/?#[]@!$&'()*+,;=\\%~")
	opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
	request = urllib2.Request(url)
	# default userAgent == "zumbot"
	userAgent = "Mozilla/5.0 (Windows NT 6.1; ZumBot/1.0; http://help.zum.com/;WOW64;Trident/7.0;rv:11.0) like Gecko"
	if _userAgent == "browser":
		userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36"
	elif _userAgent == "mobile":
		userAgent = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
	elif _userAgent == "wget":
		userAgent = "wget"

	request.add_header("User-agent", userAgent)
	ret = dict()
	for i in range(retry+1):
		try:
			response = opener.open(request)
			ret["header"] = str(response.info())
			ret["content"] = response.read()
			ret["url"] = response.url
			ret["code"] = response.code
		except Exception, msg:
			ret["header"] = str(msg)
			ret["content"] = traceback.format_exc()
			ret["code"] = None

	return ret

# DEBUG Functions
def describeNode(node):
	print "TAG:%s / DATA:%s / ATTR:%s"%(node.tag, node.text, node.attrib)

def printDic(d):
	for item in d.items():
		print "%s:%s"%item

def getDicStr(d):
	s = ""
	for item in d.items():
		s += "%s:%s\n"%item
	return s

def getListStr(l):
	s = ""
	for e in l:
		s += "%s\n"%e
	return s

# MAIN MODULE
class XmlParser:
	"""
	XML 파싱을 쉽게 할 수 있는 기본적인 함수들을 제공하는 모듈
	"""
	def __init__(self, xml_content=""):
		self.feed(xml_content)

	def feed(self, xml_content):
		xml_content = xml_content.strip()
		if not xml_content:
			return
		self.xml_content = xml_content
		self.root = fromstring(xml_content)

	# 파싱 BASE 함수
	def getOneTagValByRegex(self, tag):
		"""
		:param tag: 추출하고자 하는 데이터의 태그명
		:return: 가장 먼저 출현한 해당 태그노드의 text
		"""
		regex_tag = "<\s*%s[\w\s='\\\"]*?>([^<>]+)<\s*/\s*%s\s*>"%(tag, tag)
		m = re.match(regex_tag, self.xml_content)
		if m:
			return m.group(1)
		return ""

	def getAllTagValByRegex(self, tag):
		"""
		:param tag: 데이터를 추출하고자하는 태그명
		:return: 모든 해당 태그 노드의 Text SET
		"""
		ret_set = set()
		regex_tag = "<\s*%s[\w\s='\\\"]*?>([^<>]+)<\s*/\s*%s\s*>"%(tag, tag)
		m = re.findall(regex_tag, self.xml_content)
		for element in m:
			ret_set.add(element)
		return ret_set

	def getLinksByRegex(self):
		"""
		:return: XML 안의 모든 URL을 추출하여 반환하는 함수
		"""
		regex_link = "https?://[\w\.\-/_]+"
		ret_set = set()
		m = re.findall(regex_link, self.xml_content)
		for element in m:
			ret_set.add(element)
		return ret_set

	def getAllNodeByTraverse(self, tag):
		"""
		:param tag: 추출하고자 하는 Node의 태그
		:return: 해당 태그 노드 리스트
		"""
		ret_list = []
		for node in self.root.iter(tag):
			if DEBUG:
				describeNode(node)
			ret_list.append(node)

		return ret_list

	def getChildrenDataAsDic(self, node):
		"""
		:param node: 자식노드의 데이터를 얻고자 하는 노드
		:return: 해당 노드의 Children 의 Tag와 Data를 Key, Value 형태로 된 Dic으로 반환
		"""
		ret_dic = dict()
		for child in node:
			tag_name = child.tag
			#tag_name = child.tag.lower()  # 무조건 모든 태그명은 lowercase로 바꾼다.
			if tag_name in ret_dic:
				ret_dic[child.tag] += ";%s"%child.text
			else:
				ret_dic[child.tag] = "%s"%child.text
		return ret_dic

	def getItemDic(self, path_tags=()):
		"""
		:param path_tags: 특정 태그노드를 찾기위해 Root 부터 순차적으로 방문해야하는 tag list
		:return: 목적 태그노드의 모든 자식노드 데이터 Dictionary (key:tag, value:text)
		"""
		last_tag = self.root.tag
		if path_tags:
			last_tag = path_tags[-1]

		now_node = self.root
		for tag in path_tags:
			now_node = now_node.find(tag)

		ret_dic = dict()
		if now_node.tag == last_tag:
			ret_dic = self.getChildrenDataAsDic(now_node)

		return ret_dic

	def getItemDicList(self, path_tags=()):
		"""
		:param path_tags: Root 부터 순차적으로 접근하고자 하는 Node까지 가는 Path
		:return: 해당 아이템들 예하에 있는 컨텐츠를 모두 Key,Value 형태로 묶어서 반환(형태 : dictionary list)

		ex) path_tags : [rss, channel, item] 이면
			<item> 이라는 노드들의 모든 내부 TAG 값을 Dictionary 형태로 묶어서 List에 넣어 반환
		"""
		last_tag = self.root.tag
		if path_tags:
			last_tag = path_tags[-1]

		ret_list = []
		now_node = self.root
		for tag in path_tags:
			if tag == last_tag:
				nodes = now_node.getiterator()
				for node in nodes:  # 각 item
					data_nodes = node.getiterator()
					for data_node in data_nodes:  # item의 element
						data_dic = self.getChildrenDataAsDic(data_node)
						if data_dic:
							ret_list.append(data_dic)
			else:
				now_node = now_node.find(tag)
		return ret_list

	# 파서에서 Override 할 함수
	def getChannelData(self):
		return self.getItemDic(["channel"])

	def getDocumentData(self):
		return self.getItemDicList(("channel", "item"))

	def getLinks(self):
		link_nodes = self.getAllNodeByTraverse("link")
		guid_nodes = self.getAllNodeByTraverse("guid")
		nodes = link_nodes + guid_nodes

		ret_set = set()
		regex_link = "https?://[\w\.\-/_]+"
		for node in nodes:
			link_text = node.text
			m = re.match(regex_link, link_text)
			if m:
				ret_set.add(link_text)
		return ret_set

class RssParser(XmlParser):
	"""
	RSS FEED만 전문적으로 파싱하기 위한 파서
	필드를 제한한것 이외에는 XmlParser와 특별한 차이점이 없음
	아래는 tag명, 설명, 예시 순으로 RSS피드에 대한 명세를 적어놓은 것.

	필드 상세 정보 - RSS v2.0
	출처 : https://validator.w3.org/feed/docs/rss2.html

	======= CHANNEL ========

	<Required>
	title	The name of the channel. It's how people refer to your service. If you have an HTML website that contains the same information as your RSS file, the title of your channel should be the same as the title of your website.	GoUpstate.com News Headlines
	link	The URL to the HTML website corresponding to the channel.	http://www.goupstate.com/
	description	Phrase or sentence describing the channel.

	<Optional>
	language	The language the channel is written in. This allows aggregators to group all Italian language sites, for example, on a single page. A list of allowable values for this element, as provided by Netscape, is here. You may also use values defined by the W3C.	en-us
	copyright	Copyright notice for content in the channel.	Copyright 2002, Spartanburg Herald-Journal
	managingEditor	Email address for person responsible for editorial content.	geo@herald.com (George Matesky)
	webMaster	Email address for person responsible for technical issues relating to channel.	betty@herald.com (Betty Guernsey)
	pubDate	The publication date for the content in the channel. For example, the New York Times publishes on a daily basis, the publication date flips once every 24 hours. That's when the pubDate of the channel changes. All date-times in RSS conform to the Date and Time Specification of RFC 822, with the exception that the year may be expressed with two characters or four characters (four preferred).	Sat, 07 Sep 2002 0:00:01 GMT
	lastBuildDate	The last time the content of the channel changed.	Sat, 07 Sep 2002 9:42:31 GMT
	category	Specify one or more categories that the channel belongs to. Follows the same rules as the <item>-level category element. More info.	<category>Newspapers</category>
	generator	A string indicating the program used to generate the channel.	MightyInHouse Content System v2.3
	docs	A URL that points to the documentation for the format used in the RSS file. It's probably a pointer to this page. It's for people who might stumble across an RSS file on a Web server 25 years from now and wonder what it is.	http://backend.userland.com/rss
	cloud	Allows processes to register with a cloud to be notified of updates to the channel, implementing a lightweight publish-subscribe protocol for RSS feeds. More info here.	<cloud domain="rpc.sys.com" port="80" path="/RPC2" registerProcedure="pingMe" protocol="soap"/>
	ttl	ttl stands for time to live. It's a number of minutes that indicates how long a channel can be cached before refreshing from the source. More info here.	<ttl>60</ttl>
	image	Specifies a GIF, JPEG or PNG image that can be displayed with the channel.
	textInput	Specifies a text input box that can be displayed with the channel.
	skipHours	A hint for aggregators telling them which hours they can skip.
	skipDays	A hint for aggregators telling them which days they can skip.

	======= ITEM ========

	title	The title of the item.	Venice Film Festival Tries to Quit Sinking
	link	The URL of the item.	http://www.nytimes.com/2002/09/07/movies/07FEST.html
	description	The item synopsis.	Some of the most heated chatter at the Venice Film Festival this week was about the way that the arrival of the stars at the Palazzo del Cinema was being staged.
	author	Email address of the author of the item.	oprah@oxygen.net
	category	Includes the item in one or more categories.	Simpsons Characters
	comments	URL of a page for comments relating to the item.	http://www.myblog.org/cgi-local/mt/mt-comments.cgi?entry_id=290
	enclosure	Describes a media object that is attached to the item.	<enclosure url="http://live.curry.com/mp3/celebritySCms.mp3" length="1069871" type="audio/mpeg"/>
	guid	A string that uniquely identifies the item.	<guid isPermaLink="true">http://inessential.com/2002/09/01.php#a2</guid>
	pubDate	Indicates when the item was published.	Sun, 19 May 2002 15:21:36 GMT
	source	The RSS channel that the item came from.	<source url="http://www.quotationspage.com/data/qotd.rss">Quotes of the Day</source>
	"""
	def __init__(self, xml_content=""):
		XmlParser.__init__(self, xml_content)
		self.rss_required_fields = ["title", "link", "description"]
		self.rss_optional_fields = ["language", "copyright", "managingEditor", "webMaster", "pubDate", "lastBuildDate", "docs", "category", "generator", "docs", "cloud", "ttl", "image", "textInput", "skipHours", "skipDays"]
		self.rss_field_match_dic = {"webmaster":"webMaster"}

	def getChannelData(self):
		ch_data = RssParser.getChannelData(self)

		# 전체 정규 필드값 채우기
		all_fields = self.rss_required_fields + self.rss_optional_fields
		for field in all_fields:
			if field not in ch_data:
				ch_data[field] = ""
			else:
				ch_data[field] = ch_data[field].strip()

		# 정규 필드로 매칭이 필요한 경우
		for match_field in self.rss_field_match_dic.keys():
			if match_field in ch_data:
				if ch_data[match_field]:
					ch_data[self.rss_field_match_dic[match_field]] = ch_data[match_field]

		return ch_data


if __name__:
	pass
	#from common_util import downloadPage

	# url = "http://www.windycitymom.org/feeds/posts/default?alt=rss"
	# downData = downloadPage(url)
	# xml_parser = XmlParser(downData["content"])
	# printDic(xml_parser.getChannelData())

	#xml_parser.getAllNodeByTraverse("link")
	#nodes = xml_parser.getAllNodeByTraverse("item")
	# for node in nodes:
	# 	d = xml_parser.getChildrenDataAsDic(node)
	# 	print d.keys()
	#xml_parser.getLinksByRegex()
	# dic_list = xml_parser.getItemDic(["channel","item"])
	# print "%s Documents Detected"%len(dic_list)
	# for item in dic_list[5].items():
	# 	print "%s:%s"%item

	# r = "<\s*a>([^<>]+)<\s*/\s*a\s*>"
	# s = "<a>hello</a>"
	# m = re.match(r, s)
	# if m:
	# 	print "MATCHED!"
	#print m.pop()
