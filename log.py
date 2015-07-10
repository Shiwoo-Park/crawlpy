#!/usr/bin/env python
#coding: utf8

import logging
import sys
import logging.handlers
from os import path,makedirs,listdir,remove

#define handler
FILE_HANDLER = 0
ROTATING_FILE_HANDLER = 1
TIMED_ROTATING_FILE_HANDLER = 2
STREAM_HANDLER = 3

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

logDict = dict()

class Log:
	"""
	Logger class based on logging module

	you can make logger without root logger 
	if you don't want to write log to many files, just create Log with name and filename
	and also Log has hierarchy. 
	If you do like this 

	p_logger = Log("babo",filename="babo.log")
	c_logger = Log("babo.son",filename="babo.son.log")
	c_logger.error("HAHAHA")
	
	"HAHAHA" will be written to babo.log and babo.son.log

	and if you want to write log separately, just do like this.
	 
	b_logger = Log("babo",filename="babo.log")
	m_logger = Log("mungchungi", filename="munchungi.log")
	b_logger.error("HEHEHEHEHE")
	m_logger.error("HUHUHUHUHU")

	if you already made root logger,  then "HEHEHEHEHE" and "HUHUHUHUHU" will be written to root logfile

	"""

	def __init__(self, name=None, **kwargs):
		"""
		type of args

		filename  Specifies that a FileHandler be created, using the specified filename, rather than a StreamHandler.  
		filemode  Specifies the mode to open the file, if filename is specified (if filemode is unspecified, it defaults to 'a').
		format    Use the specified format string for the handler.  See http://www.python.org/doc/current/lib/node422.html
		datefmt   Use the specified date/time format.
		level     Set the root logger level to the specified level.
		stream    Use the specified stream to initialize the StreamHandler. Note that this argument is incompatible with 'filename' - if both are present, 'stream' is ignored.

		**kwargs can be  filename = "./aaa.log", filemode = "a", format='%(asctime)s %(levelname)s %(message)s'  

		type of level
	
		CRITICAL = 50
		FATAL = CRITICAL
		ERROR = 40
		WARNING = 30
		WARN = WARNING
		INFO = 20
		DEBUG = 10
		NOTSET = 0

		default value of args

		filename : ./wstmp.log
		format : '%(asctime)s %(levelname)s %(message)s'
		level : DEBUG

		"""
		self.logger = logging.getLogger(name)
		if name == None:
			self.name = 'root'
		else:
			self.name = name

		logDict[self.name] = self
		if len(self.logger.handlers) == 0:
			level = kwargs.get("level",INFO)
			stream = kwargs.get("stream",None)
			filename = kwargs.get("filename",None)
			if filename:
				self._checkDir(filename)
				mode = kwargs.get("filemode",'a')
				hdlr = logging.FileHandler(filename,mode)
			else:
				stream = kwargs.get("stream")
				hdlr = logging.StreamHandler(stream)


			format = kwargs.get("format",'%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s')
			dfs = kwargs.get("datefmt", "%y-%m-%d %H:%M:%S")
			fmt = logging.Formatter(format,dfs)
			hdlr.setFormatter(fmt)
			self.logger.addHandler(hdlr)
			self.logger.setLevel(level)

			self.format = format
			self.dfs = dfs
			self.level = level


	def __str__(self):
		"""
		return logger name and handlers and its child
		"""
		ret_str = "logger name : %s\n"%self.name
		n_logger = self.logger
		for name in logging.Logger.manager.loggerDict:
			if name.find(self.name) >= 0 and name != self.name:
				ret_str += "	child : " + name +"\n"
		for h in n_logger.handlers[:]:
			ret_str += " handler : " + str(h) +"\n"
		return ret_str


	def __repr__(self):
		"""
		return logger name and handlers
		"""
		return self.__str__()


	def _checkDir(self, filename):
		"""
		check directoy. unless dir exists, make dir 
		"""
		if len(path.dirname(filename)) > 0 and not path.exists(path.dirname(filename)):
			makedirs(path.dirname(filename))


	def debug(self, msg, *args, **kwargs):
		"""
		write debug level log
		"""
		self.logger.debug(msg, *args, **kwargs)


	def error(self, msg, *args, **kwargs):
		"""
		write error level log
		"""
		self.logger.error(msg,*args,**kwargs)

	
	def warning(self, msg, *args, **kwargs):
		"""
		write warning level log
		"""
		self.logger.warning(msg,*args,**kwargs)


	def critical(self, msg, *args, **kwargs):
		"""
		write critical level log
		"""
		self.logger.critical(msg, *args, **kwargs)


	def info(self, msg, *args, **kwargs):
		"""
		write info level log
		"""
		self.logger.info(msg, *args, **kwargs)

	
	def removeHandler(self):
		"""
		remove all handler
		"""
		n_logger = self.logger
		for h in n_logger.handlers[:]:
			n_logger.removeHandler(h)


	def addHandler(self, type, filename=None, **kwargs):
		"""
		add handler 

		* type of handler 

		FILE_HANDLER = 0
		ROTATING_FILE_HANDLER = 1
		TIMED_ROTATING_FILE_HANDLER = 2
		STREAM_HANDLER = 3

		It can be added.

		* type of kwargs
			FILE_HANDLER : mode
			ROTATING_FILE_HANDLER : mode, maxBytes, backupCount
			TIMED_ROTATING_FILE_HANDLER : when,interval, backupCount
			* type of when 
				'S' : second
				'M' : minute
				'H' : hour
				'D' : day
				'W' : week
				'midnight' : 00:00
				if u set when = 'S',interval = 1, then  logger will rotate file every second
				if u set when = 'midnight', interval = 1, then logger will rotate file at midnight every day

		For more information, See http://www.python.org/doc/current/lib/node410.html

		return 0 when succeeded, else return -1

		"""
		try:	
			if filename != None:
				self._checkDir(filename)
			else:
				filename = './wstmp.log'
			if type == FILE_HANDLER:
					mode = kwargs.get("mode", "a")
					fh = logging.handlers.FileHandler(filename,mode)
			elif type == ROTATING_FILE_HANDLER:
					mode = kwargs.get("mode", "a")
					maxBytes = kwargs.get("maxBytes", 512)
					backupCount = kwargs.get("backupCount", 5)
					fh = logging.handlers.RotatingFileHandler(filename,mode,maxBytes,backupCount)
			elif type == TIMED_ROTATING_FILE_HANDLER:
					
					when = kwargs.get("when", "midnight")
					interval = kwargs.get("interval", 1)
					backupCount = kwargs.get("backupCount", 0)

					fh = logging.handlers.TimedRotatingFileHandler(filename, when, interval, backupCount)
			elif type == STREAM_HANDLER:
				fh = logging.StreamHandler()
			else:
				sys.stderr.write("we don't have that kind of Handler\n")
				return -1
			level = kwargs.get("level", self.level)
			format = kwargs.get("format", self.format)
			dfs = kwargs.get("datefmt",self.dfs)
			fh.setLevel(level)
			fh.setFormatter(logging.Formatter(format,dfs))
			self.logger.addHandler(fh)
			return 0
		except Exception,msg:
			sys.stderr.write("%s\n"% msg)
			return -1


	def resetHandler(self, type, filename=None, **kwargs):
		"""
		remove all other handler and add new handler
		"""
		try:
			self.removeHandler()

			self.addHandler(type, filename, **kwargs)
		except Exception,msg:
			sys.stderr.write("%s\n"%msg)



