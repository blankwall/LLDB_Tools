import lldb
import sys, os


prog = sys.argv[1]
TIMEOUT = 10
attach = False
start_breaks = 0
verbose = False

class Break:
	addr = 0
	name = 1


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

def run_commands(command_interpreter, commands, verbose = 1):
	return_obj = lldb.SBCommandReturnObject()
	for command in commands:
		command_interpreter.HandleCommand(command, return_obj)
		if return_obj.Succeeded():
			return return_obj.GetOutput()


def add_break(interpret, addr, op=Break.addr):
	pre = "br set -o"
	output = lldb.SBCommandReturnObject()
	if op == Break.addr:
		interpret.HandleCommand(pre + " -a " + addr, output)
	elif op == Break.name:
		interpret.HandleCommand(pre + " -n " + addr, output)

def add_break_shared(interpret, addr, library, op=Break.addr):
	pre = "br set -o --shlib " + library
	output = lldb.SBCommandReturnObject()
	if op == Break.addr:
		interpret.HandleCommand(pre + " -a " + addr, output)
	elif op == Break.name:
		interpret.HandleCommand(pre + " -n " + addr, output)

def analyze(debugger, verbose = 0):
	command_interpreter = debugger.GetCommandInterpreter()
	brs = breaklist(command_interpreter)
	print "Breaks not hit: "
	print brs[1:]

	not_hit = start_breaks - (len(brs)-1)
	percent = (not_hit  / float(start_breaks)) * 100

	print "\n---------\nNot Hit", len(brs)-1
	print "% hit " + str(percent)

def cleanup(debugger):
	analyze(debugger,1)
	lldb.SBDebugger.Terminate()
	exit()

def breaklist(command_interpreter):
	return [line for line in run_commands(command_interpreter, ['breakpoint list -b'],1).split('\n') if line.strip() != '']

def usage():
	print "lldb-trace.py program to trace [-v] <(filecontainingbreaks.txt |  -sh SharedLibraryName shbreaks.txt)> "
	print "Example: ", "lldb-trace.py /Applications/Preview.app/Contents/MacOS/Preview -sh SceneKit funcs.txt"
	exit()

class Config:
	def __init__(self):
		self.shared = []
		self.breaks = []
		self.app = ""

	def display(self):
		print self.app, self.shared, self.breaks

	def parse(self, argv):
		global verbose
		try:
			self.app = argv[0]
			argv = argv[1:]
			sh = False
			count = 0
			for i in range(len(argv)):
				if i > count:
					sh = False
				if i > (len(argv)-1):
						break

				if argv[i] == '-sh':
					sh_lib = {argv[i+1] : argv[i+2]}
					self.shared.append(sh_lib)
					sh = True
					count = i+2

				elif argv[i] == '-v':
					verbose = True
				else:
					if not sh:
						self.breaks.append(argv[i])
		except Exception, e:
			usage()


def main(argv):
	global start_breaks, attach, verbose

	parse = Config()
	parse.parse(argv)
	if verbose:
		parse.display()

	debugger = lldb.SBDebugger.Create()
	debugger.SetAsync(True)
	command_interpreter = debugger.GetCommandInterpreter()

	print "Creating a target for '%s'" % parse.app

	error = lldb.SBError()
	target = debugger.CreateTarget(parse.app, None, None, True, error)


	try:
		for dicti in parse.shared:
			for shlib in dicti:
				sh_break = [i for i in file(dicti[shlib], "r").read().split("\n") if i != '']
				[add_break_shared(command_interpreter, x , shlib) for x in sh_break]

		for breakpoint in parse.breaks:
			main_break = [i for i in file(breakpoint, "r").read().split("\n") if i != '']
			[add_break(command_interpreter, x) for x in main_break]

	except:
		usage()


	brs = breaklist(command_interpreter)
	print "TOTAL NUMBER OF BREAKS = ", len(brs) - 1
	start_breaks = len(brs) - 1


	if verbose:
		print "Current breaks: "
		print brs[1:]


	launchinfo = lldb.SBLaunchInfo([])
	launchinfo.SetWorkingDirectory(os.getcwd())
	process = target.Launch(launchinfo, error)

	if process or process.GetProcessID() != lldb.LLDB_INVALID_PROCESS_ID:
		pid = process.GetProcessID()
		print "PID = %d\n" % pid
		listener = debugger.GetListener()

		done = False
		found = False
		event = lldb.SBEvent()

		while not done:
			if listener.WaitForEvent(TIMEOUT, event):
				if lldb.SBProcess.EventIsProcessEvent(event):
					state = lldb.SBProcess.GetStateFromEvent(event)

					if state == lldb.eStateInvalid:
						continue
					elif state == 10:
						cleanup(debugger)
					else:
						if state == lldb.eStateStopped:
							if attach:
								attach = False
								process.Continue()

							pid = process.GetProcessID()

							for thread in process:
								if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
									process.SetSelectedThread(thread)
									break

							reason = thread.GetStopReason()
							state = process.GetState()

							if reason == lldb.eStopReasonNone:
								if state == 6:
									continue
								elif state == 10:
									print "Program exited - " + str(process.GetExitStatus())
									cleanup(debugger)
								elif state == 5:
									print "No stop reason destroying for now"
									lldb.SBDebugger.Terminate()
									exit()

							elif reason == lldb.eStopReasonInvalid:
								continue

							elif reason == lldb.eStopReasonBreakpoint:
								rip = get_reg(command_interpreter, "rip")
								try:
									breakpoints[rip].hit = 1
								except:
									pass
								process.Continue()
							else:
								print reason + "-+-+-+-+"
								process.Continue()
			else:
				print "Program Timed out "
				cleanup(debugger)


if __name__ == '__main__':
    main(sys.argv[1:])
