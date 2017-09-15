import time
import sqlite3

class Site:
	def __init__(self, db_path):
		self.db_path = db_path
		self.db = sqlite3.connect(db_path)
		
		cursor = self.db.cursor()
		cursor.execute('CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY AUTOINCREMENT, postedTime INTEGER, modifiedTime INTEGER, title TEXT, format TEXT, body TEXT)')
		self.db.commit()
		cursor.close()
	
	def post(self, id, title, format, body):
		now = int(time.time())
		cursor = self.db.cursor()
		
		postedTime = now
		if id != None:
			cursor.execute('SELECT postedTime FROM pages WHERE id=?', (id, ))
			row = cursor.fetchone()
			if row != None:
				postedTime = row[0]
		
		cursor.execute('REPLACE INTO pages(id,postedTime,modifiedTime,title,format,body) VALUES(?,?,?,?,?,?)', (id, postedTime, now, title, format, body))
		self.db.commit()
		
		cursor.execute('SELECT id FROM pages WHERE ROWID=last_insert_rowid()')
		row = cursor.fetchone()
		cursor.close()
		
		return row[0] if row != None else None
	
	def exists(self, id):
		cursor = self.db.cursor()
		cursor.execute('SELECT COUNT(*) FROM pages WHERE id=?', (id, ))
		result = cursor.fetchone()[0]
		cursor.close()
		
		return result != 0
	
	def close(self):
		self.db.close()
	
