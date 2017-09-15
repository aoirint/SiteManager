import os
import datetime
import tempfile

FORMATS = [
	{
		'key': 'html',
		'extension': '.html',
		'template': '''<!DOCTYPE html>
<meta charset="UTF-8">
<title>%(title)s</title>

<h1>%(title)s</h1>
'''
	},
	{
		'key': 'markdown',
		'extension': '.md',
		'template': '''# %(title)s
'''
	}
]
EDIT = 'vim %s'


FORMAT_KEYS = [v['key'] for v in FORMATS]


def edit_temp(content='',suffix=''):
	with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as fp:
		if len(content) != -1:
			fp.write(content)
		path = fp.name
	
	before = os.path.getmtime(path)
	os.system(EDIT % path)
	
	with open(path, 'r') as fp:
		return (fp.read(), before != os.path.getmtime(path))

def print_formats():
		for i in range(len(FORMATS)):
			print(str(i) + ':', FORMAT_KEYS[i])

def to_format(keyOrIdx):
	if not keyOrIdx in FORMAT_KEYS:
		if keyOrIdx.isdecimal():
			id = int(keyOrIdx)
			if 0 <= id and id < len(FORMATS):
				return FORMATS[id]
	else:
		key = keyOrIdx
		return FORMATS[FORMAT_KEYS.index(key)]
	return None

class Cmd:
	def __call__(self, cmdv, cmdc, opts, site):
		print('Cmd')
		pass


class PagesCmd(Cmd):
	def __call__(self, cmdv, cmdc, opts, site):
		print('PagesCmd')
		if not cmdc in (1, 2):
			print('Invalid call: The number of arguments must be 0 or 1, pages, pages <limit or id_range>')
			return False
		
		cursor = site.db.cursor()
		limit = None
		id_range = None
		order_flag = True
		if '-r' in opts:
			order_flag = not order_flag
		
		if cmdc == 1:
			if not '-a' in opts:
				limit = 10
			else:
				order = 'ASC' if order_flag else 'DESC'
				cursor.execute('SELECT id,title,modifiedTime FROM pages ORDER BY id %s' % order)
		elif cmdc == 2:
			if cmdv[1].isdecimal():
				limit = int(cmdv[1])
			elif '-' in cmdv[1]:
				id_range = cmdv[1].split('-')
		
		
		if limit != None:
			order = 'DESC' if order_flag else 'ASC'
			cursor.execute('SELECT id,title,modifiedTime FROM pages ORDER BY modifiedTime %s LIMIT ?' % order, (limit,))
		elif id_range != None:
			if id_range[0] > id_range[1]:
				order_flag = not order_flag
			
			order = 'ASC' if order_flag else 'DESC'
			cursor.execute('SELECT id,title,modifiedTime FROM pages WHERE id BETWEEN ? AND ? ORDER BY id %s' % order, (id_range[0], id_range[1]))
		
		
		print('id'.rjust(4), 'title'.ljust(16), 'modified')
		for row in cursor.fetchall():
			modified = datetime.datetime.fromtimestamp(row[2])
			print(str(row[0]).rjust(4), row[1].ljust(16), modified.isoformat())
		
		cursor.close()

	def print_help(self):
		print('''PagesCmd:
	pages:
		最新のページ10件を取得、更新時刻の降順で表示する
	pages N:
		最新のページN件を取得、更新時刻の降順で表示する
	pages A-B:
		ID AからBのページを取得、IDの昇順で表示する

オプション
	-r: 出力順を反転
	-a: 引数0個のとき、すべてのページを取得、IDの昇順で表示する
''')

class PostCmd(Cmd):
	def __call__(self, cmdv, cmdc, opts, site):
		print('PostCmd')
		if cmdc != 1:
			print('Invalid call: The number of arguments must be 0, post')
			return False
		
		title = input('Title: ') or 'No title'
		print(title)
		
		print(' Formats '.center(28, '-'))
		print_formats()
		print('-' * 28)
		
		format = to_format(input('Format: ') or FORMAT_KEYS[0])
		if format == None:
			print('Canceled:', 'No such format \'%s\'' % format)
			return False
		print(format['key'])
		
		print('Body:', end=' ')
		body, updated = edit_temp(content=format['template'], suffix=format['extension'])
		print(len(body), 'chars')
		
		if len(body) == 0:
			print('Canceled:', 'Null body')
			return False
		elif not updated:
			print('Canceled:', 'No update')
			return False
		else:
			id = site.post(None, title, format['key'], body)
			
			print('Posted:', '\'%s\'' % title, 'as ID(%d)' % id)
			return True

	def print_help(self):
		print('''PostCmd:
	post:
		新規にページを投稿する''')

class EditCmd(Cmd):
	def __call__(self, cmdv, cmdc, opts, site):
		print('EditCmd')
		if cmdc != 2:
			print('Invalid call: The number of arguments must be 1, edit <id>')
			return False
		if not cmdv[1].isdecimal():
			print('Invalid argument:', 'ID must be an integer')
			return False
		
		id = int(cmdv[1])
		if not site.exists(id):
			print('Invalid argument:', 'No such page exists', 'ID=' + str(id))
			return False
		
		cursor = site.db.cursor()
		cursor.execute('SELECT title,format,body from pages WHERE id=?', (id, ))
		title, format, body = cursor.fetchone()
		cursor.close()
		
		title_updated = False
		format_updated = False
		body_updated = False
		
		print('Title:', title)
		if input('Change title? (y/n)> ') == 'y':
			new_title = input('Title: ')
			if len(title) != 0:
				print('Updated title: %s -> %s' % (title, new_title))
				title = new_title
				title_updated = True
		
		print('Format:', format)
		if input('Change format? (y/n)> ') == 'y':
			print_formats()
			new_format = input('Format: ')
			if to_format(new_format) != None:
				print('Updated format: %s -> %s' % (format, new_format))
				format = new_format
				format_updated = True
		format = to_format(format)
		
		if input('Edit body? (y/n)> ') == 'y':
			print('Body:', end=' ')
			body, body_updated = edit_temp(body, suffix=format['extension'])
			print(len(body), 'chars')
		
			if len(body) == 0:
				print('Canceled:', 'Null body')
				return False
		
		if title_updated or format_updated or body_updated:
			id = site.post(id, title, format['key'], body)
			print('Edited:', '\'%s\'' % title, 'as ID(%d)' % id)
			return True
		else:
			print('Canceled:', 'No update')
			return False
	
	def print_help(self):
		print('''PostCmd:
	edit <id>:
		既存のページを編集する''')
