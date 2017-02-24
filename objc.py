hex = lambda x: "0x{:x}".format(x)

def check_objc(msg_addr):
	xref = db.xref()
	rdi = a.prevreg(msg_addr, 'rdi') # location where rdi is loaded
	rsi = a.prevreg(msg_addr, 'rsi') # location where rsi is loaded

	rdi_t = ins.op_type(rdi,1)
	rsi_t = ins.op_type(rsi,1)

	if rsi_t == 'register':
		new_reg = ins.op_value(rsi,1).name
		rsi =  a.prevreg(rsi, new_reg)
		rsi_t = ins.op_type(rsi,1)
		if rsi_t != 'phrase':
			print "NOT FOUND"
			return


	if rsi_t == 'phrase':
		data = ins.op_value(rsi, 1).offset
		xref = db.xref()
		refs = map(lambda x: hex(x), xref.data_down(data))
		refs = map(lambda x: hex(x), xref.data_up(int(refs[0],16)))

		if len(refs) <= 1:
			print "NOT FOUND"
			return

		addr = int(refs[0], 16)
		name = idc.Qword(addr)
		unk = idc.Qword(addr+8)
		func = idc.Qword(addr+16)

		db.comment(msg_addr, hex(func))

		try:
			xref.add_code(msg_addr,func)
		except:
			pass

	else:
		print "NOT FOUND"
