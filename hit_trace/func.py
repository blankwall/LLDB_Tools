from idautils import *
from idaapi import *
from os.path import expanduser
home = expanduser("~")

FILE = home + "/func.txt"

a = file(FILE, "w+")
a.close()
ea = BeginEA()
for funcea in Functions(SegStart(ea), SegEnd(ea)):
    functionName = GetFunctionName(funcea)
    functionStart = hex(funcea)[:-1]
    functionEnd = hex(FindFuncEnd(funcea))
    a = file(FILE, "a+")
    a.write(functionStart + "\n")
    a.close()

print "ALL DONE"