#coding: utf8

from urllib import quote
from parser import HtmlParser, RESERVED, LinkURL, makePerfectURL
import xml.dom.minidom
from log  import getLogger


def getText(nodelist):
	rc = ""
	for node in nodelist:
		try:
			rc += node.data.encode("utf8")
		except Exception, msg:
			getLogger().error(msg)
	return rc


class XmlParser:
	
	def __init__(self, base_url=None):
		self.links = dict()
		self.dom = None
		self.title = ""
		self.base_url = base_url

	def addLink(self, url, anchor_text, tag, description=""):
		if not url.startswith("http"):
			url = makePerfectURL(url, self.base_url)
		if url not in self.links :
			self.links[url] = list()
		link = LinkURL(url, tag, "IN", anchor_text, "")
		link.description = description
		self.links[url].append(link)

	def parseBlogspot(self, contents):
		
		result_dict = dict()


		for field in ["title","link","image", "generator","language", "description", "writer"]:
			result_dict[field] = ""

		try:
			self.dom = xml.dom.minidom.parseString(contents)


			t_node = self.dom.getElementsByTagName('title')
			if len(t_node) > 0:
				self.title = getText(self.dom.getElementsByTagName('title')[0].childNodes)
			else:
				self.title = ""
			result_dict["title"] = self.title

			if len(self.dom.getElementsByTagName("link") ) > 0:
				result_dict["link"] = getText(self.dom.getElementsByTagName("link")[0].childNodes).strip()
				
			if len(self.dom.getElementsByTagName("image")) > 0:
				result_dict["image"] = getText(self.dom.getElementsByTagName("image")[0].getElementsByTagName("url")[0].childNodes)

			if len(self.dom.getElementsByTagName("generator")) > 0:
				result_dict["generator"] = getText(self.dom.getElementsByTagName("generator")[0].childNodes)

			if len(self.dom.getElementsByTagName("author")) >0:
				try:
					result_dict["writer"] = getText(self.dom.getElementsByTagName("author")[0].getElementsByTagName("name")[0].childNodes)
				except Exception, msg:
					pass

			nodelist = self.dom.getElementsByTagName("entry")
			if len(nodelist ) > 0:
				for node in nodelist:

					links = node.getElementsByTagName("link")
					for l_node in links:
						if l_node.attributes["rel"].value == "alternate":
							url = l_node.attributes["href"].value.encode("utf8")
							try:
								t_title = l_node.attributes["title"].value.encode("utf8")
							except Exception, msg:
								continue

							self.addLink(url,t_title, "A" , "")
							try:
								pubdate = node.getElementsByTagName("published")
								if len(pubdate) > 0 :
									write_time = getText(pubdate[0].childNodes)
									if write_time.find(".") > 0:
										write_time = write_time[:write_time.rfind(".")].replace("T", " ")

									self.links[url][0].pubdate = write_time

							except Exception, msg:
								getLogger().error(msg)
							
							try:
								content = node.getElementsByTagName("content")
								self.links[url][0].content = getText(content[0].childNodes)
							except Exception, msg:
								getLogger().error(msg)

			else:
				nodelist = self.dom.getElementsByTagName("item")
				for node in nodelist:

					url = getText(node.getElementsByTagName("link")[0].childNodes)
					title = getText(node.getElementsByTagName("title")[0].childNodes)
					self.addLink(url,title, "A" , "")
					try:
						pubdate = node.getElementsByTagName("pubDate")
						if len(pubdate) > 0 :
							write_time = getText(pubdate[0].childNodes)
							if write_time.find(".") > 0:
								write_time = write_time[:write_time.rfind(".")].replace("T", " ")

							self.links[url][0].pubdate = write_time

					except Exception, msg:
						getLogger().error(msg)
							
					try:
						content = node.getElementsByTagName("description")
						if len(content) > 0:
							self.links[url][0].content = getText(content[0].childNodes)
						else:
							content = node.getElementsByTagName("atom:summary")

							if len(content) > 0:
								self.links[url][0].content = getText(content[0].childNodes)
					except Exception, msg:
						getLogger().error(msg)


					try:
						category = node.getElementsByTagName("category")
						if len(category) > 0:
							self.links[url][0].categories = getText(category[0].childNodes)
					except Exception, msg:
						getLogger().error(msg)
							
		except Exception, msg:
			getLogger().error(msg)	
		return result_dict

	def parseWordPress(self, contents):

		result_dict = dict()

		for field in ["title","link","image", "generator","language", "description", "writer"]:
			result_dict[field] = ""

		try:
			self.dom = xml.dom.minidom.parseString(contents)

			self.title = getText(self.dom.getElementsByTagName('title')[0].childNodes)
			result_dict["title"] = self.title

			if len(self.dom.getElementsByTagName("author")) >0:
				result_dict["writer"] = getText(self.dom.getElementsByTagName("author")[0].getElementsByTagName("name")[0].childNodes)

			if len(self.dom.getElementsByTagName("link") ) > 0:
				result_dict["link"] = getText(self.dom.getElementsByTagName("link")[0].childNodes).strip()
				
			if len(self.dom.getElementsByTagName("image")) > 0:
				result_dict["image"] = getText(self.dom.getElementsByTagName("image")[0].getElementsByTagName("url")[0].childNodes)

			if len(self.dom.getElementsByTagName("generator")) > 0:
				result_dict["generator"] = getText(self.dom.getElementsByTagName("generator")[0].childNodes)

			nodelist = self.dom.getElementsByTagName("item")
			if len(nodelist ) > 0:
				for node in nodelist:
					try:
						if node.attributes["rel"].value == "alternate":
							url = node.attributes["href"].value
							try:
								t_title = node.attributes["title"].value
							except Exception, msg:
								print msg
							self.addLink(url,t_title, "A" , "")
					except Exception, msg:
						pass
		except Exception, msg:
			print msg

		for node in nodelist:
			try:
				title = getText(node.getElementsByTagName("title")[0].childNodes)
			except Exception, msg:
				title = ""
			try:
				link_url = getText(node.getElementsByTagName("link")[0].childNodes)
			except Exception, msg:
				link_url = ""

			if title == "" and link_url == "":
				continue

			if len(node.getElementsByTagName("guid")) > 0:

				tt_url = getText(node.getElementsByTagName("guid")[0].childNodes)
				if tt_url.startswith("http"):
					link_url = tt_url

			if link_url == "":
				try:
					for t_node in node.getElementsByTagName("link"):
						if t_node.attributes["rel"].value == "alternate":
							link_url = t_node.attributes["href"].value
							break
				except Exception, msg:
					getLogger().error(msg)

			descs = node.getElementsByTagName("description")
			description = ""
			if len(descs) > 0 :
				description = getText(descs[0].childNodes)


			try:
				pubdate = node.getElementsByTagName("pubDate")
			except Exception, msg:
				getLogger().error(msg)
			
			write_time = ""
			if len(pubdate) > 0 :
				write_time = getText(pubdate[0].childNodes)
			else:
				pubdate = node.getElementsByTagName("dc:date")
				if len(pubdate) > 0 :
					write_time = getText(pubdate[0].childNodes)
				else:
					pubdate = node.getElementsByTagName("published")
					if len(pubdate) > 0 :
						write_time = getText(pubdate[0].childNodes)

			body_node = node.getElementsByTagName("content:encoded")
			l_contents = ""
			if len(body_node) > 0 :
				l_contents = getText(body_node[0].childNodes)
			else:
				body_node = node.getElementsByTagName("content")
				if len(body_node) > 0 :
					l_contents = getText(body_node[0].childNodes)

			category_nodes = node.getElementsByTagName("category")

			cates = set()
			for cate_node in category_nodes:
				cate = getText(cate_node.childNodes)
				cates.add(cate)

			categories = ",".join(cates)

			writer_nodes = node.getElementsByTagName("dc:creator")
			writer = ""
			if len(writer_nodes) > 0:
				writer = getText(writer_nodes[0].childNodes)
			else:
				writer_nodes = node.getElementsByTagName("author")
				if len(writer_nodes) > 0:
					writer = getText(writer_nodes[0].childNodes)
					if writer == "":
						writer = getText(self.dom.getElementsByTagName("author")[0].getElementsByTagName("name")[0].childNodes)

						
			thumbnail = ""
			tags = ""
			try:
				thumb_node = node.getElementsByTagName("media:thumbnail")
				if len(thumb_node) > 0:
					thumbnail = thumb_node[0].attributes["url"].value
				else:
					image_nodes = node.getElementsByTagName("enclosure")
					for t_node in image_nodes:
						try:
							if t_node.attributes["type"].value == "image/jpeg":
								thumbnail = t_node.attributes["url"].value
								break
						except Exception, msg:
							pass
				if thumbnail == "":
					thumb_node = node.getElementsByTagName("media:content")
					if len(thumb_node) > 0:
						thumbnail = thumb_node[0].attributes["url"].value
				tags_node = node.getElementsByTagName("tag")
				if len(tags_node) > 0:
					tags = getText(tags_node[0].childNodes)

			except Exception, msg:
				getLogger().error(msg)

			self.addLink(link_url,title, "A" , description)
			self.links[link_url][0].pubdate = write_time

			self.links[link_url][0].content = l_contents
			self.links[link_url][0].categories = categories
			self.links[link_url][0].tags = tags
			if len(l_contents) == 0:
				self.links[link_url][0].content = description


			try:
				if self.links[link_url][0].content:
					body, res = self.parseHtml(link_url, "<html><body>"+self.links[link_url][0].content+"</body></html>")
					self.links[link_url][0].content = body
					self.links[link_url][0].res_dict = res
			except Exception, msg:
				getLogger().error(msg)

			if len(writer) > 0:
				if result_dict["writer"] == "":
					result_dict["writer"] = writer
				self.links[link_url][0].writer = writer

			if len(thumbnail) > 0:
				self.links[link_url][0].thumb = thumbnail
			else:
				self.links[link_url][0].thumb = ""

		return result_dict

	def parseHtml(self, base_url, html):
		try:
			parser = HtmlParser()                                                  
			parsing_result = parser.parse(html, False)                             
			#[title_text, full_text, core_text, rest_text, all_links, etc_datas] = parsing_result
			res_dict = parsing_result

			tree = parser.tree
			title = ""
			body = ""
			write_time = 0
			imgs = None
			res = dict()

			s_id = tree.root.id
			view_node = tree.root
			e_id = view_node.findENode()
			(extractedContent, rest_text, links_in_summary, imgs, core_len, text_list) = tree.root.getTextImageWithPosition(s_id, e_id)
			body_pieces = extractedContent.split()
			body_text = " ".join(body_pieces)
			body = body_text.replace("|11818|", "&")

			#res["all_links"] = res_dict["all_links"]
			res["links"] = links_in_summary
			res["image_count"] = len(imgs)

			res["images"] = list()
			for i_link in imgs:
				r_image = parser.makePerfectURL(i_link)
				res["images"].append(r_image)
			res["embed_links"] = parser.embed_links
			res["meta_data"] = parser.meta_dict
			res["body_extension"] = rest_text.strip()
			return body, res
		except Exception, msg:
			return body, res

		


	def parse(self, contents, temp):
		# resultReturn
		result_dict = dict()

		for field in ["title","link","image", "generator","language", "description", "writer"]:
			result_dict[field] = ""

		try:
			self.dom = xml.dom.minidom.parseString(contents)
			self.title = getText(self.dom.getElementsByTagName("title")[0].childNodes)

			result_dict["title"] = self.title

			if len(self.dom.getElementsByTagName("link") ) > 0:
				result_dict["link"] = getText(self.dom.getElementsByTagName("link")[0].childNodes).strip()
				
			if len(self.dom.getElementsByTagName("image")) > 0:
				result_dict["image"] = getText(self.dom.getElementsByTagName("image")[0].getElementsByTagName("url")[0].childNodes)

			if len(self.dom.getElementsByTagName("generator")) > 0:
				result_dict["generator"] = getText(self.dom.getElementsByTagName("generator")[0].childNodes)


			if result_dict["generator"].find("wordpress") >= 0:
				return self.parseWordPress(contents)
			if result_dict["generator"].lower().find("blogger") >= 0:
				return self.parseBlogspot(contents)


			if len(self.dom.getElementsByTagName("language")) > 0:
				result_dict["language"] = getText(self.dom.getElementsByTagName("language")[0].childNodes)
			if len(self.dom.getElementsByTagName("description")) > 0:
				result_dict["description"] = getText(self.dom.getElementsByTagName("description")[0].childNodes)
			try:
				
				if len(self.dom.getElementsByTagName("managingEditor")) >0:
					result_dict["writer"] = getText(self.dom.getElementsByTagName("managingEditor")[0].childNodes)
				elif len(self.dom.getElementsByTagName("webMaster")) >0:
					result_dict["writer"] = getText(self.dom.getElementsByTagName("webMaster")[0].childNodes)
				else:
					tt_list = self.dom.getElementsByTagName("author")

					try:
						if len(tt_list) > 0:
							writer = getText(tt_list[0].getElementsByTagName("name")[0].childNodes)
							if writer != "":
								result_dict["writer"] = writer
								tt_node = self.dom.getElementsByTagName("author")[0].getElementsByTagName("gd:image")[0]
								image = tt_node.attributes["src"].value.encode("utf8")
								if image != "":
									result_dict["image"] = image
					except Exception, msg:	
						pass
			except Exception, msg:
				getLogger().error(msg)

		except Exception, msg:
			getLogger().error(msg)

		try:
			nodelist = self.dom.getElementsByTagName("item")
		except Exception, msg:
			return result_dict
		if len(nodelist) == 0:
			nodelist = self.dom.getElementsByTagName("entry")
		if len(nodelist) == 0:
			nodelist = self.dom.getElementsByTagName("link")

		for node in nodelist:
			try:
				title = getText(node.getElementsByTagName("title")[0].childNodes)
			except Exception, msg:
				title = ""
			try:
				link_url = getText(node.getElementsByTagName("link")[0].childNodes)
			except Exception, msg:
				try:
					link_url = node.attributes["xml:base"].value.encode("utf8")
				except Exception, msg:
					link_url = ""
			if link_url == "":
				continue

			if len(node.getElementsByTagName("guid")) > 0:
				tt_url = getText(node.getElementsByTagName("guid")[0].childNodes)
				if tt_url.startswith("http"):
					link_url = tt_url

			if link_url == "":
				try:
					for t_node in node.getElementsByTagName("link"):
						if t_node.attributes["rel"].value == "alternate":
							link_url = t_node.attributes["href"].value.encode("utf8")
							break
				except Exception, msg:
					getLogger().error(msg)

			descs = node.getElementsByTagName("description")
			description = ""
			if len(descs) > 0 :
				description = getText(descs[0].childNodes)

			try:
				pubdate = node.getElementsByTagName("pubDate")
			except Exception, msg:
				getLogger().error(msg)
			
			write_time = ""
			if len(pubdate) > 0 :
				write_time = getText(pubdate[0].childNodes)
			else:
				pubdate = node.getElementsByTagName("dc:date")
				if len(pubdate) > 0 :
					write_time = getText(pubdate[0].childNodes)
				else:
					pubdate = node.getElementsByTagName("published")
					if len(pubdate) > 0 :
						write_time = getText(pubdate[0].childNodes)
					else:
						pubdate = node.getElementsByTagName("a10:updated")
						if len(pubdate) > 0 :
							write_time = getText(pubdate[0].childNodes)
							write_time = write_time[:write_time.rfind("+")].replace("T", " ")

			body_node = node.getElementsByTagName("content:encoded")
			l_contents = ""
			if len(body_node) > 0 :
				l_contents = getText(body_node[0].childNodes)
			else:
				body_node = node.getElementsByTagName("content")
				if len(body_node) > 0 :
					l_contents = getText(body_node[0].childNodes)

			category_nodes = node.getElementsByTagName("category")

			cates = set()
			for cate_node in category_nodes:
				cate = getText(cate_node.childNodes)
				cates.add(cate)

			categories = ",".join(cates)

			writer_nodes = node.getElementsByTagName("dc:creator")
			writer = ""
			if len(writer_nodes) > 0:
				writer = getText(writer_nodes[0].childNodes)
			else:
				writer_nodes = node.getElementsByTagName("author")
				if len(writer_nodes) > 0:
					writer = getText(writer_nodes[0].childNodes)
					if writer == "":
						try:
							writer = getText(self.dom.getElementsByTagName("author")[0].getElementsByTagName("name")[0].childNodes)
						except Exception, msg:
							pass
						
			thumbnail = ""
			tags = ""
			try:
				thumb_node = node.getElementsByTagName("media:thumbnail")
				if len(thumb_node) > 0:
					thumbnail = thumb_node[0].attributes["url"].value.encode("utf8")
				else:
					image_nodes = node.getElementsByTagName("enclosure")
					for t_node in image_nodes:
						try:
							if t_node.attributes["type"].value == "image/jpeg":
								thumbnail = t_node.attributes["url"].value.encode("utf8")
								break
						except Exception, msg:
							pass
				if thumbnail == "":
					thumb_node = node.getElementsByTagName("media:content")
					if len(thumb_node) > 0:
						thumbnail = thumb_node[0].attributes["url"].value.encode("utf8")
				tags_node = node.getElementsByTagName("tag")
				if len(tags_node) > 0:
					tags = getText(tags_node[0].childNodes)

			except Exception, msg:
				getLogger().error(msg)

			self.addLink(link_url,title, "A" , description)
			self.links[link_url][0].pubdate = write_time
			self.links[link_url][0].content = l_contents
			self.links[link_url][0].categories = categories
			self.links[link_url][0].tags = tags
			if len(l_contents) == 0:
				self.links[link_url][0].content = description

			if len(writer) > 0:
				if result_dict["writer"] == "":
					result_dict["writer"] = writer
				self.links[link_url][0].writer = writer

			if len(thumbnail) > 0:
				self.links[link_url][0].thumb = thumbnail
			else:
				self.links[link_url][0].thumb = ""

		full_links = []
		L = self.links.items()
		try:
			L.sort(key=lambda item:item[1].id)
		except Exception, msg:
			pass
		full_links += [urldata for url, urldata in L]

		return result_dict


