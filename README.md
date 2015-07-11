# Crawl Utility

These are individual modules for crawling the web.
You can easily manipulate diverse type of data by using these modules.

Give it a try!!!

## Module intro

#### date_parser.py

Normalize diverse type of date strings and be able to produce into type what you want.
It supports 한국어 날짜포맷, English date formats and ago pattern formats(~~ 전)
Here's how to use.

```python
from date_parser import DateParser

parser = DateParser()

some_random_date_string = "Tue Dec 30 2014 17:10:24 +0000"

timestamp = parser.getUnixTimestamp(some_random_date_string)
default_format_date_string = parser.getDate(some_random_date_string)
```

#### data_parser.py

Extracts specific type of data from specific length of string, this module currently provides
* extracting Korean name
* extracting Email address

#### xml_producer.py

XML data maker (file, string)

#### xml_parer.py 

XML data parser (include FEED, RSS parser)

#### url_parser.py - in operation

URL parser it offer's easy-regex like URL parsing function.

#### log.py

Provides easy-logging include, file logger by implementing function below in your python program
and call *setLogger()* at the initial point of the program.

```python

import os
import time
from log import Log, getLogger

LOG_PATH = "/my_program/logs

def setLogger():
	log_format = "%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
	date_format = "%y-%m-%d %H:%M:%S"
	mark_time = time.strftime("%Y%m%d")
	path_dir = LOG_PATH+"/%s"%mark_time
	if not os.path.exists(path_dir):
		os.makedirs(path_dir)
	log_file = path_dir+"/my_log_%s.log"%(os.getpid())
	root_logger = Log(filename=log_file, format=log_format, datefmt=date_format)
	
def logTest():
	getLogger().info("My first log")
```