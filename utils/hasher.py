#!/usr/bin/env python
#coding: utf8
"""
HASH : A string into a hashed string

usage :
	hasher = Hasher(hash_type)
	hashdate = hasher.digest(string)

possible hash type:
	MD5 = 128-bit message digest
	SHA1 = 160-bit message digest
	SHA224 = 224-bit message digest
	SHA256 = 256-bit message digest
	SHA384 = 384-bit message digest 
	SHA512 = 512-bit message digest
"""
# future statement must top on the file
from __future__ import with_statement 
import os, sys
import hashlib 
import threading
import urlparse

HASHTYPE_MD5 =  0
HASHTYPE_SHA1 =  1
HASHTYPE_SHA224 = 2
HASHTYPE_SHA256 = 3
HASHTYPE_SHA384 = 4
HASHTYPE_SHA512 = 5
HASHTYPE_SHA = 5



class Hasher:
	"""
	HASH class for wrapping hashlib
	"""
	hash_type = None
	hash_class = None
	_hash_class_copy = None
	_lock = threading.Lock()


	def __init__(self, hash_type=HASHTYPE_SHA256):
		"""
		Init Hasher class
		If no argument about hash_type, initial SHA256
		"""
		self.setHashType(hash_type)


	def __repr__(self):
		"""
		Just print hasher's hash_type
		"""
		return "('%s','hash_class : %s')" % (self.getHashType(),self.hash_class)


	def __str__(self):
		"""
		Just print hasher's hash_type
		"""
		return "('%s','hash_class : %s')" % (self.getHashType(),self.hash_class)


	def setHashType(self, hash_type):
		"""
		Setting hash type and hash function
		Possible resetting hash function
		You must use hasy_type in [HASHTYPE_MD5, HASHTYPE_SHA1, HASHTYPE_SHA224, HASHTYPE_SHA256, HASHTYPE_SHA384, HASHTYPE_SHA512]
		Or you will see the assertion error
		"""
		assert (hash_type in [HASHTYPE_MD5, HASHTYPE_SHA1, HASHTYPE_SHA224, HASHTYPE_SHA256, HASHTYPE_SHA384, HASHTYPE_SHA512])

		with self._lock:
			self.hash_type = hash_type
			if self.hash_class is not None:
				del self.hash_class
			if self._hash_class_copy is not None:
				del self._hash_class_copy
			
			if hash_type == HASHTYPE_MD5:
				self.hash_class = hashlib.md5()
			elif hash_type == HASHTYPE_SHA1:
				self.hash_class = hashlib.sha1()
			elif hash_type == HASHTYPE_SHA224:
				self.hash_class = hashlib.sha224()
			elif hash_type == HASHTYPE_SHA256:
				self.hash_class = hashlib.sha256()
			elif hash_type == HASHTYPE_SHA384:
				self.hash_class = hashlib.sha384()
			elif hash_type == HASHTYPE_SHA512:
				self.hash_class = hashlib.sha512()
			else:
				assert (hash_type in [HASHTYPE_MD5, HASHTYPE_SHA1, HASHTYPE_SHA224, HASHTYPE_SHA256, HASHTYPE_SHA384, HASHTYPE_SHA512])
				return

			self._hash_class_copy = self.hash_class.copy()

	
	def getHashType(self):
		"""
		Getting current hash type
		You must use hasy_type in [HASHTYPE_MD5, HASHTYPE_SHA1, HASHTYPE_SHA224, HASHTYPE_SHA256, HASHTYPE_SHA384, HASHTYPE_SHA512]
		Or you will see the assertion error
		"""
		assert (self.hash_type in [HASHTYPE_MD5, HASHTYPE_SHA1, HASHTYPE_SHA224, HASHTYPE_SHA256, HASHTYPE_SHA384, HASHTYPE_SHA512])

		with self._lock:
			currenthashlib_type = ""
			if self.hash_type == HASHTYPE_MD5:
				currenthashlib_type = "hash type : MD5"
			elif self.hash_type == HASHTYPE_SHA1:
				currenthashlib_type = "hash type : SHA1"
			elif self.hash_type == HASHTYPE_SHA224:
				currenthashlib_type = "hash type : SHA224"
			elif self.hash_type == HASHTYPE_SHA256:
				currenthashlib_type = "hash type : SHA256"
			elif self.hash_type == HASHTYPE_SHA384:
				currenthashlib_type = "hash type : SHA384"
			elif self.hash_type == HASHTYPE_SHA512:
				currenthashlib_type = "hash type : SHA512"
			else:
				assert (self.hash_type in [HASHTYPE_MD5, HASHTYPE_SHA1, HASHTYPE_SHA224, HASHTYPE_SHA256, HASHTYPE_SHA384, HASHTYPE_SHA512])
				return

		return currenthashlib_type 


	def digest(self, original_string):
		"""
		Get binary hash string 
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class.update(original_string)
			hash_string = self.hash_class.digest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string


	def hexdigest(self, original_string):
		"""
		Get hexadecimal hash string 
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class.update(original_string)
			hash_string = self.hash_class.hexdigest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string
	

	def md5(self, original_string):
		"""
		Get md5 hexadecimal hash string just once 
		But hasy type will keep a previous hash type
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class = hashlib.md5(original_string)
			hash_string = self.hash_class.hexdigest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string


	def sha1(self, original_string):
		"""
		Get sha1 hexadecimal hash string just once 
		But hasy type will keep a previous hash type
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class = hashlib.sha1(original_string)
			hash_string = self.hash_class.hexdigest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string


	def sha224(self, original_string):
		"""
		Get sha224 hexadecimal hash string just once 
		But hasy type will keep a previous hash type
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class = hashlib.sha224(original_string)
			hash_string = self.hash_class.hexdigest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string


	def sha256(self, original_string):
		"""
		Get sha256 hexadecimal hash string just once 
		But hasy type will keep a previous hash type
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class = hashlib.sha256(original_string)
			hash_string = self.hash_class.hexdigest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string


	def sha384(self, original_string):
		"""
		Get sha384 hexadecimal hash string just once 
		But hasy type will keep a previous hash type
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class = hashlib.sha384(original_string)
			hash_string = self.hash_class.hexdigest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string


	def sha512(self, original_string):
		"""
		Get sha512 hexadecimal hash string just once 
		But hasy type will keep a previous hash type
		You must use string or unicode, or you will see the assertion error
		"""
		assert type(original_string) in (str, unicode)

		with self._lock:
			self.hash_class = hashlib.sha512(original_string)
			hash_string = self.hash_class.hexdigest()
			del self.hash_class
			self.hash_class = self._hash_class_copy.copy()
		
		return hash_string


dochash_ignore = range(0,65) + range(91,97) + range(123,127)
dochash_trmap = ""
for cc in range(256):
	if cc in dochash_ignore:
		dochash_trmap += " "
	else:
		dochash_trmap += chr(cc)

class DocHash:
	"""
	Document hash class
	"""
	def hash(self, url, document, hash_type=HASHTYPE_SHA256):
		"""
		DocHash.hash(...) -> 64 bytes hexadecimal string

		Get Document hash with netloc + document (summary)
		"""
		hasher = Hasher(hash_type)
		netloc = urlparse.urlparse(url)[1]

		try:
			split_netloc = netloc.split(".")
			s_netloc = split_netloc[0]
			if s_netloc.startswith("www"):
				r_netloc = s_netloc[3:]
				len_netloc = len(r_netloc)

				if r_netloc.isdigit():
					# www + number
					netloc = ".".join(split_netloc[1:])
				elif r_netloc == "w"*len_netloc:
					# www + [w]*
					netloc = ".".join(split_netloc[1:])
		except:
			pass

		if document == None:
			document = ""

		try:
			if type(netloc) == unicode:
				netloc = netloc.encode("utf8", "ignore")
			if type(document) == unicode:
				document = document.encode("utf8", "ignore")
		except:
			pass

		hash_value = hasher.hexdigest(netloc + "".join(document.translate(dochash_trmap).split()))

		del hasher
		return hash_value 

	hash = classmethod(hash)



if __name__ == "__main__":
	hasher = Hasher()
	print hasher.getHashType()
	print hasher.digest("dddddd")
	print hasher.hexdigest("dddddd")
	hasher = Hasher(HASHTYPE_SHA512)
	print hasher
	print hasher.digest("dddddd")
	print hasher.hexdigest("dddddd")
	hasher.setHashType(HASHTYPE_MD5)
	a =  hasher.digest("dddddd"), "digest"
	b =  hasher.hexdigest("dddddd"), "hexadigest"

	import base64
	print a[0]
	print b[0]
	print base64.encodestring(a[0])

	print len(a[0]), len(b[0]),  len(base64.encodestring(a[0]))
	# use simple type function
	print hasher.md5("ddddd")
	print hasher.sha1("ddddd")
	print hasher.sha256("ddddd")
	print hasher.getHashType()

	print
	print "> DocHash Test..."
	print DocHash.hash("http://kcircle.tistory.com/12", "alsdkfjlaksdjflkasjdf")
	print DocHash.hash("http://kcircle.tistory.com/guest", "alsdkfjlaksdjflkasjdf")
	print DocHash.hash("http://tistory.com/asdlfj/asdfl", "alsdkfjlaksdjflkasjdf")
	print DocHash.hash("http://www.tistory.com/asdlfj/asdfl", "alsdkfjlaksdjflkasjdf")
	print DocHash.hash("http://www2.tistory.com/asdlfj/asdfl", "alsdkfjlaksdjflkasjdf")
	print DocHash.hash("http://wwwww.tistory.com/asdlfj/asdfl", "alsdkfjlaksdjflkasjdf")
	print DocHash.hash("http://www213.tistory.com/asdlfj/asdfl", "alsdkfjlaksdjflkasjdf")
	print DocHash.hash("http://www23a.tistory.com/asdlfj/asdfl", "alsdkfjlaksdjflkasjdf")

	str1 = """
