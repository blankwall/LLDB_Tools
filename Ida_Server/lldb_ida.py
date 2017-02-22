import lldb
import socket
from os.path import expanduser
home = expanduser("~")

HOST = 'localhost'
PORT = 11946
FILE = home + "/vfuncs.txt"
lookup = {}

class Addr:
	def __init__(self, addr, reg,offset, deref):
		self.addr =  int(addr,16)
		self.reg = reg
		self.offset = int(offset,16)
		self.deref = int(deref)

class Ida:
	def __init__(self):
		self.s = socket.socket()
		self.s.connect((HOST,PORT))
		self.color_value = 0x0000ff

	def comment(self, addr, comment):
		com = "idaapi.set_cmt({0}, \"{1}\", 0)".format(hex(addr), comment)
		self.s.send(com + "\n")

	def color(self, addr):
		color = "SetColor(" + addr + ", CIC_ITEM," + hex(self.color_value) +")"
		self.s.send(color)

	def send(self, mess):
		self.s.send(mess)

def test():
	print "HI"

def get_reg(interpret, reg):
	output = lldb.SBCommandReturnObject()
	interpret.HandleCommand("reg read " + reg, output)
	x = output.GetOutput()
	beg = 0
	for i in range(len(x)):
		if x[i] == '0' and x[i+1] == 'x':
			beg = i
		if beg != 0:
			if x[i] == ' ':
				break
	return int(x[beg:i], 16)

def read_mem(interpret, addr, size):
	output = lldb.SBCommandReturnObject()
	interpret.HandleCommand("memory read --size {0} --format x --count 1 {1}".format(size, addr), output)	
	return output.GetOutput().rstrip().split(" ")[-1]

def breakpoint_function (frame, bp_loc, dictp):
	global idob

	thread = frame.GetThread()
	ci = lldb.debugger.GetCommandInterpreter()
	output = lldb.SBCommandReturnObject()

	# If main thread is not current selected thread
	# ci.HandleCommand("thread select 2", output)

	rip = get_reg(ci, 'rip')
	lp = lookup[rip]
	reg = get_reg(ci, lp.reg)
	if lp.deref:
		deref = read_mem(ci, reg + lp.offset, 8)
	else:
		deref = hex(reg)

	idob.comment(rip, deref)
	idob.send("done")
	ci.HandleCommand("script print \"DATA SENT\"", output)
	ci.HandleCommand("continue", output)



idob = Ida()
ci = lldb.debugger.GetCommandInterpreter()
output = lldb.SBCommandReturnObject()

breaks = file(FILE).readlines()
for i in breaks:
	stuff = i.strip().split(" ")
	addr = Addr(stuff[0], stuff[1], stuff[2], stuff[3])
	lookup[addr.addr] = addr
	ci.HandleCommand("br set -o -a " + hex(addr.addr), output)
	print output.GetOutput()
	ci.HandleCommand("br com add -F lldb_ida.breakpoint_function", output)
