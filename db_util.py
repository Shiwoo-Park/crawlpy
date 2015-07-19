#!/usr/bin/env python2.7
# coding: utf8

import MySQLdb
import MySQLdb.cursors
from config.db_info import DB_INFO
from log import getLogger


def getDBConnection(host, usr, pwd, db, cursor_type="normal"):
	db_connect = None
	db_cursor = None
	try:
		if cursor_type == "dict":
			db_connect = MySQLdb.connect(host, usr, pwd, db, cursorclass=MySQLdb.cursors.DictCursor)
		else:
			db_connect = MySQLdb.connect(host, usr, pwd, db)
		db_connect.set_character_set('utf8')
		db_cursor = db_connect.cursor()
	except Exception, msg:
		getLogger().error("getDBCursor() Failed : %s"%msg)
	return db_connect, db_cursor


def getDBConnectionByName(name, cursor_type="normal"):
	if name in DB_INFO:
		return getDBConnection(DB_INFO["host"], DB_INFO["user"], DB_INFO["pwd"], DB_INFO["db"], cursor_type)
	return None


def selectQuery(dbCursor, query, params=()):
	dbCursor.execute(query, params)
	result = dbCursor.fetchall()
	return result


def executeQuery(dbCursor, query, params=(), desc=""):
	ret = desc
	dbCursor.execute(query, params)
	dbCursor.execute("commit")
	ret += " Success"
	return ret


# 쿼리의 WHERE 부분
def makeWhereClause(dic, keyList=None):
	whereClause = ""
	params = []
	if dic:
		for key,val in dic.items():
			add = False
			if keyList:
				if key in keyList:
					add = True
			else:
				add = True

			if add:
				if len(params) > 0:
					whereClause += " AND "
				whereClause += key+"=%s"
				params.append(val)

	return (whereClause, params)


def selectCount(dbCursor, tableName, whereDic=None, where="", params=()):
	if whereDic:
		where, params = makeWhereClause(whereDic)
		if len(params) > 0:
			where = " WHERE "+where

	query = "SELECT COUNT(1) FROM "+tableName + where
	dbCursor.execute(query, params)
	ret = dbCursor.fetchone()
	return ret[0]

def selectData(dbCursor, selectList, tableName, whereDic=None, where="", params=(), order="", limit=""):
	colStr = ""

	for col in selectList:
		colStr += col+","
	if len(colStr) > 0:
		colStr = colStr[:-1]

	if whereDic:
		where, params = makeWhereClause(whereDic)
		if len(params) > 0:
			where = " WHERE "+where

	query = "SELECT "+colStr+" FROM "+tableName + where + order + limit

	dbCursor.execute(query, params)
	ret = dbCursor.fetchall()
	return ret

def insertData(dbCursor, desc, tableName, dataDic, isIgnore=False):
	ret = "Insert "+desc+" Data"
	fields = ""
	values = ""
	params = []

	for key, val in dataDic.items() :
		fields += key+","
		values += "%s,"
		params.append(val)
	if len(params) > 0:
		fields = fields[:-1]
		values = values[:-1]

	if isIgnore:
		query = "INSERT IGNORE INTO "+tableName+" ("+fields+") VALUES ("+values+")"
	else:
		query = "INSERT INTO "+tableName+" ("+fields+") VALUES ("+values+")"

	dbCursor.execute(query, params)
	dbCursor.execute("commit")
	ret += " : Success"
	return ret

def updateData(dbCursor, desc, tableName, setDic, whereDic=None):
	ret = "Update "+desc+" Data"
	setClause = ""
	params = []
	for key,val in setDic.items():
		if len(params) > 0:
			setClause += ", "
		setClause += key+"=%s"
		params.append(val)

	whereClause = ""
	if whereDic:
		whereClause, whereParams = makeWhereClause(whereDic)
		whereClause = " WHERE "+whereClause
		params = params + whereParams

	query = "UPDATE "+tableName+" SET "+setClause + whereClause
	dbCursor.execute(query, params)
	dbCursor.execute("commit")
	ret += " : Success"
	return ret

def deleteData(dbCursor, desc, tableName, whereDic):
	ret = "Delete "+desc+" Data"
	whereClause, params = makeWhereClause(whereDic)
	query = "DELETE FROM "+tableName+" WHERE "+whereClause
	dbCursor.execute(query, params)
	dbCursor.execute("commit")
	ret += " : Success"
	return ret

if __name__ == "__main__":
	pass
