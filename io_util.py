def saveIntoFile(context, path):
	f = open(path, 'a')
	f.write(context+"\n")
	f.close()


def readFile(path):
	f = open(path)
	text = f.read()
	f.close()
	return text


def readFileAsList(path):
	f = open(path)
	lines = f.readlines()
	f.close()
	return lines
