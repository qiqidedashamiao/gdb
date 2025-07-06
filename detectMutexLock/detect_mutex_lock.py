# -*- coding: utf-8 -*-
'''
只能检测应用层使用Mutex的enter和leave，不能检测系统调用的Mutex其他直接调用pthread_mutex_lock的情况
'''
import os
import re
import sys
# import gdb
# 添加上一层目录到模块搜索路径
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from utilTool.tool import run_command
from utilTool.tool_core import start_gdb_core


#判断当前栈信息是否正在执行mutex_lock函数
def parse_mutex_lock(bt_res):
    value_dict = {}
    mutex_name = ''
    #判断当前栈信息是否正在执行mutex_lock函数
    frames = bt_res.split('\n')
    for frame in frames:
        '''
        lock_guard<mutex>
        #2  0x00007f1700a0ed68 in pthread_mutex_lock () from /lib64/libpthread.so.0
        #3  0x000000000040119c in __gthread_mutex_lock (__mutex=0x607340 <mtx2>) at /usr/include/c++/4.8.2/x86_64-redhat-linux/bits/gthr-default.h:748
        (gdb) p *__mutex 
        $2 = {__data = {__lock = 2, __count = 0, __owner = 21599, __nusers = 1, __kind = 0, __spins = 0, __elision = 0, __list = {__prev = 0x0, __next = 0x0}}, 
        '''
        if 'mutex=' in frame:
            # print(bt_res)
            # value_dict = {}
            # value_dict['thread_index'] = thread_index
            value_dict['frame'] = bt_res
            # 使用正则表达式分割字符串，正则表达式最外层必须加上[]
            parts = re.split(r'[ )]', frame.split('=')[1])
            value_dict['addr'] = parts[0]
            # print(value_dict)
            mutex_name = frame.split('(')[1].split('=')[0]
            frame_index = frame.split('#')[1].split()[0]
            res = run_command(gdb_process, 'frame {}'.format(frame_index), False)
            # print(res)
            if mutex_name == '__mutex':
                res = run_command(gdb_process, 'p *{}'.format(mutex_name), False)
            elif mutex_name == 'mutex':
                res = run_command(gdb_process, 'p  {}'.format(mutex_name), False)
            # print(res)
            #解析出__lock、__count、__owner、__nusers、__kind、__spins、__elision的值
            parts = res.split('\n')
            for part in parts:
                if '__lock' in part:
                    value_dict['__lock'] = int(part.split('=')[1].split(',')[0])
                elif '__count' in part:
                    value_dict['__count'] = int(part.split('=')[1].split(',')[0])
                elif '__owner' in part:
                    value_dict['__owner'] = int(part.split('=')[1].split(',')[0])
                elif '__nusers' in part:
                    value_dict['__nusers'] = int(part.split('=')[1].split(',')[0])
                elif '__kind' in part:
                    value_dict['__kind'] = int(part.split('=')[1].split(',')[0])
                elif '__spins' in part:
                    value_dict['__spins'] = int(part.split('=')[1].split(',')[0])
                elif '__elision' in part:
                    value_dict['__elision'] = int(part.split('=')[1].split(',')[0])
            break
    return value_dict

