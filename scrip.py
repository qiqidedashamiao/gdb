# -*- coding: utf-8 -*-
# scrip.py
from tool import find_breakpoint_number, run_command, set_breakpoints, start_gdb
# Start the gdb process
print("start")
gdb_process = start_gdb('gdb', 'a.out')
print("gdb start success")

# Set a breakpoint
breakpoints = ['func', 'Derived::print']
set_breakpoints(gdb_process, breakpoints)

# Start the program
res = run_command(gdb_process, 'run')
print(res)

# Wait for the breakpoint to be hit
find_breakpoint_number(gdb_process, res, 2)

res = run_command(gdb_process, 'info locals')
print(res)

res = run_command(gdb_process, 'p *this')
print(res)

# 退出
res = run_command(gdb_process, 'quit')
