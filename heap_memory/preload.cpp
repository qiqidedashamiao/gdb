
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/syscall.h>
#include <dlfcn.h>
#include <unistd.h>
#include <malloc.h>
#include <new>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <cerrno>

//如果定义宏USE_BACKTRACK，则包含头文件<execinfo.h>
#ifdef USE_BACKTRACE
#include <execinfo.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif
void __libc_free(void*);
void * __libc_malloc(size_t);
void *__libc_calloc(size_t, size_t);
void *__libc_realloc(void*, size_t);

void MemTraceInit();

#ifdef __cplusplus
}
#endif


#define gettid() syscall(SYS_gettid)

void MemTraceInit();

void SaveTraceInfo(int optype, void * buf, int len);

void * operator new(size_t size);
void * operator new (size_t size, const std::nothrow_t&);

//是否重载取决于C++库的实现
void * operator new[](size_t size);
//__externally_visible__ 属性告诉编译器，即使这个函数在本翻译单元中未被引用，它也不应该被删除或优化掉，因为它可能会被外部链接使用（例如通过动态链接或插件机制）
void operator delete(void *ptr) _GLIBCXX_USE_NOEXCEPT
  __attribute__((__externally_visible__));

//是否重载取决于C++库的实现
void operator delete[](void *ptr) _GLIBCXX_USE_NOEXCEPT
  __attribute__((__externally_visible__));


// backtrace_symbols()
// backtrace_symbols_fd()


static int s_init = 0;


// 清理函数（如果需要）
__attribute__((destructor)) void cleanup() {
    // ... 在dlclose时执行的清理代码（如果有）
}



/**
 * purpose: 进程启动前初始化内存跟踪信息
 * param:
 * return:
*/
__attribute__ ((constructor))
void _main(int argc, char** argv)
{
	fprintf(stdout,"[pid:%d][tid:%ld]zl: malloctest init argc:%d\n",getpid(), gettid(), argc);
	char path[1024];
	memset(path, 0 ,sizeof(path));
	if (readlink("/proc/self/exe", path, sizeof(path) - 1) > 0)
	{
		char *pName = strrchr(path, '/');
		if (pName != NULL)
		{
			fprintf(stdout,"[pid:%d][tid:%ld]zl:pname:%s\n",getpid(), gettid(), pName);
			int len = strlen(pName);
			for( int i = 0; i < len-4; ++i)
			{
				if (pName[i] == 's')
				{
					if (pName[i+1] == 'o'
					&& pName[i+2] == 'n'
					&& pName[i+3] == 'i'
					&& pName[i+4] == 'a')
					{
						// MemTraceInit();
						// updateParam();
						s_init = 1;
						fprintf(stdout,"[pid:%d][tid:%ld]zl: s_init:%d\n",getpid(), gettid(),s_init);
						// createThread(getpid());
						break;
					}
				}
			}
		}
	}
}

void my_stat_malloc(size_t size, void *ptr)
{

}

void my_stat_free(size_t size, void *ptr)
{

}

extern "C" void * malloc(size_t size)
{
    if (size == 0)
    {
        return NULL;
    }
    void* result = NULL;

	result = (void*)__libc_malloc(size);
    if (s_init == 1)
    {
        my_stat_malloc(size, result);
    }
	return result;
}

// 假设元数据在分配的内存块之前，并且包含一个 size_t 类型的大小字段
// 最后3位用于其他目的
size_t get_allocated_size(void* ptr) {
    if (ptr == NULL) {
        return 0;
    }

    // 根据特定的内存分配器实现调整偏移量
    size_t* size_ptr = (size_t*)((uint8_t*)ptr - sizeof(size_t));
    // 屏蔽掉最后3位
    return *size_ptr & ~((size_t)0x7);
}

extern "C" void free(void *ptr)
{
	if (ptr == NULL)
	{
		return;
	}
    if (s_init == 1)
    {
        size_t size_ptr = get_allocated_size(ptr);
        my_stat_free(size_ptr, ptr);
    }
	__libc_free(ptr);
	return;
}


extern "C" void *calloc(size_t nmemb, size_t size)
{
	void* result = NULL;
	result = (void*)__libc_calloc(nmemb, size);
    if (s_init == 1)
    {
        my_stat_malloc(nmemb*size, result);
    }
	return result;
}

extern "C" void *realloc(void *ptr, size_t size)
{
	void* result = NULL;
    if (s_init == 1)
    {
        size_t size_ptr = get_allocated_size(ptr);
        my_stat_free(size_ptr, ptr);
    }
	result = (void*)__libc_realloc(ptr, size);
    if (s_init == 1)
    {
        my_stat_malloc(size, result);
    }
	return result;
}

// void * operator new(size_t size)
// {
// 	void * result = NULL;
// 	InsertTraceMallocBig(MEMOP_NEW_BIG, NULL, size);
// 	result = (void*)__libc_malloc(size);
// 	InsertTraceMalloc(MEMOP_NEW, result, size);
// 	return result;
// }
// void * operator new (size_t size, const std::nothrow_t&)
// {
// 	void * result = NULL;
// 	InsertTraceMallocBig(MEMOP_NEW_NOTHROW_BIG, NULL, size);
// 	result = (void*)__libc_malloc(size);
// 	InsertTraceMalloc(MEMOP_NEW_NOTHROW, result, size);
// 	return result;
// }

// void * operator new[](size_t size)
// {
// 	void * result = NULL;
// 	InsertTraceMallocBig(MEMOP_NEW_ARRAY_BIG, NULL, size);
// 	result = (void*)__libc_malloc(size);
// 	InsertTraceMalloc(MEMOP_NEW_ARRAY, result, size);
// 	return result;
// }

// void operator delete(void* ptr) _GLIBCXX_USE_NOEXCEPT 
// {
// 	if(ptr != NULL)
// 	{
// 		InsertTraceFree(MEMOP_DELETE, ptr);
// 		__libc_free(ptr);
// 	}
// 	return;
// }

// void operator delete[](void *ptr) _GLIBCXX_USE_NOEXCEPT
// {
// 	if(ptr != NULL)
// 	{
// 		InsertTraceFree(MEMOP_DELETE_ARRAY, ptr);
// 		__libc_free(ptr);
// 	}
// 	return;
// }