if __name__ == '__main__':
    sonia_path = "../a.out"
    core_path = '../core.26120'
    # 如果是直接运行脚本，则使用命令行参数中的core文件
    if len(sys.argv) > 2 :
        sonia_path = sys.argv[1]
        core_path = sys.argv[2]
    # Start the gdb process
    # print("start")
    gdb_process = start_gdb_core('gdb', sonia_path, core_path, False)
    # print("gdb start success")

    # 打印当前线程的调用栈
    res = run_command(gdb_process, 'bt', False)
    # print(res)

    #获取当前实际的线程号
    #[Current thread is 4 (Thread 0x7f46d0a19700 (LWP 21600))]
    res = run_command(gdb_process, 'thread', False)
    # print(res)
    thread_id = int(res.split('LWP ')[1].split(')')[0])
    thread_index = 1

    mutex_dict = {}

    value_dict = parse_mutex_lock(res)
    if len(value_dict) > 0:
        value_dict['thread_index'] = thread_index
        mutex_dict[thread_id] = value_dict
        value_dict_copy = value_dict.copy() # 复制一份，避免删除frame字段
        value_dict_copy.pop('frame', None) # 如果键不存在，不会引发 KeyError
        # print('{}:{}'.format(thread_id, value_dict_copy))

    # 获取线程个数并打印所有的线程栈信息
    # * 1    Thread 0x7f46d0a19700 (LWP 21600) 0x000000000040119c in __gthread_mutex_lock (__mutex=0x607340 <mtx2>)
    res = run_command(gdb_process, 'info threads', False)
    # print(res)
    threads = res.split('\n')
    for thread in threads:
        if 'Thread' in thread or 'LWP' in thread:
            thread_index = thread.strip('*').split()[0]
            thread_index = int(thread_index)
            if thread_index == 1:
                continue
            thread_id = int(re.split(r'[ )]', thread.split('LWP ')[1])[0])
            res = run_command(gdb_process, 'thread {}'.format(thread_index), False)
            # print(res)
            res = run_command(gdb_process, 'bt', False)
            # print(res)
            value_dict = parse_mutex_lock(res)
            if len(value_dict) > 0:
                value_dict['thread_index'] = thread_index
                mutex_dict[thread_id] = value_dict
                value_dict_copy = value_dict.copy() # 复制一份，避免删除frame字段
                value_dict_copy.pop('frame', None) # 如果键不存在，不会引发 KeyError
                # print('{}:{}'.format(thread_id, value_dict_copy))


    print('------------------------detect end---------------------------------')
    # for key in mutex_dict:
    #     print('{}:'.format(key))
    #     value_dict_copy = mutex_dict[key].copy() # 复制一份，避免删除frame字段
    #     value_dict_copy.pop('frame', None) # 如果键不存在，不会引发 KeyError
    #     print('{}'.format(value_dict_copy))
    #     print('{}'.format(mutex_dict[key]['frame']))

    lock_detect = False
    lock_thread_id = []

    for key in mutex_dict:
        thread_id = key
        value_dict = mutex_dict[key]
        __owner = value_dict['__owner']
        temp_thread_id = [thread_id]
        # print('--------------------------------------------------------')
        # print(f"thread_id: {thread_id}, __owner: {__owner}, temp_thread_id: {temp_thread_id}")
        #判断__owner是否在mutex_dict中
        count = 0
        used = {}
        while __owner in mutex_dict:
            count += 1
            if count > mutex_dict.__len__():
                print('Too many iterations, breaking to avoid infinite loop.')
                break
            if __owner == thread_id:
                # temp_thread_id.append(__owner)
                lock_detect = True
                lock_thread_id = temp_thread_id
                break
            used[__owner] = True
            temp_thread_id.append(__owner)
            __owner = mutex_dict[__owner]['__owner']
            if __owner in used:
                print('Detected a cycle, breaking to avoid infinite loop.')
                break
            
            # print(f"2thread_id: {thread_id}, __owner: {__owner}, temp_thread_id: {temp_thread_id}")
        if lock_detect:
            break

    # # 打印所有线程的调用栈
    # res = run_command(gdb_process, 'thread apply all bt')
    # print(res)

    # 退出
    # res = run_command(gdb_process, 'quit')

    # lock_detect = False

    if lock_detect:
        print('--------------------------------------------------------')
        print('----------------Deadlock detected success:-----------------')
        for thread_id in lock_thread_id:
            print('{}:'.format(thread_id))
            value_dict_copy = mutex_dict[key].copy() # 复制一份，避免删除frame字段
            value_dict_copy.pop('frame', None) # 如果键不存在，不会引发 KeyError
            print('{}'.format(value_dict_copy))
            print('{}'.format(mutex_dict[thread_id]['frame']))
    else:
        print('---------------------------------------------------------')
        print('----------------Deadlock detected failed-----------------')
        for key in mutex_dict:
            print('{}:'.format(key))
            value_dict_copy = mutex_dict[key].copy() # 复制一份，避免删除frame字段
            value_dict_copy.pop('frame', None) # 如果键不存在，不会引发 KeyError
            print('{}'.format(value_dict_copy))
            print('{}'.format(mutex_dict[key]['frame']))