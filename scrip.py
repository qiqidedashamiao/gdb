# -*- coding: utf-8 -*-
import subprocess
# Start the gdb process
gdb_process = subprocess.Popen(['gdb', 'a.out'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 发送命令和接收输出
# Set some gdb parameters
# gdb_process.stdin.write(b"set pagination off\n")
# gdb_process.stdin.write(b"set print pretty on\n")

print("start")
gdb_process.stdin.write(b"\n")
gdb_process.stdin.flush()
output = b""
while True:
    line = gdb_process.stdout.readline()
    if not line:
        break  # 如果GDB关闭stdout或者出错，退出循环
    output += line
    # 检查是否出现(gdb)提示符
    if output.endswith(b'(gdb)'):
        break
print(output)

def run_command(command):
    command = (command + '\n').encode('utf-8')
    gdb_process.stdin.write(command)
    print("send command: ", command)
    gdb_process.stdin.flush()
    output = ''
    while True:
        line = gdb_process.stdout.readline().decode('utf-8')
        print("receive line: ", line.encode('utf-8'))
        output += line

        if line.strip() == '(gdb)':
            break
    return output

# print(run_command('break func'))
breakpoints = ['func']
for bp in breakpoints:
    print(run_command('break {}'.format(bp)))

print(run_command('run'))

print(run_command('quit'))
