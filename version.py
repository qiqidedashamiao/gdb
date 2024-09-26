import sys
print(sys.version)
import gdb

gdb.execute("break *digui")
gdb.execute("run")

the_line = gdb.execute("info registers rip", to_string=True)
gdb.execute("dump memory memory.dump $rip $rip+100")