조 회 : 887 등록일 : 2008-01-25 벌써 2008년 새해도 한달이 지나갑니다. 새해 초 세우셨던 계휙들은 지켜져 나가는지.. 다시 한번 더 다짐을 하여야 할 시기인것 같습니다. 2008년에는 뜻하는 모든 바를 소원 성취 하시기를 바랍니다. 이제 2월이면 우리 민족의 진짜 새해인 설날이 다가옵니다. 맛난거 마니 드시고 가족들과 함께 행복하게 보내세요. 다시 한번 인사 드립니다. ~~새해 복 마니 받으십시요~~ 항상 최선을 다하는 모습을 보여드리겠습니다. 태광철망(주) 임직원일동 배상
	""".strip()

	str2 = """
조 회 : 883 등록일 : 2007-01-25 벌써 2008년 새해도 한달이 지나갑니다. 새해 초 세우셨던 계휙들은 지켜져 나가는지.. 다시 한번 더 다짐을 하여야 할 시기인것 같습니다. 2008년에는 뜻하는 모든 바를 소원 성취 하시기를 바랍니다. 이제 2월이면 우리 민족의 진짜 새해인 설날이 다가옵니다. 맛난거 마니 드시고 가족들과 함께 행복하게 보내세요. 다시 한번 인사 드립니다. ~~새해 복 마니 받으십시요~~ 항상 최선을 다하는 모습을 보여드리겠습니다. 태광철망(주) 임직원일동 배상  
	""".strip()
	print
	url = "http://tkmesh.co.kr/notice/notice_view.asp?cate=C&code=AAaa3&idx=4"
	print url
	print DocHash.hash(url, str1)
	print DocHash.hash(url, str2)


	
#EOF
