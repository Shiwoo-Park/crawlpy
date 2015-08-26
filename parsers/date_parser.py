#/usr/bin/env python
# coding: utf-8

"""
NORMALIZE ALL KINDs OF DATE FORMAT

Made by. shiwoo park 2015
silva23@naver.com
"""

import time
import re
from datetime import datetime,timedelta
import traceback

TIME_TXT_MAX_LEN = 100  # 유입 시간 문자열의 체크 허용 최대길이.

DEBUG = True
DEBUG = False

DEEP_DEBUG = True
DEEP_DEBUG = False

def getListStr(l):
	s = "["
	for elem in l:
		s += ", %s"%str(elem)
	return s+"]"

class DateParser:

	def __init__(self):
		self.default_format = "%Y-%m-%d %H:%M:%S" # 기본 출력 날짜포맷 (2014-01-01 13:01:01)
		self.reserve_dic = dict()
		self.trans_word_kvlist = []  # dateFormat에 해당하는 변환 대상 문자열 지정.  [ (dateFormat, wordList), ... ]
		self.trans_num_kvlist = []  # number에 해당하는 변환 대상 문자열 지정.  [ (number, wordList), ... ]
		self.pattern_kvlist = []  # dateFormat에 해당하는 REGEX패턴 지정.  [ ( dateFormat, patternList ), ...  ]
		self.ago_pattern_list = []
		self.light_delim_list = ["[","]","(",")"]  # 구분자(lv.1)
		self.heavy_delim_list = ["/","-",".",":","+"]  # 구분자(lv.2)
		self.rm_str_list = [",","&nbsp;","&nbsp","EST","PST","CDT","GMT","at","T"]  # 삭제
		self.zeropad_format_list = ["%m","%d","%H","%M","%S"]  # zero padding이 필요한 format

		self.initFormatStrDic()

	def initFormatStrDic(self):
		# 영어로의 변환이 필요한 문자열의 경우
		# - 변환전 문자열 : ';' 로 복수개 지정 가능 (길이가 긴것을 먼저 지정)
		# - 변환후 문자열 : reserveDic 내부 같은 key값 list의 동일 index value
		self.trans_word_kvlist.append( ("%p", ["오전","오후"] ) )
		self.trans_word_kvlist.append( ("%B", ["October;october;Oct;10월", "November;november;Nov;11월", "December;december;Dec;12월", "January;january;Jan;01월;1월", "February;february;Feb;02월;2월", "March;march;Mar;03월;3월", "April;april;Apr;04월;4월", "May;05월;5월", "June;Jun;06월;6월", "July;Jul;07월;7월", "August;Aug;08월;8월", "September;september;Sep;09월;9월"] ) )
		self.trans_word_kvlist.append( ("%A", ["Sunday;Sun;일요일", "Monday;Mon;월요일", "Tuesday;Tue;화요일;화", "Wednesday;Wed;수요일;수", "Thursday;Thu;목요일;목", "Friday;Fri;금요일;금", "Saturday;Sat;토요일;토"] ) )

		# 숫자로의 변환이 필요한 문자열 경우
		self.trans_num_kvlist.append( ("1", ["한","일","one","a "]) )
		self.trans_num_kvlist.append( ("2", ["두","이","two"]) )
		self.trans_num_kvlist.append( ("3", ["세","삼","three"]) )
		self.trans_num_kvlist.append( ("4", ["네","사","four"]) )
		self.trans_num_kvlist.append( ("5", ["다섯","오","five"]) )
		self.trans_num_kvlist.append( ("6", ["여섯","육","six"]) )
		self.trans_num_kvlist.append( ("7", ["일곱","칠","seven"]) )
		self.trans_num_kvlist.append( ("8", ["여덟","팔","eight"]) )
		self.trans_num_kvlist.append( ("9", ["아홉","구","nine"]) )
		self.trans_num_kvlist.append( ("10", ["열","십","ten"]) )

		# 예약된 날짜 패턴의 경우
		# - 단축어의 경우 모두 Full name 으로 전환하여 예약어 매칭
		self.reserve_dic["%A"] = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
		self.reserve_dic["%B"] = ["October","November","December","January","February","March","April","May","June","July","August","September"]
		self.reserve_dic["%p"] = ["AM","PM","am","pm"]


		# 정규표현식으로 Format인식 : [ (formatStr,regexList), ... ]
		# - 하위 Group 지정 시 동작 1 : 지정된 그룹값을 모두 붙여서 최종 값 제작
		# - 하위 Group 지정 시 동작 2 : key값 의 '$n$' 에 번호에 맞추어 replace  ex) $1$ 는 group(1) 으로 replace
		# - 하위 Group이 없을 시 : found된 문자열 통째가 최종값이 됨.
		# - 숫자값에 대해서는 zeroPadding이 반드시 필요

		td = "[:]"  # time Delimiter
		dd = "[\-\.\/]"  # date Delimiter

		# 덩치가 큰 패턴

		self.pattern_kvlist.append( ("%y$2$%m$4$%d$6$%H$8$%M$10$%S", [".*?(\d{2})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2})(\D+)(\d{1,2})\s*("+td+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) )  # 13/02/22/15:41:12
		self.pattern_kvlist.append( ("%Y$2$%m$4$%d$6$%H$8$%M$10$%S", [".*?(\d{4})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2})(\D+)(\d{1,2})\s*("+td+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) ) # 2013/02/22 15:41:12
		self.pattern_kvlist.append( ("%Y$2$%m$4$%d$6$%H$8$%M$10$%S$12$", [".*?(\d{4})\s*(년)\s*(\d{1,2})\s*(월)\s*(\d{1,2})\s*(일)\s*(\d{1,2})\s*(시)\s*(\d{1,2})\s*(분)\s*(\d{1,2})\s*(초).*"]) ) # 2015년03월11일 01시19분25초
		self.pattern_kvlist.append( ("%Y$2$%m$4$%d$6$%H$8$%M$10$", [".*?(\d{4})\s*(년)\s*(\d{1,2})\s*(월)\s*(\d{1,2})\s*(일)\s*(\d{1,2})\s*(시)\s*(\d{1,2})\s*(분).*"]) ) # 2015년03월11일 01시19분
		self.pattern_kvlist.append( ("%Y$2$%m$4$%d$6$%H$8$%M", [".*?(\d{4})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2})(\D*)(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) ) # 2013/02/22 15:41
		self.pattern_kvlist.append( ("%Y$2$%m$4$%d$6$", [".*?(\d{4})\s*(년)\s*(\d{1,2})\s*(월)\s*(\d{1,2})\s*(일).*"]) ) # 2015년03월11일
		self.pattern_kvlist.append( ("%Y$2$%m$4$%d", [".*?(\d{4})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2}).*"]) )
		self.pattern_kvlist.append( ("%m$2$%d$4$%Y", [".*?(\d{1,2})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{4}).*"]) )
		self.pattern_kvlist.append( ("%x", [".*\d{2}/\d{2}/\d{2}", "\d{2}/\d{2}/\d{4}", "\d{2}\.\d{2}\.\d{4}.*"]) )
		self.pattern_kvlist.append( ("%y$2$%m$4$%d", [".*?(\d{2})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2}).*"]) )
		self.pattern_kvlist.append( ("%m$2$%d", ["(\d{1,2})\s*("+dd+")\s*(\d{1,2})"+dd+"?"]) )
		self.pattern_kvlist.append( ("%H$2$%M$4$%S$6$", [".*?(\d{1,2})\s*(시)\s*(\d{1,2})\s*(분)\s*(\d{1,2})\s*(초).*"]) )
		self.pattern_kvlist.append( ("%H$2$%M$4$%S", [".*?\D(\d{1,2})\s*("+td+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) )
		self.pattern_kvlist.append( ("%H$2$%M$4$%S", ["\s*?(\d{1,2})\s*("+td+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) )
		self.pattern_kvlist.append( ("%H$2$%M", ["(\d{1,2})\s*("+td+")\s*(\d{1,2})"]) )
		self.pattern_kvlist.append( ("%Y%m%d", ["\d{8}"]) )
		self.pattern_kvlist.append( ("%Y:%m:%d", ["\d{4}:\d{1,2}:\d{1,2}"]) )  # 2006:09:05
		self.pattern_kvlist.append( ("%Y%m%d", ["어제|yesterday|엊그제|그저께|그제"]) )

		# 덩치가 작은 패턴
		self.pattern_kvlist.append( ("%Y", ["^\s*(\d{4})\s*년\s*$"]) )  # 2014년
		self.pattern_kvlist.append( ("%Y", ["^\s*(\d{4})\s*"+dd+"\s*$"]) )  # 2014년
		self.pattern_kvlist.append( ("%m", ["^\s*(\d{1,2})\s*월호?\s*$"]) )  # 3월, 12월
		self.pattern_kvlist.append( ("%d", ["^\s*(\d{1,2})\s*일\s*$"]) )  # 2일, 11일
		self.pattern_kvlist.append( ("%H", ["^\s*(\d{1,2})\s*시\s*$"]) )  # 2시, 11시
		self.pattern_kvlist.append( ("%M", ["^\s*(\d{1,2})\s*분\s*$"]) )  # 2분, 41분
		self.pattern_kvlist.append( ("%S", ["^\s*(\d{1,2})\s*초\s*$"]) )  # 2초, 51초
		self.pattern_kvlist.append( ("%z", ["[+-]\d{4}","([+-]\d{2}):(\d{2})"]) ) # UTC offset(+|-HHMM) = +0000, -1030, +09:00
		self.pattern_kvlist.append( ("%Y", ["^\s*(\d{4})\s*$"]) )# 2014
		self.pattern_kvlist.append( ("%d;%m;%y;%H;%M;%S", ["^\s*(\d{1,2})\s*$"]) )# 두글자 숫자

		self.ago_pattern_list.append( ("%m", [".*?(\d+)\s*(개월|달|months|month)\s*(ago|전).*"]) )
		self.ago_pattern_list.append( ("%w", [".*?(\d+)\s*(주|주일|weeks|week)\s*(ago|전).*"]) )
		self.ago_pattern_list.append( ("%d", [".*?(\d+)\s*(일|days|day)\s*(ago|전).*"]) )
		self.ago_pattern_list.append( ("%H", [".*?(\d+)\s*(시간|hours|hour|hrs|hr)\s*(ago|전).*"]) )
		self.ago_pattern_list.append( ("%M", [".*?(\d+)\s*(분|minutes|minute|min)\s*(ago|전).*"]) )
		self.ago_pattern_list.append( ("%S", [".*?(\d+)\s*(초|seconds|second|sec)\s*(ago|전).*"]) )

	# Util functions ===============================================================

	def zeroPadding(self, s):  # 3 > 03
		if len(s) == 1:
			s = "0" + s
		return s

	def isInt(self, s):
		try:
			i = int(s)
			return True
		except :
			return False

	def hasTimeData(self, timestamp):
		if timestamp == 0:
			return False
		date_str = self.getDateByStamp(timestamp)
		if "00:00:00" in date_str:
			return False
		else:
			return True

	def getTimestampByRegexAgoPattern(self, date_str):
		#print "getTimestampByRegexAgoPattern : ",dateStr

		format_str = ""
		time_value = 0

		# 숫자 문자열 변환
		trans_str = date_str
		for number, num_str_list in self.trans_num_kvlist:
			for num_str in num_str_list:
				if num_str in trans_str:
					trans_str = trans_str.replace(num_str, number)
		#print "After Number Transform : %s"%trans_str

		# Ago 패턴 매칭 확인
		for candi_str in [date_str, trans_str]:
			for date_format, pt_list in self.ago_pattern_list:
				matched = False

				for pt in pt_list:
					m = re.match(pt, candi_str)
					if m:
						matched = True
						time_value = int(m.group(1))
						format_str = date_format
						#print "AGO-PATTERN MATCHED [%s : %s]"%(format_str, time_value)
						break
				if matched :
					break

		if format_str and (time_value > 0):
			now_time = datetime.now()
			time_gap = None
			if format_str == "%m":
				time_gap = timedelta(days=(30 * time_value))
			elif format_str == "%w":
				time_gap = timedelta(weeks=time_value)
			elif format_str == "%d":
				time_gap = timedelta(days=time_value)
			elif format_str == "%H":
				time_gap = timedelta(hours=time_value)
			elif format_str == "%M":
				time_gap = timedelta(minutes=time_value)
			elif format_str == "%S":
				time_gap = timedelta(seconds=time_value)
			before_time = now_time - time_gap
			return time.mktime(before_time.timetuple())
		else:
			return 0

	# Processing functions ==========================================================


	def getPatternMatchingResult(self, date_format_list):
		# 추출된 후보 포맷들에 대해 매칭 진행 (Date format, timestamp) 튜플 저장
		ret = []
		now = time.localtime()
		for date_format, dateStr in date_format_list:

			if DEBUG and not DEEP_DEBUG:
				print ("		DATESTR : %s / FORMAT : %s"%(dateStr, date_format))

			try:
				if date_format in ["%m", "%B", "%d", "%H", "%M", "%S"]:  # 부정확한 단일데이터가 올경우 pass
					continue
				if ("%Y" not in date_format) and ("%y" not in date_format):
					if ("%B" in date_format) or ("%m" in date_format) or ("%d" in date_format):
						continue
				if ("%B" not in date_format) and ("%m" not in date_format):
					if "%d" in date_format:
						continue
				if "%p" in date_format:  # AM,PM 있을 시 시간값수정
					date_format = date_format.replace("%H", "%I")

				#print "KKKKKKKK %s // %s"%(dateStr, date_format)
				time_obj = time.strptime(dateStr, date_format)
				if (time_obj.tm_year == 1900) and (time_obj.tm_mon == 1) and (time_obj.tm_mday == 1):
					dateStr = "%s-%s-%s %s:%s:%s"%(now.tm_year, now.tm_mon, now.tm_mday, time_obj.tm_hour, time_obj.tm_min, time_obj.tm_sec)
					time_obj = time.strptime(dateStr, self.default_format)
				timestamp = time.mktime(time_obj)

				if timestamp < 0:  # 1900-01-01 : 년월일을 오늘날짜로
					ymd_format = "%Y-%m-%d"
					ymd_str = time.strftime(ymd_format, now)
					time_obj = time.strptime(ymd_str+" "+dateStr, ymd_format+" "+date_format)
					timestamp = time.mktime(time_obj)

				ret.append((date_format, timestamp))
			except Exception, msg:
				if DEBUG:
					traceback.print_exc()
				pass

		if DEBUG:
			print ("getPatternMatchingResult()\n	INPUT LIST : %s\n	RET LIST : %s"%(getListStr(date_format_list), ret))
		return ret


	def analyze(self, date_str):
		""" dateStr : Date 문자열
		    return : UnixTimestamp
		"""
		if not date_str:
			return 0
		date_str = date_str.strip()
		if len(date_str) == 0:
			return 0
		if len(date_str) > TIME_TXT_MAX_LEN:  # TimeText가 너무길면 처리X
			return 0
		original_string = date_str

		# 순수히 정규표현식 패턴만으로 포맷 추출 시도
		if DEBUG:
			print "========== EXTRACT STEP 1 =========="
		list1 = self.getFormatList([date_str])
		ret1 = self.getPatternMatchingResult(list1)

		if DEBUG:
			print "========== EXTRACT STEP 2 =========="
		# Lv.1 Normalize 이후 포맷 추출 시도
		original_date_str = date_str
		normalized_token_list = self.normalize(date_str)
		list2 = self.getFormatList(normalized_token_list)
		ret2 = self.getPatternMatchingResult(list2)

		ret_timestamp, ret_format = self.getBestTimestamp(ret1+ret2)

		# Lv.2 Normalize 이후 포맷 추출 시도
		if (ret_timestamp == 0) or (len(ret_format) == 2):
			if DEBUG:
				print "========== EXTRACT STEP 3 =========="
			normalized_token_list_lv2 = self.normalize(original_date_str, level=2)
			list3 = self.getFormatList(normalized_token_list_lv2)
			ret3 = self.getPatternMatchingResult(list3)
			lv2_ret_timestamp, lv2_ret_format = self.getBestTimestamp(ret3)
			if len(lv2_ret_format) > 2:
				ret_timestamp = lv2_ret_timestamp

		if ret_timestamp == 0:
			ret_timestamp = self.getTimestampByRegexAgoPattern(original_string)

		# 미래날짜인 경우 0 처리 ('년월일시분' 정보가 있다면 승인)
		if ret_timestamp > int(time.time()):
			if DEBUG:
				print "Future time : %s(%s)"%(self.getDateByStamp(ret_timestamp), ret_timestamp)
			if not self.isValidFutureTime(ret_timestamp):
				ret_timestamp = 0

		return ret_timestamp

	def getBestTimestamp(self, candidate_list):
		# 각각의 후보에 대해 점수를 매긴다
		max_score = 0
		best_timestamp = 0
		best_date_format = ""
		for date_format, timestamp in candidate_list:
			score = 0
			# 날짜에 대한 검사 (반드시 년 > 월 > 일 순차적으로 모두 들어있어야 함.)
			if ("%Y" in date_format) or ("%y" in date_format):
				score += 2
				if ("%m" in date_format) or ("%B" in date_format):
					score += 1
					if ("%d" in date_format):
						score += 2
			# 시간에 대한 검사 (반드시 시 > 분 > 초 순차적으로 모두 들어있어야 함.)
			if ("%H" in date_format) or ("%I" in date_format):
				score += 2
				if "%p" in date_format:
					score += 1
				if "%M" in date_format:
					score += 1
					if "%S" in date_format:
						score += 2

			if score > max_score:
				max_score = score
				best_timestamp = timestamp
				best_date_format = date_format

			if DEBUG:
				print("DATE FORMAT:%s | SCORE:%s"%(date_format, score))
		return best_timestamp, best_date_format

	def normalize(self, date_str, level=1, elem_limit=5):  # 단계별 Normalizing
		""" dateStr : Date 문자열
		    return : normalized Date 문자열

		    level 1 : 삭제
		    level 2 : 삭제 + 구분
		"""
		# 문자열 제거
		for rmstr in self.rm_str_list:
			date_str = date_str.replace(rmstr, " ")
		#print ("AFTER RM : "+dateStr)

		# 1차 구분자 구분
		for ldelim in self.light_delim_list:
			date_str = date_str.replace(ldelim, " ")
		#print ("AFTER RM LIGHT DELIM : "+dateStr)

		# 공백 통일
		" ".join(date_str.split())
		word_list = date_str.split(" ")
		#print ("AFTER NORMALIZE (Lv.1) : "+str(word_list))

		if level > 1:  # 2단계 이상 Normalize Delim
			new_word_list = []
			for idx in range(0, len(word_list)):  # 각 Word에 대해
				word = word_list[idx]
				for hdelim in self.heavy_delim_list:  # 2단계 구분자 구분
					if hdelim in word:
						word = word.replace(hdelim, " ")

				# 공백 통일
				" ".join(word.split())
				tmp_list = word.split(" ")
				for tmp in tmp_list:
					if len(tmp.strip()) != 0:
						new_word_list.append(tmp.strip())
				if len(new_word_list) > elem_limit:
					return []

			word_list = new_word_list
		#print ("AFTER NORMALIZE (Lv.2) : "+str(new_word_list))

		# English Trans 예약어 확인
		new_word_list = []
		for word in word_list:  # 각 word에 대해
			matched = False

			for date_format, text_list in self.trans_word_kvlist:  # 각 Trans Set에 대해
				size = len(text_list)
				after_txt_list = self.reserve_dic[date_format]

				for idx in range(0, size):  # 각 매칭 String에 대해
					sub_list = text_list[idx].split(";")  # October;Oct;10월
					after_txt = after_txt_list[idx]

					for before_txt in sub_list:
						if before_txt == word:
							word = word.replace(before_txt, after_txt)
							matched = True
							break

					if matched:
						break

				if matched:
					break
			new_word_list.append(word)

		word_list = new_word_list
		#print ("AFTER ENG TRANSFER : "+str(word_list))
		if DEBUG:
			print ("normalize()\n	INPUT STRING : %s\n	NORMALIZED STRING LIST (Lv.%s): %s"%(date_str, level, getListStr(word_list)))

		return word_list


	def getFormatList(self, normalized_token_list):
		""" normalizedTokenList : normalized되어 조각난 Time text 리스트
		    return : tokenList가 형성할 수 있는 모든 Time format string list
		"""

		# 각 토큰에 대한 Format 후보 List를 모은다 (모든 경우의 수 Collect)
		candi_list = []
		for token in normalized_token_list:
			possible_format_set_list = self.getPossibleFormatSetList(token)  # [ (dateformat, string), .... ]
			if possible_format_set_list:
				if len(candi_list) == 0:  # 첫번째 토큰일때
					for promising_date_formats, promising_date_str in possible_format_set_list:
						promising_date_format_list = promising_date_formats.split(";")
						for promising_date_format in promising_date_format_list:
							candi_list.append((promising_date_format, promising_date_str))
				else:  # 두번째 이후 토큰 처리
					new_candi_list = list(candi_list)
					for candi_format, candiStr in candi_list:
						for promising_date_formats, promising_date_str in possible_format_set_list:
							# 하나의 정규표현식에 여러 date format이 매칭되는 경우 발생 가능
							# (ex. %d;%m;%y;%H;%M;%S, 한자리 혹은 두자리 숫자)
							promising_date_format_list = promising_date_formats.split(";")
							for promising_date_format in promising_date_format_list:
								# Format String 연결 규칙 설정
								# - 년도 데이터 : %Y, %y
								# - 월 데이터 : %m, %B(%b 포함)
								# - 날짜데이터 > 시간데이터
								# - 같은 포맷 반복 불가
								if promising_date_format in candi_format:
									continue
								if (promising_date_format == "%Y"):
									if ("%y" in candi_format) or len(promising_date_str) != 4:
										continue
								if (promising_date_format == "%y") and ("%Y" in candi_format):
									continue
								if (promising_date_format == "%m") and ("%B" in candi_format):
									continue
								if (promising_date_format == "%B") and ("%m" in candi_format):
									continue
								if ("%H" in promising_date_format) and ("%H" in candi_format):
									continue
								if promising_date_format in ["%H", "%M", "%S"]:  # 시간데이터가 날짜데이터보다 우선할수 없음
									if "%d" not in candi_format:
										continue
									elif ("%m" not in candi_format) and ("%B" not in candi_format):
										continue

								if promising_date_format not in candi_format:
									new_candi_list.append( (candi_format+" "+promising_date_format, candiStr+" "+promising_date_str) )

					candi_list = new_candi_list

			if DEEP_DEBUG:
				print "			TOKEN : %s, CANDI_LIST : %s"%(token, getListStr(candi_list))

		# 부정확한 후보군 제거
		# - 날짜 데이터가 2개이하인경우는 모두 탈락
		# - 년+월, 시+분 일 경우만 통과
		# - 년도가 월보다 왼쪽, 시간이 분보다 왼쪽에 출현해야함.
		ret_list = []
		for d_format, d_str in candi_list:
			data_count = d_format.count("%")
			if "%p" in d_format:
				data_count -= 1

			if data_count > 2:
				ret_list.append((d_format, d_str))

			elif ("%y" in d_format) or ("%Y" in d_format):
				year_pos = d_format.find("%y")
				if year_pos < 0:
					year_pos = d_format.find("%Y")
				if ("%m" in d_format) or ("%B" in d_format):
					month_pos = d_format.find("%m")
					if month_pos < 0:
						ret_list.append((d_format, d_str))
					elif year_pos < month_pos:
						ret_list.append((d_format, d_str))

			elif ("%H" in d_format) or ("%I" in d_format):
				hour_pos = d_format.find("%y")
				if hour_pos < 0:
					hour_pos = d_format.find("%Y")
				if "%M" in d_format:
					min_pos = d_format.find("%M")
					if hour_pos < min_pos:
						ret_list.append((d_format, d_str))

		if DEBUG:
			print ("getFormatList()\n	INPUT LIST : %s\n	CANDIDATE LIST : %s"%(getListStr(normalized_token_list), getListStr(ret_list)))

		return ret_list

	# 전체 String 형성을 위한 DateFormat 경우의 수를 만든다.


	def getPossibleFormatSetList(self, token):  # 3월 > March
		""" s : 최소단위 구분 문자열
		    return : 대입 가능 date format string LIST
		"""
		if len(token.strip()) == 0:
			return None

		# 패턴 매칭
		ret = []
		if DEEP_DEBUG:
			print "	getPossibleFormatSetList(%s)"%token
		for date_format, pt_list in self.pattern_kvlist:
			matched = False

			for pt in pt_list:
				m = re.match(pt, token)
				if m:
					if DEEP_DEBUG:
						print "		matched : %s | %s"%(date_format, pt)
					matched = True
					if date_format in ["%z"]:  # 토큰으로 고려하지 않을 dateFormat
						break

					new_str = ""
					if m.lastindex:
						for i in range(1, m.lastindex+1):
							date_format = date_format.replace("$%s$"%i, m.group(i))
							group_str = m.group(i)
							if self.isInt(group_str):
								group_str = self.zeroPadding(group_str)
							new_str += group_str
					else:
						new_str = m.group(0)
						if (new_str == "어제") or (new_str == "yesterday"):
							target_date = datetime.now() - timedelta(days=1)
							new_str = target_date.strftime("%Y%m%d")
						elif (new_str == "그제") or (new_str == "그저께") or (new_str == "엊그제"):
							target_date = datetime.now() - timedelta(days=2)
							new_str = target_date.strftime("%Y%m%d")
					ret.append((date_format, new_str))
					if DEEP_DEBUG:
						print "		CANDI APPEND : %s | %s"%(date_format, new_str)
					break

		# 예약어 매칭
		for date_format, txt_list in self.reserve_dic.items():
			for text in txt_list:
				if text == token:
					ret.append( (date_format, text) )
					if DEEP_DEBUG:
						print "		CANDI APPEND : %s | %s"%(date_format, text)

		if DEEP_DEBUG:
			print ("		CANDI LIST : %s"%(getListStr(ret)))

		return ret

	def isValidFutureTime(self, timestamp):
		# 년월일시분 정보를 모두 포함하고 있으면 valid
		time_obj = time.localtime(int(timestamp))
		if time_obj.tm_min == 0:
			return False
		if time_obj.tm_hour == 0:
			return False
		if time_obj.tm_mday == 0:
			return False
		if time_obj.tm_hour == 0:
			return False
		if time_obj.tm_year == 0:
			return False
		return True

	# Output functions ===========================================================

	def getUnixTimestamp(self, dateStr):
		return int( self.analyze(dateStr) )

	def getDate(self, dateStr, dateFormat=None):
		unixTimestamp = self.analyze(dateStr)
		return self.getDateByStamp(unixTimestamp, dateFormat)

	def getDateByStamp(self, timestamp, dateFormat=None):
		if dateFormat:
			return time.strftime(dateFormat, time.localtime(int(timestamp)))
		else:
			return time.strftime(self.default_format, time.localtime(int(timestamp)))

if __name__ == "__main__":
	from resource.date_samples import TIME_AGODATA, TIME_DATEDATA, ASSERT_TIME_DATEDATA

	set_err = """
	"""

	d_parser = DateParser()

	ASSERT_MODE = "a"

	if ASSERT_MODE:
		test_data = ASSERT_TIME_DATEDATA
		error_count = 0
		for line in test_data.split("\n"):
			if line is None:
				continue
			line = line.strip()
			if len(line) == 0:
				continue
			if line.startswith("#"):
				continue
			tmpList = line.split("	")
			time_txt = tmpList[0]
			outputTimeTxt = d_parser.getDate(time_txt)
			answerTimeTxt = tmpList[1]
			try:
				assert outputTimeTxt == answerTimeTxt
			except:
				error_count += 1
				print "INPUT STRING :	%s"%time_txt
				print "OUTPUT STRING :	%s"%outputTimeTxt
				print "ANSWER STRING :	%s\n"%answerTimeTxt
		print "CHECK FINISHED : %s ERRORS"%error_count

	else:
		test_data = TIME_AGODATA
		test_data = TIME_DATEDATA
		test_data = set_err
		for time_txt in test_data.split("\n"):
			if time_txt is None:
				continue
			time_txt = time_txt.strip()
			if len(time_txt) == 0:
				continue
			if DEBUG:
				print "@@@ INPUT STRING : %s @@@"%time_txt
			timestamp = d_parser.getUnixTimestamp(time_txt)
			print ""
			date_txt = d_parser.getDateByStamp(timestamp)
			print "#################################"
			print "	%s\n	%s (%s)"%(time_txt, date_txt, timestamp)
			print "#################################"
			#"""
