#!/usr/bin/env python
# coding: utf-8

PATTERN_DATA = """
generator	wordpress.org	<meta name="generator" content="WordPress
generator	drupal.org	<meta name="Generator" content="Drupal
generator	blog.daum.net	type="application/rss+xml" title="RSS" href="http://blog.daum.net
generator	textcube.org	<meta name="generator" content="Textcube
generator	blog.daum.net	<meta property="og:url" content="http://blog.daum.net
generator	wordpress.com	<meta name="generator" content="WordPress.com"
generator	xpressengine.com	meta name="Generator" content="XpressEngine"
generator	xpressengine.com	div class="xe-widget-wrapper
generator	blog.naver.com	type="application/wlwmanifest+xml" href="http://blog.naver.com
generator	blog.naver.com	var blogURL = 'http://blog.naver.com';
generator	tistory.com	var TOP_SSL_URL = 'https://www.tistory.com';
dead	expired	서비스기간이 만료 되었습니다
dead	expired	<div class="subtitle">Speak with a domain specialist!</div>
dead	expired	<title>카페24 :: 대한민국 No.1 카페24 호스팅</title>
dead	expired	var refreshurl = "http://hostinfo.cafe24.com/serviceexpire/servicestop.html
dead	expired	이 도메인은 요금 미납으로 도메인네임 서비스(DNS)가 정지되었습니다.
dead	expired	<IMG src="img/logo.gif" border="0" target="dnsever">
dead	expired	세도의 도메인 파킹</a>을 통해 무료로 제공되는 페이지입니다
dead	invalid	불편을 끼쳐 드려 죄송합니다.
dead	deleted	콘텐츠가 YouTube의 서비스 약관을 위반하여 삭제된 동영상입니다.
dead	invalid	현재 처리 중인 동영상입니다.
category	shopping	본 결제 창은 결제완료 후 자동으로 닫히며,결제 진행 중에 본 결제 창을 닫으시면
"""