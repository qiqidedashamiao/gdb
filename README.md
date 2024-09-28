gdb 加载python版本
source version.py

执行gdb命令
gdb.execute("break func")

获取执行命令的输出结果带上参数to_string=True
the_line = gdb.execute("info registers rip", to_string=True)