def getLogger(name=None, **kwargs):
	"""
	return logger by name
	"""
	if name == None:
		if len(logging.getLogger().handlers) == 0:
			t_logger = Log(**kwargs)
			logDict['root'] = t_logger
			return t_logger.logger
		else:
			try:
				return logDict['root'].logger
			except:
				return logging.getLogger()
	else:
		if name in logDict:
			return logDict[name].logger
		else:
			t_logger = Log(name,**kwargs)
			logDict[name] = t_logger
			return t_logger.logger
	

def logTest():
	p_logger = getLogger("babo.ppp")
	p_logger.error("TEST")
	p_logger.debug("FFFF")


if __name__ == "__main__":
	
	try:
		
		root_logger = Log()
		root_logger.resetHandler(TIMED_ROTATING_FILE_HANDLER, "./time_rotating.log", when = 'S', backupCount=10)
		root_logger.addHandler(STREAM_HANDLER)
		root_logger.addHandler(ROTATING_FILE_HANDLER, "./rotating_file.log", mode='w', maxBytes=1024, backupCount=2, level=ERROR)

		babo_logger = Log("babo", filename="babo.log")
		babo_logger.addHandler(ROTATING_FILE_HANDLER, "./test.log", mode='a', maxBytes=512, backupCount=2)

		babo_kkk_logger = Log("babo.kkk", filename='./babo.kkk.log')
		babo_ppp_logger = Log("babo.ppp", filename='./babo.ppp.log')

		mungchungi_logger = Log("mungchungi", filename='./mungchungi.log')

		for i in range(0,100):
			root_logger.debug("AAAasdf asdfasdf asdfasdf")
			babo_kkk_logger.debug("PPP")
			babo_ppp_logger.debug("KKK")
			mungchungi_logger.debug("LLL")

		print babo_kkk_logger
		print babo_logger

		logTest()

	except Exception,msg:
		sys.stderr.write("%s\n"%msg)
