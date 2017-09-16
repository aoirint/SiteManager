import time
import sqlite3

class Site:
	def __init__(self, db_path):
		self.db_path = db_path
		self.db = sqlite3.connect(db_path)
		
		cursor = self.db.cursor()
		cursor.execute('CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY AUTOINCREMENT, postedTime INTEGER, modifiedTime INTEGER, title TEXT, format TEXT, body TEXT)')
		cursor.execute('CREATE TABLE IF NOT EXISTS links (path TEXT UNIQUE, id INTEGER, lastOutTime INTEGER)')
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
	
	def add_link(self, path, id):
		if not self.exists(id):
			return False
		
		cursor = self.db.cursor()
		cursor.execute('REPLACE INTO links VALUES(?,?,NULL)', (path, id))
		self.db.commit()
		cursor.close()
		return True
	
	def remove_link(self, path):
		cursor = self.db.cursor()
		cursor.execute('DELETE FROM links WHERE path=?', (path, ))
		self.db.commit()
		cursor.close()
	
	def on_out(self, path):
		now = int(time.time())
		
		cursor = self.db.cursor()
		cursor.execute('UPDATE links SET lastOutTime=? WHERE path=?', (path, now))
		self.db.commit()
		cursor.close()
	
	def get_last_out_time(self, path):
		cursor = self.db.cursor()
		cursor.execute('SELECT lastOutTime FROM links WHERE path=?', (path, ))
		row = cursor.fetchone()
		cursor.close()
		
		if row != None:
			return row[0]
		return None
	
	def close(self):
		self.db.close()
	
