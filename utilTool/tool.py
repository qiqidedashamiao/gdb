# -*- coding: utf-8 -*-
import subprocess


# gdb 中使用source命令 
# import gdb
# # gdb 交互式接口
# # Start the gdb process
# def start_gdb(gdb_path, exe_path):
#     gdb_process = None
#     set_gdb_params(gdb_process)
#     return gdb_process
# # 发送命令和接收输出  command: 命令，示例：'set pagination off'
# def run_command(gdb_process, command):
#     print("send command: {}".format(command))
#     output = gdb.execute(command, to_string=True)
#     return output

# # 发送命令  command: 命令，示例：'set pagination off'
# def run_command_nowait(gdb_process, command):
#     print("send command: {}".format(command))
#     gdb.execute(command)

# python 启动gdb接口
# Start the gdb process
def start_gdb(gdb_path, exe_path):
    gdb_process = subprocess.Popen([gdb_path, exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = read_output_start(gdb_process)
    print(output.decode('utf-8'))  # 解码为字符串
    set_gdb_params(gdb_process)
    return gdb_process

# 发送命令和接收输出  command: 命令，示例：'set pagination off'
def run_command(gdb_process, command, show=True):
    # print("send command: ", command)
    if show:
        print("send command: {}".format(command))
    command = (command + '\n').encode('utf-8')
    gdb_process.stdin.write(command)
    gdb_process.stdin.flush()
    if command == b'quit\n':
        return ""
    output = read_output(gdb_process)
    return output

# 发送命令  command: 命令，示例：'set pagination off'
def run_command_nowait(gdb_process, command, show=True):
    if show:
        print("send command: {}".format(command))
    command = (command + '\n').encode('utf-8')
    gdb_process.stdin.write(command)
    gdb_process.stdin.flush()
    if command == b'quit\n':
        return ""
    read_output(gdb_process)
    # return output



# 设置gdb的一些参数
def set_gdb_params(gdb_process, show=True):
    res = run_command(gdb_process, 'set pagination off', show)
    if show:
        print(res)
    res = run_command(gdb_process, 'set print pretty on', show)
    if show:
        print(res)

# 读输出
def read_output(gdb_process):
    output = b""
    while True:
        line = gdb_process.stdout.read(1)
        output += line
        # print(f"out:{output}")
        # (gdb)表示输出结束
        if output.endswith(b'(gdb)'):
            break
    return output.decode('utf-8')  # 解码为字符串

# 读输出
def read_output_start(gdb_process):
    output = b""
    while True:
        line = gdb_process.stdout.read(1)
        output += line
        # (gdb)表示输出结束
        if output.endswith(b'\n(gdb)'):
            break
    return output.decode('utf-8')  # 解码为字符串

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

