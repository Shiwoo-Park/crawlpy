#/usr/bin/env python
# coding: utf-8

import urllib2
import traceback

ESCAPE_CHARS = ":/?#[]@!$&'()*+,;=\\%~"

def downloadPage(url, _userAgent="", retry=1):
	"""
	:param url: visit URL
	:param _userAgent: UserAgent String
	ex1. Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36
	ex2. Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30
	:param retry: count

	:return: dictionary (contains data by each key)
	- header : response header
	- content : html
	- url : response url
	- code : httpcode
	- error : error msg(error stack)
	"""

	url = urllib2.quote(url, safe=ESCAPE_CHARS)
	opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(), urllib2.HTTPCookieProcessor())
	request = urllib2.Request(url)
	if _userAgent:
		request.add_header("User-agent", _userAgent)

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
			ret["content"] = ""
			ret["code"] = None
			ret["error"] = traceback.format_exc()

	return ret