#/usr/bin/env python
# coding: utf8
"""
NORMALIZE ALL KINDs OF DATE FORMAT

Made by. shiwoo park 2015
silva23@naver.com
"""
import time
import re
from datetime import datetime,timedelta
#import traceback

TIME_TXT_MAX_LEN = 100 # 유입 시간 문자열의 체크 허용 최대길이.
DEBUG = True
DEBUG = False

class DateFactory :

	def __init__(self) :
		self.defaultFormat = "%Y-%m-%d %H:%M:%S" # 기본 출력 날짜포맷 (2014-01-01 13:01:01)
		self.reserveDic = dict()
		self.transWordKVList = [] # dateFormat에 해당하는 변환 대상 문자열 지정.  [ (dateFormat, wordList), ... ]
		self.transNumKVList = [] # number에 해당하는 변환 대상 문자열 지정.  [ (number, wordList), ... ]
		self.patternKVList = [] # dateFormat에 해당하는 REGEX패턴 지정.  [ ( dateFormat, patternList ), ...  ]
		self.agoPatternList = []
		self.lightDelimList = ["[","]","(",")"] # 구분자(lv.1)
		self.heavyDelimList = ["/","-",".",":","+"] # 구분자(lv.2)
		self.rmStrList = [",","&nbsp;","&nbsp","EST","PST","CDT","GMT","at","T"] # 삭제
		self.zeroPadFormatList = ["%m","%d","%H","%M","%S"] # zero padding이 필요한 format
		self.rmPtrnList = []
		self.initFormatStrDic()

	def initFormatStrDic(self) :
		# 영어로의 변환이 필요한 문자열의 경우
		# - 변환전 문자열 : ';' 로 복수개 지정 가능 (길이가 긴것을 먼저 지정)
		# - 변환후 문자열 : reserveDic 내부 같은 key값 list의 동일 index value
		self.transWordKVList.append( ("%p", ["오전","오후"] ) )
		self.transWordKVList.append( ("%B", ["October;Oct;10월", "November;Nov;11월", "December;Dec;12월", "January;Jan;01월;1월", "February;Feb;02월;2월", "March;Mar;03월;3월", "April;Apr;04월;4월", "May;05월;5월", "June;Jun;06월;6월", "July;Jul;07월;7월", "August;Aug;08월;8월", "September;Sep;09월;9월"] ) )
		self.transWordKVList.append( ("%A", ["Sunday;Sun;일요일", "Monday;Mon;월요일", "Tuesday;Tue;화요일;화", "Wednesday;Wed;수요일;수", "Thursday;Thu;목요일;목", "Friday;Fri;금요일;금", "Saturday;Sat;토요일;토"] ) )

		# 숫자로의 변환이 필요한 문자열 경우
		self.transNumKVList.append( ("1", ["한","일","one","a "]) )
		self.transNumKVList.append( ("2", ["두","이","two"]) )
		self.transNumKVList.append( ("3", ["세","삼","three"]) )
		self.transNumKVList.append( ("4", ["네","사","four"]) )
		self.transNumKVList.append( ("5", ["다섯","오","five"]) )
		self.transNumKVList.append( ("6", ["여섯","육","six"]) )
		self.transNumKVList.append( ("7", ["일곱","칠","seven"]) )
		self.transNumKVList.append( ("8", ["여덟","팔","eight"]) )
		self.transNumKVList.append( ("9", ["아홉","구","nine"]) )
		self.transNumKVList.append( ("10", ["열","십","ten"]) )

		# 예약된 날짜 패턴의 경우
		# - 단축어의 경우 모두 Full name 으로 전환하여 예약어 매칭
		self.reserveDic["%A"] = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
		self.reserveDic["%B"] = ["October","November","December","January","February","March","April","May","June","July","August","September"]
		self.reserveDic["%p"] = ["AM","PM","am","pm"]


		# 정규표현식으로 Format인식 : [ (formatStr,regexList), ... ]
		# - 하위 Group 지정 시 동작 1 : 지정된 그룹값을 모두 붙여서 최종 값 제작
		# - 하위 Group 지정 시 동작 2 : key값 의 '$n$' 에 번호에 맞추어 replace  ex) $1$ 는 group(1) 으로 replace
		# - 하위 Group이 없을 시 : found된 문자열 통째가 최종값이 됨.
		# - 숫자값에 대해서는 zeroPadding이 반드시 필요

		td = "[:]" # time Delimiter
		dd = "[\-\.\/]" # date Delimiter

		# 덩치가 큰 패턴
		self.patternKVList.append( ("%y$2$%m$4$%d$6$%H$8$%M$10$%S", [".*?(\d{2})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2})\s*("+"[\/\.]"+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) ) # 13/02/22/15:41:12
		self.patternKVList.append( ("%Y$2$%m$4$%d$6$%H$8$%M$10$%S", [".*?(\d{4})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2})(\s*)(\d{1,2})\s*("+td+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) ) # 2013/02/22 15:41:12
		self.patternKVList.append( ("%Y$2$%m$4$%d$6$%H$8$%M$10$%S$12$", [".*?(\d{4})\s*(년)\s*(\d{1,2})\s*(월)\s*(\d{1,2})\s*(일)\s*(\d{1,2})\s*(시)\s*(\d{1,2})\s*(분)\s*(\d{1,2})\s*(초).*"]) ) # 2015년03월11일 01시19분25초
		self.patternKVList.append( ("%Y$2$%m$4$%d$6$%H$8$%M$10$", [".*?(\d{4})\s*(년)\s*(\d{1,2})\s*(월)\s*(\d{1,2})\s*(일)\s*(\d{1,2})\s*(시)\s*(\d{1,2})\s*(분).*"]) ) # 2015년03월11일 01시19분
		self.patternKVList.append( ("%Y$2$%m$4$%d$6$%H$8$%M", [".*?(\d{4})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2})(\D*)(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) ) # 2013/02/22 15:41
		self.patternKVList.append( ("%Y$2$%m$4$%d$6$", [".*?(\d{4})\s*(년)\s*(\d{1,2})\s*(월)\s*(\d{1,2})\s*(일).*"]) ) # 2015년03월11일
		self.patternKVList.append( ("%Y$2$%m$4$%d", [".*?(\d{4})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2}).*"]) )
		self.patternKVList.append( ("%m$2$%d$4$%Y", [".*?(\d{1,2})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{4}).*"]) )
		self.patternKVList.append( ("%x", [".*\d{2}/\d{2}/\d{2}","\d{2}/\d{2}/\d{4}","\d{2}\.\d{2}\.\d{4}.*"]) )
		self.patternKVList.append( ("%y$2$%m$4$%d", [".*?(\d{2})\s*("+dd+")\s*(\d{1,2})\s*("+dd+")\s*(\d{1,2}).*"]) )
		self.patternKVList.append( ("%H$2$%M$4$%S", [".*?(\d{1,2})\s*("+td+")\s*(\d{1,2})\s*("+td+")\s*(\d{1,2}).*"]) )
		self.patternKVList.append( ("%H$2$%M", ["(\d{1,2})\s*("+td+")\s*(\d{1,2})"]) )
		self.patternKVList.append( ("%Y%m%d", ["\d{8}"]) )

		# 덩치가 작은 패턴
		self.patternKVList.append( ("%Y", ["^\s*(\d{4})\s*년\s*$"]) ) # 2014년
		self.patternKVList.append( ("%m", ["^\s*(\d{1,2})\s*월\s*$"]) ) # 3월, 12월
		self.patternKVList.append( ("%d", ["^\s*(\d{1,2})\s*일\s*$"]) ) # 2일, 11일
		self.patternKVList.append( ("%H", ["^\s*(\d{1,2})\s*시\s*$"]) ) # 2시, 11시
		self.patternKVList.append( ("%M", ["^\s*(\d{1,2})\s*분\s*$"]) ) # 2분, 41분
		self.patternKVList.append( ("%S", ["^\s*(\d{1,2})\s*초\s*$"]) ) # 2초, 51초
		self.patternKVList.append( ("%z", ["[+-]\d{4}","([+-]\d{2}):(\d{2})"]) ) # UTC offset(+|-HHMM) = +0000, -1030, +09:00
		self.patternKVList.append( ("%Y", ["^\s*(\d{4})\s*$"]) )# 2014
		self.patternKVList.append( ("%d;%m;%Y;%H;%M;%S", ["^\s*(\d{1,2})\s*$"]) )# 2014, 2014년

		self.agoPatternList.append( ("%m", [".*?(\d+)\s*(개월|달|months|month)\s*(ago|전).*"]) )
		self.agoPatternList.append( ("%w", [".*?(\d+)\s*(주|주일|weeks|week)\s*(ago|전).*"]) )
		self.agoPatternList.append( ("%d", [".*?(\d+)\s*(일|days|day)\s*(ago|전).*"]) )
		self.agoPatternList.append( ("%H", [".*?(\d+)\s*(시간|hours|hour|hrs|hr)\s*(ago|전).*"]) )
		self.agoPatternList.append( ("%M", [".*?(\d+)\s*(분|minutes|minute|min)\s*(ago|전).*"]) )
		self.agoPatternList.append( ("%S", [".*?(\d+)\s*(초|seconds|second|sec)\s*(ago|전).*"]) )

	# Util functions ===============================================================

	def zeroPadding(self, s) : # 3 > 03
		if len(s) == 1:
			s = "0"+s
		return s

	def isInt(self, s) :
		try :
			i = int(s)
			return True
		except :
			return False

	def hasTimeData(self, unixTimestamp) :
		if unixTimestamp == 0 :
			return False
		datestr = self.getDateByStamp(unixTimestamp)
		if "00:00:00" in datestr :
			return False
		else :
			return True

	def getTimestampByRegexAgoPattern(self, dateStr):
		#print "getTimestampByRegexAgoPattern : ",dateStr
		formatStr = ""
		timeValue = 0

		# 숫자 문자열 변환
		transStr = dateStr
		for number, numStrList in self.transNumKVList :
			for numStr in numStrList :
				if numStr in transStr :
					transStr = transStr.replace(numStr, number)
		#print "After Number Transform : %s"%transStr

		# Ago 패턴 매칭 확인
		for candiStr in [dateStr, transStr] :
			for dFormat, ptList in self.agoPatternList :
				matched = False

				for pt in ptList :
					m = re.match(pt, candiStr)
					if m :
						matched = True
						timeValue = int(m.group(1))
						formatStr = dFormat
						#print "AGO-PATTERN MATCHED [%s : %s]"%(formatStr, timeValue)
						break
				if matched :
					break

		if formatStr and (timeValue > 0):
			nowTime = datetime.now()
			timeGap = None
			if formatStr == "%m" :
				timeGap = timedelta(days=(30 * timeValue))
			elif formatStr == "%w" :
				timeGap = timedelta(weeks=timeValue)
			elif formatStr == "%d" :
				timeGap = timedelta(days=timeValue)
			elif formatStr == "%H" :
				timeGap = timedelta(hours=timeValue)
			elif formatStr == "%M" :
				timeGap = timedelta(minutes=timeValue)
			elif formatStr == "%S" :
				timeGap = timedelta(seconds=timeValue)
			beforeTime = nowTime - timeGap
			return time.mktime(beforeTime.timetuple())
		else :
			return 0

	def getTimestampByStaticAgoPattern(self, dateStr):
		timeGap = 0
		if ("어제" in dateStr) or ("yesterday" in dateStr) :
			timeGap = timedelta(days=1)
		elif ("그저께" in dateStr) or ("그제" in dateStr) :
			timeGap = timedelta(days=2)

		if timeGap != 0 :
			nowTime = datetime.now()
			beforeTime = nowTime - timeGap
			return time.mktime(beforeTime.timetuple())
		else :
			return 0

	# Processing functions ==========================================================

	def analyze(self, dateStr) :
		""" dateStr : Date 문자열
		    return : UnixTimestamp
		"""
		if not dateStr :
			return 0
		dateStr = dateStr.strip()
		if len(dateStr) == 0 :
			return 0
		if len(dateStr) > TIME_TXT_MAX_LEN : # TimeText가 너무길면 처리X
			return 0
		originalString = dateStr
		timestamp = 0

		# 순수히 정규표현식 패턴만으로 포맷 추출 시도
		list1 = self.getFormatList([dateStr])
		if DEBUG:
			print ("LIST1 : " + str(list1) )

		# Normalize 이후 포맷 추출 시도
		normalizedTokenList = self.normalize(dateStr)
		#print ("NORMALIZED STRING LIST: " + str(normalizedTokenList))
		list2 = self.getFormatList(normalizedTokenList)
		if DEBUG:
			print ("LIST2 : " + str(list2) )
		dFormatList = list1 +[("###","###")]+ list2

		# 추출 포맷 모니터링 코드
		#for v1, v2 in dFormatList :
		#	print "[ %s, %s ] "%(v1,v2)

		# 추출된 후보 포맷들에 대해 매칭 진행 (Date format, timestamp) 튜플 저장
		ret1 = [] # list1으로 추출된 값 (only pattern)
		ret2 = [] # list2로 추출된 값 (문자열 분할,분석 포함)
		ptChkFinished = False
		for dateFormat, dateStr in dFormatList :

			if DEBUG:
				print ("DATESTR : %s / FORMAT : %s"%(dateStr, dateFormat) )

			if dateFormat == "###" and dateStr == "###": # List1(패턴체크) 검사
				ptChkFinished = True
				continue

			try :
				if dateFormat in ["%d","%H","%M","%S"] : # 부정확한 단일데이터가 올경우 pass
					continue
				if "%p" in dateFormat : # AM,PM 있을 시 시간값수정
					dateFormat = dateFormat.replace("%H","%I")

				timeObj = time.strptime(dateStr, dateFormat)
				timestamp = time.mktime(timeObj)

				if timestamp < 0 : # 1900-01-01 : 년월일을 오늘날짜로
					now = time.localtime()
					ymdFormat = "%Y-%m-%d"
					ymdStr = time.strftime(ymdFormat, now)
					timeObj = time.strptime(ymdStr+" "+dateStr, ymdFormat+" "+dateFormat)
					timestamp = time.mktime(timeObj)

				# 시간 데이터 유무에 따른 처리
				if ptChkFinished :
					ret2.append( (dateFormat, timestamp) )
				else :
					ret1.append( (dateFormat, timestamp) )
			except Exception, msg :
				#traceback.print_exc()
				pass

		# ret 1과2 중에서 더 좋은것을 뽑는다.
		if DEBUG:
			print ("RET1 : %s / RET2 : %s"%(ret1, ret2) )


		"""
		ret = ret1
		if ret1 == 0 :
			ret = ret2
		if not self.hasTimeData(ret1) and self.hasTimeData(ret2) :
			# ret1은 시간데이터가 없는데 ret2는 있을때
			ret = ret2
		"""

		ret = self.getBestTimestamp(ret1+ret2)

		if ret == 0 :
			ret =  self.getTimestampByRegexAgoPattern(originalString)
		if ret == 0 :
			ret = self.getTimestampByStaticAgoPattern(originalString)

		return ret

	def getBestTimestamp(self, candidateList):
		scoreMax = 0
		bestTimestamp = 0
		for dateFormat, timestamp in candidateList:
			score = 0
			if "%Y" in dateFormat:
				score += 2
				if ("%m" in dateFormat) or ("%B" in dateFormat):
					score += 1
					if ("%d" in dateFormat):
						score += 2
			elif ("%m" in dateFormat) or ("%B" in dateFormat):
				score += 1
				if ("%d" in dateFormat):
					score += 1
			if "%H" in dateFormat:
				score += 2
				if "%M" in dateFormat:
					score += 1
					if "%S" in dateFormat:
						score += 2
			elif "%M" in dateFormat:
				score += 1
				if "%S" in dateFormat:
					score += 1
			if score > scoreMax:
				scoreMax = score
				bestTimestamp = timestamp
			if DEBUG:
				print("DATE FORMAT:%s | SCORE:%s"%(dateFormat, score))
		return bestTimestamp

	def normalize(self, dateStr, level=1) : # 단계별 Normalizing
		""" dateStr : Date 문자열
		    return : normalized Date 문자열

		    level 1 : 삭제
		    level 2 : 삭제 + 구분
		"""
		# 문자열 제거
		for rmStr in self.rmStrList :
			dateStr = dateStr.replace(rmStr," ")
		#print ("AFTER RM : "+dateStr)

		# 1차 구분자 구분
		for ldelim in self.lightDelimList :
			dateStr = dateStr.replace(ldelim," ")
		#print ("AFTER RM LIGHT DELIM : "+dateStr)

		# 공백 통일
		" ".join(dateStr.split())
		wordList = dateStr.split(" ")
		#print ("AFTER NORMALIZE (Lv.1) : "+str(wordList))

		if level > 1 : # 2단계 이상 Normalize Delim
			newWordList = []
			for idx in range(0, len(wordList)) : # 각 Word에 대해
				word = wordList[idx]
				for hdelim in self.heavyDelimList : # 2단계 구분자 구분
					if hdelim in word :
						word = word.replace(hdelim," ")

				# 공백 통일
				" ".join(word.split())
				tmpList = word.split(" ")
				for tmp in tmpList :
					if len(tmp.strip()) != 0 :
						newWordList.append(tmp.strip())

			wordList = newWordList
		#print ("AFTER NORMALIZE (Lv.2) : "+str(newWordList))

		# English Trans 예약어 확인
		newWordList = []
		for word in wordList : # 각 word에 대해
			matched = False

			for dFormat, textList in self.transWordKVList : # 각 Trans Set에 대해
				size = len(textList)
				afterTxtList = self.reserveDic[dFormat]

				for idx in range(0, size) : # 각 매칭 String에 대해
					subList = textList[idx].split(";")
					afterTxt = afterTxtList[idx]

					for beforeTxt in subList :
						if beforeTxt in word :
							word = word.replace(beforeTxt, afterTxt)
							matched = True
							break

					if matched :
						break

				if matched :
					break
			newWordList.append(word)

		wordList = newWordList
		#print ("AFTER ENG TRANSFER : "+str(wordList))

		return wordList


	def getFormatList(self, normalizedTokenList) :
		""" normalizedTokenList : normalized되어 조각난 Time text 리스트
		    return : tokenList가 형성할 수 있는 모든 Time format string list
		"""

		# 각 토큰에 대한 Format 후보 List를 모은다 (모든 경우의 수 Collect)
		candiList = []
		for token in normalizedTokenList :
			setList = self.getPossibleFormatSetList(token) # [ (dateformat, string), .... ]
			if setList :
				if len(candiList) == 0 : # 첫번째 토큰일때
					for setFormat, setStr in setList :
						for f in setFormat.split(";") :
							candiList.append( (f,setStr) )
				else : # 두번째 이후 토큰 처리
					newCandiList = list()
					for candiFormat, candiStr in candiList :
						for setFormat, setStr in setList :
							for f in setFormat.split(";") :
								#print "SET : ",f ,setStr
								# Format String 연결 규칙 설정
								# - 년도 데이터 : %Y, %y
								# - 월 데이터 : %m, %B(%b 포함)
								# - 날짜데이터 > 시간데이터
								# - 같은 포맷 반복 불가
								if f == "%Y" and "%y" in candiFormat :
									continue
								if f == "%Y" and "%y" in candiFormat :
									continue
								if f == "%m" and "%B" in candiFormat :
									continue
								if f == "%B" and "%m" in candiFormat :
									continue
								if f in ["%H","%M","%S"] : # 시간데이터가 날짜데이터보다 우선할수 없음
									if "%d" not in candiFormat :
										continue
									if ("%m" not in candiFormat) and ("%B" not in candiFormat) :
										continue
								if f not in candiFormat :
									newCandiList.append( (candiFormat+" "+f, candiStr+" "+setStr) )
								#print ("NEW CANDI : "+str(newCandiList))
					candiList = newCandiList
		if DEBUG:
			print ("CANDIDATE LIST : "+str(candiList))

		return candiList

	# 전체 String 형성을 위한 DateFormat 경우의 수를 만든다.


	def getPossibleFormatSetList(self, s) : # 3월 > March
		""" s : 최소단위 구분 문자열
		    return : 대입 가능 date format string LIST
		"""
		if len(s.strip()) == 0 :
			return None

		# 패턴 매칭
		ret = []
		for dFormat, ptList in self.patternKVList :
			matched = False

			for pt in ptList :
				m = re.match(pt, s)
				if m :
					matched = True
					if dFormat in ["%z"] : # 토큰으로 고려하지 않을 dateFormat
						break

					newStr = ""
					if m.lastindex :
						for i in range(1, m.lastindex+1) :
							dFormat = dFormat.replace("$%s$"%i, m.group(i))
							groupStr = m.group(i)
							if self.isInt( groupStr ) :
								groupStr = self.zeroPadding(groupStr)
							newStr += groupStr
					else :
						newStr = m.group(0)
					ret.append( (dFormat, newStr) )
					break
				#if matched :
				#	break

		# 예약어 매칭
		for dFormat, txtList in self.reserveDic.items() :
			for text in txtList :
				if text == s :
					ret.append( (dFormat, text) )

		#print ("TOKEN : "+s+" : "+str(ret) )
		return ret



	# Output functions ===========================================================

	def getUnixTimestamp(self, dateStr) :
		return int( self.analyze(dateStr) )

	def getDate(self, dateStr, dateFormat=None) :
		unixTimestamp = self.analyze(dateStr)
		return self.getDateByStamp(unixTimestamp, dateFormat)

	def getDateByStamp(self, timestamp, dateFormat=None) :
		if dateFormat :
			return time.strftime(dateFormat, time.localtime(int(timestamp)))
		else :
			return time.strftime(self.defaultFormat, time.localtime(int(timestamp)))

if __name__ == "__main__":
	from resource_date import TIME_AGODATA, TIME_DATEDATA
	set_err = """
	"""


	set1 = """
	2015/1/15 13:30"
	September 11, 2014 at 6:41 pm
	2014년 12월 1일
	<무카스미디어 = 정길수 수습기자> (2015-03-17 오후 6:35)
	ten minutes ago
	19 분 전
	2015. 04.05(일) 19:32
	2015. 04.16. 18:49
	입력시간 : 2015. 04.16. 18:49
	Mon 03 Feb 2014 19:01:00 -0500
	"""

	set2 = """
	Mon 03 Feb 2014 19:01:00 -0500
	"""

	dFac = DateFactory()
	#testData = set_err
	#testData = set2
	testData = TIME_AGODATA
	testData = set1
	testData = set2
	testData = TIME_DATEDATA
	#print testData

	for timeTxt in testData.split("\n") :
		if timeTxt is None :
			continue
		timeTxt = timeTxt.strip()
		if len(timeTxt) == 0 :
			continue
		if DEBUG:
			print "@@@ INPUT STRING : %s @@@"%timeTxt
		unixTxt = dFac.getUnixTimestamp(timeTxt)
		print ""
		dateTxt = dFac.getDate(timeTxt)
		print "#################################"
		print " INPUT STRING : ", timeTxt
		print " UNIX TIMESTAMP : ", unixTxt
		print " DEFAULT DATE : ", dateTxt
		print "#################################"
