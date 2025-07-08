gdb 加载python版本
source version.py

执行gdb命令
gdb.execute("break func")

获取执行命令的输出结果带上参数to_string=True
the_line = gdb.execute("info registers rip", to_string=True)

生成core文件
ulimit -c unlimited

tool.py gdb操作的一些封装函数

tool_core.py  gdb core操作的一些函数


detect_mutex_lock.py   检测死锁，依赖于tool.py  和 tool_core.py

memory.py  生成自定义命令，检测输入的堆地址是否被别人使用

