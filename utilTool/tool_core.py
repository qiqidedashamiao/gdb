# -*- coding: utf-8 -*-
import os
import subprocess
import sys
# import gdb
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from tool import read_output, run_command, set_gdb_params, read_output_start

# # python 启动gdb接口
# # Start the gdb process core dump
# def start_gdb_core(gdb_path, exe_path, core_file_path):
#     # 加载其他 Python 脚本
    
#     gdb_process = None
#     set_gdb_params(gdb_process)
#     return gdb_process


def start_gdb_core(gdb_path, exe_path, core_file_path, show=True):
    gdb_process = subprocess.Popen([gdb_path, exe_path, core_file_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = read_output_start(gdb_process)
    if show:
        print(output)
    set_gdb_params(gdb_process, show)
    return gdb_process