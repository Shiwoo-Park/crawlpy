#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parsers.blog_rss_parser import BlogFeedParser
from utils.str_util import getDicStr, getListStr
from utils.http_client import downloadPage
from utils.io_util import readFile

SAVE_PATH = "C:\Users\jsilva\Desktop\Temp\[SC] blog\\rss\parse_result.txt"

def testAll():
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

	file = open(SAVE_PATH, mode="a")
	urls = rss_links.split("\n")
	xml_parser = BlogFeedParser()

	for url in urls:
		url = url.strip()
		if not url.startswith("http://"):
			continue
		print "Visit : %s"%url
		file.write("==================== PARSE [%s] ====================\n"%url)
		channel_data, link_data = testURL(url, xml_parser, file)
		file.flush()
		print "	Parsed : %s"%url
	file.close()

def testURL(url, xml_parser=None, output_file=None):
	downData = downloadPage(url)
	return testXML(downData["content"], xml_parser, output_file)

def testFile(path, xml_parser=None, output_file=None):
	xml_str = readFile(path)
	return testXML(xml_str, xml_parser, output_file)

def testXML(xml_str, xml_parser=None, output_file=None):
	if not xml_parser:
		xml_parser = BlogFeedParser()

	xml_parser.feed(xml_str)
	channel_data = xml_parser.getChannelData()
	link_data = xml_parser.getLinks()
	channel_data_str = getDicStr(channel_data)
	link_data_str = getListStr(link_data)

	print channel_data_str
	print link_data_str

	if output_file:
		output_file.write(channel_data_str)
		output_file.write(link_data_str)

	return channel_data, link_data

if __name__:
	#testAll()
	testFile("resources/rss_feed_burner_sample.xml")
	#testURL("http://feeds.feedburner.com/vs-rss")