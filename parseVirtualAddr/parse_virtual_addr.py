# -*- coding: utf-8 -*-
'''
只能检测应用层使用Mutex的enter和leave，不能检测系统调用的Mutex其他直接调用pthread_mutex_lock的情况
'''
import subprocess
import sys
import readline
import os
import atexit
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#添加上一层目录到模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__)) 
parent_dir = os.path.dirname(current_dir) 
# print(parent_dir)
sys.path.append(parent_dir)
from utilTool.tool import run_command
from utilTool.tool_core import start_gdb_core


# 定义一个函数，用于解析core文件使用
def parse_core_file(core_file_path):
    # 在这里编写解析core文件的代码
    pass

# 定义一个类，用于core文件相关的操作
class CoreFile:
    def __init__(self, config):
        # 初始化配置
        print("init core file")
        self.config = config
        # 判断目录data是否存在，如果不存在则创建
        if not os.path.exists('data'):
            os.mkdir('data')
        self.loadmap = {}
        self.loadzeromap = {}
        self.gdb_process = None
        pass

    # 定义一个析构函数
    def __del__(self):
        if self.gdb_process is not None:
            # 关闭gdb进程
            print("close gdb process")
            self.gdb_process.terminate()
    
    # #1 解析core文件中所有的LOAD信息集合，并返回
    def get_load_info(self):
        # 使用aarch64-linux-gnu-hi3519dv500-v2-readelf命令获取所有LOAD信息
        command = f'{self.config.get_cross()}readelf -l {self.config.get_core_path()} > data/log-readelf-l'
        # 执行linux命令
        res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(res)
        # res = run_command(command)
        if res.returncode != 0:
            print(f"Error: {res.stderr}")
            return None
        #     '''
        #     LOAD格式如下，一个LOAD信息占两行：
        #     NOTE           0x0000000000009688 0x0000000000000000 0x0000000000000000
        #                 0x00000000000249ac 0x0000000000000000         0x0
        # LOAD           0x000000000002f000 0x0000000000400000 0x0000000000000000
        #                 0x0000000000001000 0x0000000003d53000  R E    0x1000
        # LOAD           0x0000000000030000 0x0000000004163000 0x0000000000000000
        #                 0x0000000000075000 0x0000000000075000  R      0x1000
        #     '''
        loadlines = []
        # 读文件data/log-readelf-l
        with open('data/log-readelf-l', 'r') as f:
            lines = f.readlines()
            # 遍历每一行
            # flag = False
            loadline = ''
            for line in lines:
                # 如果包含LOAD，则解析
                if 'LOAD' in line:
                    loadline = line
                elif loadline != '':
                    loadline += line
                    loadlines.append(loadline)
                    loadline = ''
        print(f"loadlines: {len(loadlines)}")
        for line in loadlines:
            #按照空格进行分割
            # print(line)
            lines = line.split()
            # print(f"line: {len(lines)}")
            # print(lines)
            if len(lines) == 7:
                self.loadzeromap[lines[2]] = line
            elif len(lines) > 7:
                if len(lines) == 9:
                    #将lines[6]和lines[7]合并
                    lines[6] += lines[7]
                    lines.pop(7)
                
                # 将lines[2]和lines[5]按照16进制转为10进制
                # lines[2] = int(lines[2], 16)
                # lines[5] = int(lines[5], 16)
                # 计算虚拟地址结束地址edn = lines[2] + lines[5]，并追加到lines后面
                endaddr = hex(int(lines[2], 16) + int(lines[5], 16))
                # endaddr = lines[2] + lines[5]

                lines.append(endaddr)
                
                self.loadmap[lines[2]] = lines

            else:
                print(f"Error: {line}")

            # print(lines)
            # break
                
        print(f"loadmap: {len(self.loadmap)}")
        print(f"loadzeromap: {len(self.loadzeromap)}")

   
    # 检测虚拟地址addr是否在虚拟地址范围内，并且返回虚拟地址所在的虚拟地址范围
    def check_virtual_address(self, addr):
        # 遍历loadmap，如果addr在loadmap中，则返回loadmap中的值
        for key,lines in self.loadmap.items():
            addrint = int(addr, 16)
            if addrint >= int(lines[2], 16) and addrint <= int(lines[8], 16):
                return key,lines
        # 如果addr不在loadmap中，则返回None
        return None,None

    # 定义一个方法，查找core文件包含当前虚拟地址的虚拟地址
    def find_virtual_address(self, addr):
        if self.loadmap == {}:
            self.get_load_info()
        if self.gdb_process is None:
            self.gdb_process = start_gdb_core(f"{self.config.get_cross()}gdb", self.config.get_sonia_path(), self.config.get_core_path(),False)
            if self.gdb_process is None:
                print("gdb start failed")
                return False
            print("gdb start success")
            #加载lib
            if self.config.get_lib_path() != '':
                res = run_command(self.gdb_process, f'set solib-search-path {self.config.get_lib_path()}')
                # print(res)
        
        #遍历每一个loadmap，通过gdb的find命令查找包含addr的虚拟地址，lines[2]为虚拟地址起始地址，lines[8]为虚拟地址结束地址
        for key,lines in self.loadmap.items():
            # print(f"key: {key}")
            cmdline = f'find {lines[2]},{lines[8]},{addr}'
            res = run_command(self.gdb_process, cmdline, False)
            # print(res)
            # print(f"res: {res}")
            if "Pattern not found" in res:
                continue
            else:
                print(cmdline)
                print(f"{res}")
                # print(lines)
                '''
                0x7f70076798
                0x7f700767a0
                0x7f7008ae20
                3 patterns found.
                '''
                # 解析输出结果，判断每一个输出结果所在的虚拟地址范围
                values = res.split('\n')
                values.pop()
                values.pop()
                for value in values:
                    print(f"addr: {value}")
                    value_key,values_lines = self.check_virtual_address(value)
                    print(f"values_lines:{values_lines}") 

    # 定义一个方法，查找core文件包含当前虚拟地址的虚拟地址
    def find_virtual_address_end(self, addr):
        if self.loadmap == {}:
            self.get_load_info()
        if self.gdb_process is None:
            self.gdb_process = start_gdb_core(f"{self.config.get_cross()}gdb", self.config.get_sonia_path(), self.config.get_core_path(),False)
            if self.gdb_process is None:
                print("gdb start failed")
                return False
            print("gdb start success")
            #加载lib
            if self.config.get_lib_path() != '':
                res = run_command(self.gdb_process, f'set solib-search-path {self.config.get_lib_path()}')
                # print(res)
        
        #遍历每一个loadmap，通过gdb的find命令查找包含addr的虚拟地址，lines[2]为虚拟地址起始地址，lines[8]为虚拟地址结束地址
        for key,lines in self.loadmap.items():
            # print(f"key: {key}")
            cmdline = f'find {lines[2]},{lines[8]},{addr}'
            res = run_command(self.gdb_process, cmdline, False)
            # print(res)
            # print(f"res: {res}")
            if "Pattern not found" in res:
                continue
            else:
                print(cmdline)
                print(f"{res}")
                # print(lines)
                '''
                0x7f70076798
                0x7f700767a0
                0x7f7008ae20
                3 patterns found.
                '''
                # 解析输出结果，判断每一个输出结果所在的虚拟地址范围
                values = res.split('\n')
                values.pop()
                values.pop()
                for value in values:
                    print(f"addr: {value}")
                    value_key,values_lines = self.check_virtual_address(value)
                    print(f"values_lines:{values_lines}") 

