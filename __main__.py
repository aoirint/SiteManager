import sys
import site_mn
import cmd

if __name__ == '__main__':
	if len(sys.argv) == 2:
		running = True
		db_path = sys.argv[1]
		
		site_ = site_mn.Site(db_path)
		cmds = {
			'post': cmd.PostCmd(),
			'edit': cmd.EditCmd(),
			'pages': cmd.PagesCmd(),
			'link': cmd.LinkCmd(),
			'links': cmd.LinksCmd(),
			'out': cmd.OutCmd(),
			'config': cmd.ConfigCmd()
		}
		
		while running:
			input_text = input('> ').strip()
			if len(input_text) == 0:
				continue
			
			cmdv = input_text.split(' ')
			opts = []
			for v in cmdv:
				if len(v) > 1 and v[0] == '-' and not v[1].isnumeric():
					opts.append(v)
			
			for v in opts:
				cmdv.remove(v)
			
			cmdc = len(cmdv)
			if cmdc == 0:
				continue
			
			id = None
			if cmdv[0] in ('exit', 'q'):
				running = False
			elif cmdv[0] in cmds:
				if '-h' in opts:
					cmds[cmdv[0]].print_help()
				else:
					cmds[cmdv[0]](cmdv, cmdc, opts, site_)
			elif cmdv[0] in ('help', '?'):
				print('''Help
Command List:
To read help for each command, use '-h' option.''')
				for k in cmds:
					print('	' + k)
				print('''	help/?
	exit/q''')
			else:
				print('Invalid command: ' + input_text)
		
		site_.close()
	else:
		pass
