#!/bin/env python
# coding: utf8
"""
A multi-producer, multi-consumer unique queue.
"""

from Queue import Queue as _Queue, Empty as QueueEmpty, Full as QueueFull
from random import shuffle as _shuffle
from threading import Lock as _ThreadLock


class Queue(_Queue):
	"""
	Create a unique queue object with a given size and an empty set
	if maxsize <= 0, the queue size is infinite
	"""

	def __init__(self, uniqness=True, maxsize=0):
		_Queue.__init__(self, maxsize)
		self.uniqness = uniqness
		self.maxsize = maxsize
		self._qset_lock = None
		if self.uniqness:
			self._qset_lock = _ThreadLock()
			self._qset = set()
		self.enq = self.put_nowait
		self.deq = self.get_nowait
		

	def __str__(self):
		"""
		x.__str__() -> str(x)
		"""
		if self.maxsize == 0:
			size_str = "%s/Inf" % self.qsize()
		else:
			size_str = "%s/%s" % (self.qsize(), self.maxsize)

		deq_str = "[ "
		for i in range(self.qsize()):
			if i >= 3:
				break

			if i > 0:
				deq_str += ","
				
			try:
				deq_str += " %s " % self.queue[i]
			except:
				deq_str += " "

		if self.qsize() > 3:
			deq_str += "... ]"
		else:
			deq_str += "]"
			
		return "%s %s " % (size_str, deq_str)


	def __repr__(self):
		""" 
		return information string about type of queue, maxsize and elements of the queue 
		"""
		if self.uniqness:
			ret_str = "unique queue whose maxsize is "
		else:
			ret_str = "original queue whose maxsize is "
		if self.maxsize == 0:
			ret_str += "infinite\n"
		else:
			ret_str += str(self.maxsize) +"\n"

		ret_str += str(self.queue)
		return ret_str
		
	
	def __len__(self):
		return len(self._qset)


	def __contains__(self, element):
		"""
		Report whether an element is a member of a queue.
		(Called in response to the expression `element in self'.)
		"""
		try:
			return element in self._qset
		except TypeError:
			transform = getattr(element, "__as_temporarily_immutable__", None)
			if transform is None:
				# re-raise the TypeError exception we caught
				raise 
			return transform() in self._qset


	def shuffle(self):
		self.mutex.acquire()
		_shuffle(self.queue)
		self.mutex.release()

	def _put(self, item, block=True, timeout=None):
		if self.uniqness:
			self._qset_lock.acquire()
			if not item in self._qset:
				self.queue.append(item)
				self._qset.add(item)
			self._qset_lock.release()
		else:
			self.queue.append(item)


	def _get(self, block=True, timeout=None):
		item = self.queue.popleft()
		if self.uniqness:
			self._qset_lock.acquire()
			self._qset.discard(item)
			self._qset_lock.release()
		return item



if __name__ == "__main__":
	uq = Queue()
	q = Queue(False)
	lq = Queue(True,100)

	import time
	for i in range(0,1000):
		uq.put("http://daum.net/index"+str(i)+".html")
		q.put("http://daum.net/index"+str(i)+".html")
		if not lq.full():
			lq.put("http://daum.net/index"+str(i)+".html")

	for i in range(0,100,2):
		uq.put("http://daum.net/index"+str(i)+".html")
		q.put("http://daum.net/index"+str(i)+".html")
		if not lq.full():
			lq.put("http://daum.net/index"+str(i)+".html")
	
	print "the size of queue :" , q.qsize()
	print "the size of queue which has max size(100) : " , lq.qsize()
	print "the size of unique queue : ", uq.qsize()

	while not uq.empty():
		item = uq.get()
		print item
		if item == None:
			break;

	while not lq.empty():
		item = lq.deq()
		print item
	print q
	print lq

