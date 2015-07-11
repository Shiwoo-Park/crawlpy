# coding:utf8
from xml_parser import FeedParser, downloadPage, getDicStr, getListStr


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
		for rf in self.rss_required_fields:
			if ch_data[rf]:
				self.channel_score += 2
		for of in self.rss_optional_fields:
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

if __name__:
	rss_links = """
major
http://blog.rss.naver.com/anjigagu.xml
http://enjoiyourlife.com/rss
http://blog.daum.net/xml/rss/ktg0205
http://rss.egloos.com/blog/plasmid

Blogger
http://www.windycitymom.org/feeds/posts/default?alt=rss
http://www.unodetantosblogs.com/feeds/posts/default?alt=rss
http://www.coles-corner-and-creations.com/feeds/posts/default?alt=rss

워드프레스
http://kimcya.com/feed/
http://null.perl-hackers.net/?feed=rss2
http://information-plus.net/feed

XE
http://www.onlifezone.com/rss
http://underkg.co.kr/rss
http://my.blogkor.com/textyle/rss

두루팔
http://www.lifeformula.net/rss.xml
	"""

	save_path = "C:\Users\jsilva\Desktop\Temp\[SC] blog\\rss\parse_result.txt"
	file = open(save_path, mode="a")
	urls = rss_links.split("\n")
	xml_parser = BlogFeedParser()

	for url in urls:
		url = url.strip()
		if not url.startswith("http://"):
			continue
		print "Visit : %s"%url
		file.write("==================== PARSE [%s] ====================\n"%url)
		downData = downloadPage(url)
		xml_parser.feed(downData["content"])
		channel_data = xml_parser.getChannelData()
		link_data = xml_parser.getLinks()
		file.write(getDicStr(channel_data))
		file.write(getListStr(link_data))
		file.flush()
		print "	Parsed : %s"%url
	file.close()
