# -*- coding: utf-8 -*-
import sys
print(sys.version)
import gdb

# 设置gdb的一些参数
# 不中断输出
gdb.execute("set pagination off")
# 格式化输出
gdb.execute("set print pretty on")

# 设置断点
gdb.execute("break func")

# 启动程序
gdb.execute("run")

# #获取寄存器信息
# the_line = gdb.execute("info registers rip", to_string=True)
# gdb.execute("dump memory memory.dump $rip $rip+100")

# 获取当前堆栈帧
frame = gdb.selected_frame()

# 获取父类指针
# parent_ptr = frame.read_var("b")
parent_ptr = gdb.parse_and_eval('b')
print("Derived class type:", parent_ptr.type)

print("Derived b.value:", parent_ptr['value'])
# child_ptr = parent_ptr.reinterpret_cast(gdb.lookup_type("Derived"))

# 获取父类指针的动态类型
# dynamic_type = parent_ptr.dynamic_type

# 打印子类类型
# print("Derived child class type:", child_ptr.value)

gdb.execute("continue")
gdb.execute("quit")

