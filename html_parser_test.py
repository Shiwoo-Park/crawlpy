#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
	# instantiate the parser and fed it some HTML
	from utils.http_client import downloadPage
	from parsers.psw_html_parser import PswHtmlParser
	from utils.io_util import saveIntoFile

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

	#testHtml = readFile("D:\logs\\test.html")

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
	savepath = "C:\Users\jsilva\PycharmProjects\html_parse_out.txt"
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
 