class Config:
    """配置类，用于存储配置信息"""
    def __init__(self):
        self.type = '0'
        self.cross = ''
        self.sonia_path = ''
        self.core_path = ''
        self.lib_path = ''
        self.stack_size = 8388608
    def __str__(self):
        return f"type: {self.type}\n" \
        f"cross: {self.cross}\n" \
        f"sonia_path: {self.sonia_path}\n" \
        f"core_path: {self.core_path}\n" \
        f"lib_path: {self.lib_path}"
    
    def set_type(self, type):
        self.type = type
    
    def get_cross(self):
        return self.cross
    
    def set_sonia_path(self, sonia_path):
        self.sonia_path = sonia_path

    def set_core_path(self, core_path):
        self.core_path = core_path
    
    def set_cross(self, cross):
        self.cross = cross
    
    def get_type(self):
        return self.type

    def get_cross(self):
        if self.cross == 'local':
            return ""
        else:
           return self.cross
    
    def get_sonia_path(self):
        return self.sonia_path
    
    def get_core_path(self):
        return self.core_path
    
    def set_lib_path(self, lib_path):
        self.lib_path = lib_path

    def get_lib_path(self):
        return self.lib_path
    
    def set_param3(self, cross, sonia_path, core_path):
        self.cross = cross
        self.sonia_path = sonia_path
        self.core_path = core_path

    def set_param2(self, cross, sonia_path):
        self.cross = cross
        self.sonia_path = sonia_path

    def set_stack_size(self, stack_size):
        self.stack_size = stack_size

    def get_stack_size(self):
        return self.stack_size
    
    def valid(self):
        if self.type == '0':
            if self.cross == '' or self.sonia_path == '' or self.core_path == '':
                return False
        elif self.type == '1':
            if self.cross == '' or self.sonia_path == '':
                return False
        else:
            return False
        return True
    
class SimplePrompt:
    def __init__(self, completions=None):
        self.history = []
        self.completions = completions or []  # 可选的补全列表
        
        # 设置readline以启用Tab补全
        self._setup_readline()
    
    def _setup_readline(self):
        """配置readline以支持Tab补全和历史记录"""
        # 设置历史文件
        histfile = os.path.join(os.path.expanduser("~"), ".simple_prompt_history")
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            pass
        
        # 注册历史保存
        atexit.register(readline.write_history_file, histfile)
        
        # 设置Tab补全
        readline.set_completer(self._completer)
        readline.parse_and_bind("tab: complete")
        
        # 设置补全分隔符 - 允许文件名补全
        readline.set_completer_delims(" \t\n\"\\'")
    
    def _completer(self, text, state):
        """Tab补全函数"""
        # 如果没有提供补全列表，尝试使用文件名补全
        if not self.completions:
            # 使用默认的文件名补全
            return readline.get_completer_delims()(text, state)
        
        # 过滤匹配的补全项
        options = [c for c in self.completions if c.startswith(text)]
        
        # 返回当前状态的匹配项
        if state < len(options):
            return options[state]
        return None
    
    def prompt(self, message):
        """获取用户输入，支持Tab补全和历史记录"""
        try:
            text = input(message)
            self.history.append(text)
            return text
        except EOFError:
            print("\n退出")
            sys.exit(0)
