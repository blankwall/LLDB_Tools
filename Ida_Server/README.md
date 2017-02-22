#LLDB Ida Server

This is a simple bridge between Ida and LLDB via sockets. A simple example is given to resolve some virtual calls. Run virtual_call.py and the ida_server in IDA. Then load the program into lldb and import lldb_ida.py and the data will be sent during execution.