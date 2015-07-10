#/usr/bin/env python
# coding: utf8

"""
Detect (Korean) name and email data

Made by. shiwoo park 2015
silva23@naver.com

<주의사항>
- 한글은 한글자당 길이가 3으로 계산된다.
- Regex로 지정할때도 한글 1글자는 길이 3으로 고려해야함.
"""

import re

DEBUG = True
DEBUG = False

CHECK_MAX_LENGTH = 200

def getListStr(_list):
	if not _list:
		return ""
	s = "["
	for elem in _list:
		s += elem+","
	s += "]"
	return s

def getDicStr(_dic):
	if not _dic:
		return ""
	s = "{"
	for k,v in _dic.items():
		s += "%s:%s, "%(k, v)
	s += "}"
	return s

class DataFilter:
	""" Extract writer and writer_email from input string
	"""
	def __init__(self):
		# Case by case 제거 문자열 추가
		self.rmCustomWordList = ["의협신문", "데스크", "지멘스", "와이어"]

		# 일단 제거해야 하는 문자열
		self.rmStrList = ["=", "/", ",", ":", "·", "^", "|", "(", ")", "[", "]", "<", ">", "&nbsp;", "&lt;", "&gt;"] + self.rmCustomWordList
		# 4글자 이상일때 해당 문자열을 포함하면 해당 문자열만 삭제
		self.rmShortWordList = ["온라인","디지털","사회","입력","문화","진행","작가","기획","기자","대표","이사","객원","국장","보도","인턴","편집","위원","사진","뉴스","신문","수습","선임"]
		# 해당 단어로 끝나면 제외
		self.rmEndswithWordList = ["팀","부","신문","일보","뉴스", "요일", "하는"]
		# 온전히 일치할때 제외할 단어들
		self.rmIndieWordList = ["보도국장","프리랜서","글쓴이","작성자","네티즌","논객들","편집인","편집부","편집인"]+self.rmShortWordList + self.rmEndswithWordList 

		# 한글자당 길이를 3으로 계산
		self.absoluteWriterRegex = "\s*?([가-힣]{6,9})\s*기자.*"
		self.absoluteEmailRegex = ".*?([\-\.\w]+@[\w\.\-]+).*"
		self.writerRegex = "^[가-힣]{6,9}$"
		self.emailRegex = "^[\.\w\-]+@[\w\.\-]+$"

	def checkValidWord(self, word):
		isValid = True
		if DEBUG:
			print "WORD : %s"%word

		# 완전일치 시 탈락
		if word:
			if word in self.rmIndieWordList:
				isValid = False
		if DEBUG:
			print "1 exact :%s"%isValid

		# 해당 문자열로 끝나면 탈락
		for endText in self.rmEndswithWordList:
			if word.endswith(endText):
				isValid = False
		if DEBUG:
			print "2 endswith :%s"%isValid

		# 해당 문자열만 삭제하였을때 한글자 이하면 탈락
		for rmText in self.rmShortWordList:
			word = word.replace(rmText, "")
		decoded = word.decode("utf-8")
		if len(decoded) < 2:
			isValid = False
		if DEBUG:
			print "3 contain :%s"%isValid

		m = re.match(self.absoluteEmailRegex, word)
		if m:
			isValid = True

		return (isValid, word)

	def checkWriterAndEmail(self, retDic, candiList):
		if DEBUG:
			print "CAME INTO checkWriterAndEmail "+getListStr(candiList)
		if len(candiList) == 1:
			decoded = candiList[0].decode("utf-8")
			if len(decoded) == 3 or len(decoded) == 2:
				if "writer" not in retDic:
					retDic["writer"] = candiList[0]
				return

		remainderList = []
		for candidate in candiList:
			m = re.match(self.emailRegex, candidate)
			if m:
				if "writer_email" not in retDic:
					retDic["writer_email"] = candidate
					continue
			m = re.match(self.writerRegex, candidate)
			if m:
				decoded = candidate.decode("utf-8")
				if len(decoded) == 3 or len(decoded) == 2:
					if "writer" not in retDic:
						retDic["writer"] = candidate
						continue
					else:
						if (len(retDic["writer"].decode("utf-8")) == 2) and (len(decoded) == 3):
							retDic["writer"] = candidate
			remainderList.append(candidate)
		if DEBUG:
			print "RETURN : %s / %s"%(getDicStr(retDic), getListStr(remainderList))
		return remainderList

	def getData(self, inputStr):
		retDic = dict()  # 최종 반환 데이터
		if len(inputStr) > CHECK_MAX_LENGTH:
			return retDic

		# 기본문자 제거 및 공백 통일
		for rmStr in self.rmStrList:
			inputStr = inputStr.replace(rmStr, " ")
		inputStr = " ".join(inputStr.split())

		if DEBUG:
			print "Input String : "+inputStr

		# 절대 패턴 체크
		m = re.match(self.absoluteWriterRegex, inputStr)
		if m:
			writer = m.group(1)
			result = self.checkValidWord(writer)
			if result[0]:
				retDic["writer"] = result[1]
				if DEBUG:
					print "Absolute WRITER found : "+retDic["writer"]

		m = re.match(self.absoluteEmailRegex, inputStr)
		if m:
			email = m.group(1)
			result = self.checkValidWord(email)
			if result[0]:
				retDic["writer_email"] = result[1]
				if DEBUG:
					print "Absolute EMAIL found : "+retDic["writer_email"]

		if len(retDic) == 2:
			return retDic

		wordList = inputStr.split(" ")

		if DEBUG:
			print "Word List : %s"%(getListStr(wordList))

		collected_word = ""
		collecting = False
		for i in range(len(wordList)):
			word = wordList[i]
			if ("." in word) and ("@" not in word):
				tmpList = word.split(".")
				wordList.remove(word)
				wordList += tmpList

			# 한 글자씩 띄엄띄엄 있을경우 붙여서 후보 추가
			if len(word.decode("utf-8")) < 3:
				new_word = collected_word + word
				if len(new_word.decode("utf-8")) < 5:
					if collected_word:
						collecting = True
					collected_word = new_word
			else:
				if collecting:
					wordList.append(collected_word)
					collected_word = ""
					collecting = False

		if collecting and collected_word:
			wordList.append(collected_word)

		if DEBUG:
			print "Processed Word List : %s"%(getListStr(wordList))

		candidateList = []
		for word in wordList:
			word = word.strip()
			if word:
				result = self.checkValidWord(word)
				if result[0]:
					candidateList.append(result[1])
		if DEBUG:
			print "Final candidates : "+getListStr(candidateList)
			print "Ret DIC : %s"%getDicStr(retDic)
		wordList = self.checkWriterAndEmail(retDic, candidateList)

		return retDic

	def getWriterAndEmail(self, inputStr):
		writerFilter = DataFilter()
		dataDic = writerFilter.getData(inputStr)
		writer = ""
		email = ""
		if "writer" in dataDic:
			writer = dataDic["writer"]
		if "writer_email" in dataDic:
			email = dataDic["writer_email"]
		return (writer, email)


# MAIN------------------------------------------------------------------------------ 
if __name__ == '__main__':
	from resource.data_samples import WRITER_DATA

	dataList = WRITER_DATA.split("\n")
	writerFilter = DataFilter()
	
	for data in dataList:
		data = data.strip()
		if data.startswith("#"):
			continue
		#print data

		if data:
			data_arr = data.split("	")
			input = data_arr[0]
			answer = ""
			if len(data_arr) > 1:
				answer = data_arr[1]
			output = writerFilter.getData(input)
			try:
				assert output["writer"] == answer
			except:
				print "INPUT : %s"%input
				print "OUTPUT : %s"%getDicStr(output)
				print "####################################"