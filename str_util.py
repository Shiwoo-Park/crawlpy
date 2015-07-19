#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def guessEncoding(s, encodings=()):
	if not encodings:
		#['ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8']
		encodings = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp424', 'cp437', 'cp500', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8']
	for encoding in encodings:
		try:
			decoded = s.decode(encoding)
			encoded = decoded.encode("utf-8")
			#print "DECODED : %s / ENCODED : %s"%(decoded, encoded)
			return encoding
		except:
			continue
	return ""

def extractStr(full_text, pattern, rm_whitespace=False):
	"""
	해당 패턴에 처음 매칭되는 문자열 영역을 덩치가 큰 문자열로부터 추출해낸다.
	:param full_text: 전체 텍스트
	:param pattern: 추출해내야 하는 영역만 **** 로 표시한 문자열 패턴
	:return: 추출 영역의 문자열
	"""
	pattern_arr = pattern.split("****")
	if len(pattern_arr) != 2:
		return ""
	if rm_whitespace:
		full_text = ''.join(full_text.split())
	left_pt = pattern_arr[0]
	right_pt = pattern_arr[1]
	s_point = 0
	e_point = len(full_text)
	matched = True

	if left_pt:
		s_point = full_text.find(left_pt) + len(left_pt)
		if s_point < 0:
			matched = False
	if right_pt:
		e_point = full_text.find(right_pt, s_point)
		if e_point < 0:
			matched = False
	#print "Left(%s:%s), Right(%s:%s)"%(left_pt, s_point, right_pt, e_point)
	if matched:
		return full_text[s_point:e_point].strip()
	return ""


def isNumStr(s):
	""" 오직 숫자로만 이루어진 문자열인지 """
	p = "^(\d+)$"
	m = re.match(p, s)
	if m:
		return True
	return False


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

if __name__ == "__main__":
	s = """
	layout.wmode = 'window';
	var qsParam = {};
	qsParam.vid = '6609703DDBE52161ACBA985614D63D9D88FC';
	qsParam.inKey = 'V122100e8178b4959b630693fc12a4e395eb3ec59c431cf1d01805c0e8209b1141cb5693fc12a4e395eb3';
	var flashVar = {};
	flashVar.callbackHandler = 'null';
	flashVar.beginTime = '';
	flashVar.hasThumbnails = '1';
	flashVar.hasRelative = '1';
	flashVar.hasLink = '1';
	flashVar.hasFullScreen = '1';
	flashVar.hasLogo = '1';
	var bean = {};
	bean.layout = layout;
	bean.qsParam = qsParam;
	bean.flashVar = flashVar;
	displayFlashMoviePlayer(bean);
}
</script>
	"""
	p = "qsParam.vid = '****;"
	print extractStr(s, p)

	p = "qsParam.vid='****;"
	print extractStr(s, p, True)
