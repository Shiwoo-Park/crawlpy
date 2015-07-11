from urlparse import urlparse

TLDs = ["com","net","org","edu","int","biz","info","name","pro","museum","gov","mil","art","aero","coop","co","mobi","asia","travel","jobs"]
ccTLDs = ["bn","mm","li","pt","gb","jo","es","py","ki","ne","ar","tg","bf","mu","la","lv","ro","fm","cc","tw","im","me","rw","pl","tn","kz","sy","gs","mz","ir","vn","ie","ga","ml","pr","au","bv","kh","tc","lr","bo","td","cr","ci","er","gi","mt","jp","nf","do","tt","vg","si","il","md","az","to","ru","pe","gr","cz","??.ac","ky","id","no","cy","at","gy","bh","mo","am","nr","eu","ch","ua","kw","bw","lt","ng","pk","np","io","ee","kp","kg","bg","tl","fo","ca","it","gq","hm","mg","ae","ht","aw","tz","cx","sb","co","nu","bi","gg","mn","al","de","et","sn","ph","wf","re","pm","fi","cg","mw","uy","gh","sa","tr","lu","vi","sg","in","mf","ad","tm","hu","ug","kn","us","gp","nz","cn","ao","gf","rs","na","cw","pa","sm","bq","bj","mq","sj","fj","om","cf","vc","ke","ba","mv","hk","ma","dm","eg","hr","ag","tj","ni","km","by","gw","cm","uz","um","bz","st","aq","cv","su","dz","ge","mp","an","br","sl","gn","dj","se","bb","my","fr","tk","iq","tp","mh","af","ss","gu","eh","bl","cu","pg","qa","va","cl","ms","lc","ai","gd","nc","ve","sk","bs","bd","mc","dk","pf","je","ws","fk","vu","gm","mx","so","uk","sh","sd","mk","lk","th","jm","ps","sr","gt","bm","ls","ck","sx","pn","bt","ly","as","tf","ec","kr","be","mr","ax","tv","cd","sz","hn","gl","lb","sv","sc","pw","nl","is"]
SLDs = ["co","go","ac","nm","ne","or","re","kg","es","ms","hs","sc","pe"]


class URLData:
	def __init__(self, url=""):
		self.original_url = url
		self.domain = ""
		self.top_domain = ""
		self.path = ""
		self.query_dic = dict()

	def __str__(self):
		d = {"original_url":self.original_url, "domain":self.domain, "top_domain":self.top_domain,
			"path":self.path, "query_dic":self.query_dic}
		return str(d)

class URLParser:

	def parse(self, url):
		"""
		:param url: url to parse
		:return: URLData object
		"""
		url_obj = urlparse(url)
		url_data = URLData(url)

		url_data.domain = url_obj.netloc
		url_data.top_domain = url_obj.netloc
		top_domain = self.getTopDomain(url_obj.netloc)
		if top_domain:
			url_data.top_domain = top_domain

		url_data.path = url_obj.path
		url_data.query_dic = self.getQueryDic(url_obj.query)
		return url_data

	def getTopDomain(self, domain):

		pieces = domain.split(".")
		if len(pieces) < 2:
			return None
		elif len(pieces) == 2:
			if pieces[1] in TLDs:
				return domain
			elif pieces[1] == "kr":
				if pieces[0] in SLDs:
					return None
				else:
					return domain
		else:
			if len(pieces) == 4:
				try:
					k = int(pieces[-1])
					return None
				except Exception, msg:
					pass

			if pieces[-1] in TLDs:
				return ".".join(pieces[-2:])
			elif pieces[-1] in ccTLDs:
				if pieces[-2] in SLDs:
					return ".".join(pieces[-3:])
				else:
					return ".".join(pieces[-2:])
			else:
				return ".".join(pieces[-3:])

	def getQueryDic(self, query):
		ret = dict()
		kv_list = query.split("&")
		for kv in kv_list:
			kv_arr = kv.split("=")
			if len(kv_arr) == 2:
				ret[kv_arr[0]] = kv_arr[1]
		return ret

if __name__ == '__main__':
	url = "http://news.abc.co.kr/web/game/view.php?a=1&b=2&c=3"
	parser = URLParser()
	parser.parse(url)