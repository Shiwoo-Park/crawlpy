#/usr/bin/env python
# coding: utf-8

import urllib2
import traceback
import codecs
import socket
from json import JSONEncoder

ESCAPE_CHARS = ":/?#[]@!$&'()*+,;=\\%~"
socket.setdefaulttimeout(10)

def downloadPage(url, user_agent="", retry=1):
	"""
	:param url: visit URL
	:param user_agent: UserAgent String
	ex1. Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36
	ex2. Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30
	:param retry: count

	:return: dictionary (contains data by each key)
	- header : response header
	- content : html (utf-8)
	- url : response url
	- code : httpcode
	- error : error msg(error stack)
	"""

	url = urllib2.quote(url, safe=ESCAPE_CHARS)
	opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
	request = urllib2.Request(url)

	if user_agent:
		request.add_header("User-agent", user_agent)

	ret = dict()
	for i in range(retry+1):
		try:
			response = opener.open(request)
			ret["header"] = str(response.info())
			ret["content"] = encodeToUTF8(response.read())
			ret["url"] = response.url
			ret["code"] = response.code
		except Exception, msg:
			ret["header"] = str(msg)
			ret["content"] = ""
			ret["code"] = None
			ret["error"] = traceback.format_exc()

	return ret

def encodeToUTF8(content):

	charset = None
	full_html = content

	if content.startswith(codecs.BOM_UTF8):
		charset = "utf8"
	elif content.startswith(codecs.BOM_UTF16):
		charset = "utf16"
	elif content.startswith(codecs.BOM_UTF32):
		charset = "utf32"

	try:
		if charset is None or len(charset.strip()) == 0:
			charset = getEncoding(content)
		else:
			charset = charset.lower().replace("charset", "")

		if charset in ['8859_1', 'euc-kr']:
			charset = 'cp949'

		if charset.lower() in ['gb2312', 'gb1980', 'gbk']:
			charset = 'gbk'

		full_html = content.decode(charset, "replace").encode("utf-8", "xmlcharrefreplace")

	except Exception, msg:
		print "parse Exception : %s %s"%(msg, charset)
		try:
			charset = getEncoding(content)
			full_html = content.decode(charset, "replace").encode("utf-8", "xmlcharrefreplace")
		except Exception, msg:
			print("parse Exception : %s", msg)
	return full_html


def getEncoding(full_html):
	support_encodings = ["utf-8", "euc-kr", "cp949", "shift_jis", "eucjp"]  #, "big5", "big5hkscs", "cyrillic", "koi8_r", "utf_16", "cp1361", "arabic", "cp950", "cp500"]
	try:
		unicode_html = unicode(full_html, "utf8")
		return "utf-8"
	except:
		decoded = False
		for trial_encoding in support_encodings:
			try:
				unicode_html = unicode(full_html, trial_encoding)
				return trial_encoding
			except Exception, msg:
				decoded = False
				continue
		return "euc-kr"


def getJsonEncodedStr(dic):
	return JSONEncoder().encode(dic)


def getContentType(_type):
	ret = ""
	if _type == "json":
		ret = "Content-type: application/json; charset=utf-8\n"
	elif _type == "text":
		ret = "Content-type: text/plain; charset=utf-8\n"
	elif _type == "html":
		ret = "Content-type: text/html; charset=utf-8\n"
	return ret