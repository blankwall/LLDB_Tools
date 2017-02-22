from idautils import *
from idaapi import *
from idc import *
from os.path import expanduser
home = expanduser("~")

FILE = home + "/vfuncs.txt"


reg = ["rax", "rbx", "rcx", "rdx", "rdi", "rsi"]

# FORMAT = addr reg offset

a = file(FILE, "w+")
a.close()
ea = BeginEA()
addr = SegStart(ea)
end = SegEnd(addr)
print hex(addr), hex(end)


while addr < end and addr != BADADDR:
	f = GetMnem(addr)
	disas = GetDisasm(addr)
	#FIX ME: add objc support
	regge = ""
	offset = "0x0"
	deref = False
	if f == 'call' and "objc" not in disas:
		for i in reg:
			if i in disas:
				op1 = GetOpnd(addr,0)
				if len(op1) > 3:
					continue
				index = op1.find("[")
				if index == -1:
					regge = op1
				else:
					deref= True
					index2 = op1.find("]")
					regge = op1[index+1:index2]
					index3 = op1.find("+")
					if index3 != -1:
						regge = op1[index+1:index3]
						offset = "0x" + op1[index3+1:index2]
				if "h" in offset:
					offset = offset[:-1]
				a = file(FILE, "a")
				a.write("0x{:x} {:s} {:s} {:b}\n".format(addr, regge, offset, deref))
				a.close()
	addr = NextHead(addr, BADADDR)

print "ALL DONE"