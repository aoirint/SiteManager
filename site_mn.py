import time
import sqlite3

class Site:
	def __init__(self, db_path):
		self.db_path = db_path
		self.db = sqlite3.connect(db_path)
		
		cursor = self.db.cursor()
		cursor.execute('CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY AUTOINCREMENT, postedTime INTEGER, modifiedTime INTEGER, title TEXT, format TEXT, body TEXT)')
		cursor.execute('CREATE TABLE IF NOT EXISTS links (path TEXT UNIQUE, id INTEGER, lastOutTime INTEGER)')
		cursor.execute('CREATE TABLE IF NOT EXISTS config (key TEXT UNIQUE, value TEXT)')
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
		
		cursor.execute('SELECT * FROM pages WHERE ROWID=last_insert_rowid()')
		row = cursor.fetchone()
		cursor.close()
		
		if row == None:
			return None
		return {
			'id': row[0],
			'postedTime': row[1],
			'modifiedTime': row[2],
			'title': row[3],
			'format': row[4],
			'body': row[5]
		}
	
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
	
	def remove_link(self, path, delete=False):
		cursor = self.db.cursor()
		if delete:
			cursor.execute('DELETE FROM links WHERE path=?', (path, ))
		else:
			cursor.execute('UPDATE links SET id=NULL WHERE path=?', (path, ))
		self.db.commit()
		cursor.close()
	
	def path_exists(self, path):
		cursor = self.db.cursor()
		cursor.execute('SELECT COUNT(*) FROM links WHERE path=?', (path, ))
		flag = cursor.fetchone()[0] != 0
		cursor.close()
		return flag
	
	def on_out(self, path):
		now = int(time.time())
		
		cursor = self.db.cursor()
		cursor.execute('UPDATE links SET lastOutTime=? WHERE path=?', (now, path))
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
	
	def get_config(self, key):
		cursor = self.db.cursor()
		cursor.execute('SELECT value FROM config WHERE key=?', (key, ))
		row = cursor.fetchone()
		cursor.close()
		
		if row != None:
			return row[0]
		return None

	def set_config(self, key, value):
		cursor = self.db.cursor()
		cursor.execute('REPLACE INTO config VALUES(?,?)', (key, value))
		row = cursor.fetchone()
		self.db.commit()
		cursor.close()
		
	def close(self):
		self.db.close()
	
