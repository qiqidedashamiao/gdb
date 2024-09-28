# -*- coding: utf-8 -*-
import subprocess

# Start the gdb process
def start_gdb(gdb_path, exe_path):
    gdb_process = subprocess.Popen([gdb_path, exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = read_output(gdb_process)
    print(output)
    set_gdb_params(gdb_process)
    return gdb_process

# 设置gdb的一些参数
def set_gdb_params(gdb_process):
    res = run_command(gdb_process, 'set pagination off')
    print(res)
    res = run_command(gdb_process, 'set print pretty on')
    print(res)

# 读输出
def read_output(gdb_process):
    output = b""
    while True:
        line = gdb_process.stdout.read(1)
        output += line
        # (gdb)表示输出结束
        if output.endswith(b'(gdb)'):
            break
    return output

# 发送命令和接收输出  command: 命令，示例：'set pagination off'
def run_command(gdb_process, command):
    # print("send command: ", command)
    print("send command: {}".format(command))
    command = (command + '\n').encode('utf-8')
    gdb_process.stdin.write(command)
    gdb_process.stdin.flush()
    if command == b'quit\n':
        return ""
    output = read_output(gdb_process)
    return output

# 设置断点 breakpoints: 断点列表，示例：['func', 'Derived::print'] 
def set_breakpoints(gdb_process, breakpoints):
    for bp in breakpoints:
        res = run_command(gdb_process, 'break {}'.format(bp))
        print(res)

# 获取断点号
# 假设返回结果包含类似 "Breakpoint 1, func (b=0x603010) at zilei.cpp:30" 的信息
def get_breakpoint_number(output):
    breakpoint_number = -1
    if 'Breakpoint' in output:
        breakpoint_number = int(output.split('Breakpoint ')[1].split(',')[0])
    return breakpoint_number

# 查看断点是否命中index，未命中则继续运行
def find_breakpoint_number(gdb_process, output, breakpoint_index):
    breakpoint_number = get_breakpoint_number(output)
    if breakpoint_number == breakpoint_index:
        print("Breakpoint {} hit".format(breakpoint_index))
        return True
    else:
        res = run_command(gdb_process, 'continue')
        print(res)
        return find_breakpoint_number(gdb_process, res, breakpoint_index)

