def check_objc(msg_addr):
	rdi = a.prevreg(msg_addr, 'rdi', write=True) # location where rdi is loaded
	rsi = a.prevreg(msg_addr, 'rsi', write=True) # location where rsi is loaded

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
		refs = db.xref.data_up(db.xref.data_down(data)[0])

		if len(refs) <= 1:
			print "NOT FOUND"
			return

		addr = refs[0]
		name = idc.Qword(addr)
		unk = idc.Qword(addr+8)
		func = idc.Qword(addr+16)

		db.tag(msg_addr, 'objc', hex(func))
		try:
			db.xref.add_code(msg_addr,func)
		except Exception as e:
			pass
	else:
		print "NOT FOUND"