if __name__ == "__main__":
    # 创建带Tab补全的提示器
    # 这里可以添加自定义的补全选项
    sp = SimplePrompt(completions=[
        'help', 'exit', 'quit', 'config', 'type', 'setcross', 'setsonia', 'setcore', 'setparam', 'setlib',  'find', 'findend',
    ])

    # 命令解释
    # 支持的命令: help, exit, quit, find
    helptext = 'exit - 退出程序\n' \
    'quit - 退出程序\n' \
    'config - 显示设置的参数信息\n' \
    'type 0|1 - 0 解析core文件（默认） 1 解析可执行文件\n' \
    'setcross path - 设置交叉编译工具链名字\n' \
    'setsonia path - 设置sonia路径\n' \
    'setcore path - 设置core文件路径\n' \
    'setparam cross,sonia,core - 设置交叉编译链名字，sonia路径，core文件路径\n' \
    'setlib path - 设置lib路径\n' \
    'find [startaddr,endaddr,]addr - 查找包含当前符号的虚拟地址\n' \
    'findend startaddr,endaddr,addr - 查找包含当前符号的虚拟地址，直到找到全局变量或者堆栈地址\n' \
    
    print("增强版交互提示器 - 支持Tab补全和历史记录(上下箭头)")
    print("输入 'exit' 退出程序")

    config = Config()
    coreFile = None
    
    while True:
        text = sp.prompt(">>> ")
        # print(f"输入: {text}")
        if text.lower() in ['exit', 'quit', "q"]:
            print("再见!")
            break
        params = text.split()
        if len(params) == 0:
            continue
        cmd = params[0]
        if cmd.lower() == 'help':
            print(helptext)
        elif cmd.lower() == 'config':
            print(config)
        elif cmd.lower() == 'type':
            if len(params) != 2 or params[1] not in ['0', '1']:
                print("参数错误")
                print("type 0|1 - 0 解析core文件（默认） 1 解析可执行文件")
            else:
                config.set_type(params[1])
        elif cmd.lower() == 'setcross':
            if len(params) != 2:
                print("参数错误")
                print("setcross path - 设置交叉编译工具链名字")
            else:
                config.set_cross(params[1])
        elif cmd.lower() == 'setsonia':
            if len(params) != 2:
                print("参数错误")
                print("setsonia path - 设置sonia路径")
            else:
                config.set_sonia_path(params[1])
        elif cmd.lower() == 'setcore':
            if len(params) != 2:
                print("参数错误")
                print("setcore path - 设置core文件路径")
            else:
                config.set_core_path(params[1])
        elif cmd.lower() == 'setparam':
            if config.get_type() == '0':
                if len(params) != 4:
                    print("参数错误：需要3个参数")
                    print("setparam cross,sonia[,core] - 设置交叉编译链名字，sonia路径，core文件路径(type=0)")
                else:
                    config.set_param3(params[1], params[2], params[3])
                    coreFile = None
            elif config.get_type() == '1':
                if len(params) < 3:
                    print("参数错误：需要2个参数")
                    print("setparam cross,sonia[,core] - 设置交叉编译链名字，sonia路径，core文件路径(type=0)")
                else:
                    config.set_param2(params[1], params[2])
        elif cmd.lower() == 'setlib':
            if len(params) != 2:
                print("参数错误")
                print("setlib path - 设置lib路径")
            else:
                config.set_lib_path(params[1])
                coreFile = None
        elif cmd.lower() == 'find':
            if len(params) != 2:
                print("参数错误")
                print("find [startaddr,endaddr,]addr - 查找包含当前符号的虚拟地址")
            else:
                if not config.valid():
                    print("配置错误，请检查配置：交叉编译链、sonia路径、core文件路径")
                    print( f"cross: {config.get_cross()}\nsonia_path: {config.get_sonia_path()}\ncore_path: {config.get_core_path()}\n" )
                else:
                    if coreFile is None:
                       coreFile = CoreFile(config)
                    coreFile.find_virtual_address(params[1])

        elif cmd.lower() == 'findend':
            if len(params) != 2:
                print("参数错误")
                print("findend startaddr,endaddr,addr - 查找包含当前符号的虚拟地址，直到找到全局变量或者堆栈地址")
            else:
                if not config.valid():
                    print("配置错误，请检查配置：交叉编译链、sonia路径、core文件路径")
                    print( f"cross: {config.get_cross()}\nsonia_path: {config.get_sonia_path()}\ncore_path: {config.get_core_path()}\n" )
                else:
                    if coreFile is None:
                        coreFile = CoreFile(config)
                    coreFile.find_virtual_address_end(params[1])