class rssParser:

	def __init__(self):
		self.parser = None
		self.title = ""

	def parse(self, url, html):
		self.parser = XmlParser(base_url=url)
		full_html = html.replace("", "").replace("","").replace("","").replace("", "").replace("", "").replace("","")  # ctrl +v  누르고 입력
		full_html = full_html.replace("", "").replace("", "").replace("", "").replace("", "").replace("","")  # ctrl +v  누르고 입력
		if full_html.find("""<?xml version="1.0" encoding="euc-kr" ?>""") >= 0:
			full_html = full_html.replace("""<?xml version="1.0" encoding="euc-kr" ?>""", "")
			full_html = full_html.decode("cp949","replace").encode("utf8")
		elif url.find("blog.moneta.co.kr") > 0 or url.find("blog.joins.com") > 0:
			full_html = html.decode("cp949","replace").encode("utf8")
			full_html = full_html.replace("<copyright>Copyright ⓒ ㈜팍스넷 / SK텔레콤㈜, All Rights Reserved</copyright>", "").replace('<?xml version="1.0" encoding="euc-kr"?>', "")
			full_html = full_html.replace("""<?xml version="1.0" encoding="euc-kr" ?>""", "")

		if url.find("blogspot.kr") >= 0 or url.find("blogspot.com") >= 0:
			res_dict = self.parser.parseBlogspot(full_html)
			res_dict["links"] = self.parser.links
		else:
			res_dict = self.parser.parse(full_html, False)
			res_dict["links"] = self.parser.links
			self.title = self.parser.title
			for tt_url in self.parser.links:
				link = self.parser.links[tt_url]
				#print link.url, link.text, link.inout, link.description


		return res_dict



if __name__ == "__main__":
	import urllib2
	import sys

	if len(sys.argv) >1:
		url = sys.argv[1]
	else:
		url = "https://feeds.feedburner.com/imaso"

	opener = urllib2.build_opener()
	req = urllib2.Request(url)
	#req.add_header("User-agent", "Mozilla/5.0 (compatible; Windows NT 6.1?; ZumBot/1.0; http://help.zum.com/inquiry)")
	req.add_header("User-agent", "wget")
	rs = opener.open(req)

	http_header = str(rs.info())
	http_content = rs.read()
	real_URL = rs.url


	parser = rssParser()
	result = parser.parse(real_URL, http_content)
	title = result["title"]
	image = result["image"]
	links = result["links"]

	print "title : ", title
	print "image : ", image
	print "author : ", result["writer"]
	print "generator : ", result["generator"]
	print "lang : ", result["language"]
	print "link : ", result["link"]

	for link in links:
		l_data = links[link][0]
		print link , l_data.text, "write_time : ",  l_data.pubdate, ", tags :", l_data.tags, "category : ", l_data.categories, "writer :" , l_data.writer 
