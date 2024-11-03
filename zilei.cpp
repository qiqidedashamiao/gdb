#include <iostream>
#include <string>
#include <thread>
#include <vector>
#include <mutex>
#include <chrono>
#include <csignal>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <pthread.h>
using namespace std;


#define gettid() syscall(SYS_gettid)
class Base {
public:
    Base() : value(1) {}
    virtual ~Base() {}
    virtual void print() const {
        cout << "Base" << endl;
    }
private:
    int value;
};

class Derived : public Base {
public:
    Derived() : value(0) {}
    void print() const {
        cout << "Derived" << endl;
    }
private:
    int value;
};

void func(Base* b) {
    //Derived* d = dynamic_cast<Derived*>(b);
    b->print();
}

mutex mtx1, mtx2;
// pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
// pthread_mutex_t mutex2 = PTHREAD_MUTEX_INITIALIZER;
void thread_func(int id)
{
    if (id % 2 == 0) {
            // 获取线程 ID 通过NYSystemThreadID()函数
            printf("[%d] try to lock mtx1\n", gettid());
            lock_guard<mutex> lock1(mtx1);
            // pthread_mutex_lock(&mutex1);
            this_thread::sleep_for(chrono::milliseconds(100)); // 模拟一些工作
            printf("[%d] get mtx1. try to lock mtx2\n", gettid());
            lock_guard<mutex> lock2(mtx2);
            // pthread_mutex_lock(&mutex2);
            printf("[%d] get both locks\n", gettid());
            // pthread_mutex_unlock(&mutex2);
            // pthread_mutex_unlock(&mutex1);
        } else {
            printf("[%d] try to lock mtx2\n", gettid());
            lock_guard<mutex> lock2(mtx2);
            // pthread_mutex_lock(&mutex2);
            this_thread::sleep_for(chrono::milliseconds(100)); // 模拟一些工作
            printf("[%d] get mtx2. try to lock mtx1\n", gettid());
            lock_guard<mutex> lock1(mtx1);
            // pthread_mutex_lock(&mutex1);
            printf("[%d] get both locks\n", gettid());
            // pthread_mutex_unlock(&mutex1);
            // pthread_mutex_unlock(&mutex2);
        }

}

//生成多个线程，模拟多线程死锁的环境
void test_sisuo() {
    
    // auto thread_func = [&](int id) {
    //     if (id % 2 == 0) {
    //         printf("[%d] try to lock mtx1\n", id);
    //         lock_guard<mutex> lock1(mtx1);
    //         this_thread::sleep_for(chrono::milliseconds(100)); // 模拟一些工作
    //         printf("[%d] get mtx1. try to lock mtx2\n", id);
    //         lock_guard<mutex> lock2(mtx2);
    //         printf("[%d] get both locks\n", id);
    //     } else {
    //         printf("[%d] try to lock mtx2\n", id);
    //         lock_guard<mutex> lock2(mtx2);
    //         this_thread::sleep_for(chrono::milliseconds(100)); // 模拟一些工作
    //         printf("[%d] get mtx2. try to lock mtx1\n", id);
    //         lock_guard<mutex> lock1(mtx1);
    //         printf("[%d] get both locks\n", id);
    //     }
    // };

    vector<thread> threads;
    for (int i = 0; i < 3; i++) {
        threads.push_back(thread(thread_func, i));
    }

    // 等待一段时间以检测死锁
    this_thread::sleep_for(chrono::seconds(5));

    // 如果检测到死锁，触发崩溃信号
    cout << "Deadlock detected, generating core dump..." << endl;
    raise(SIGABRT);

    for (auto& t : threads) {
        t.join();
    }
}

int main() {
    Base* b = new Derived();
    func(b);
    delete b;
    // cout << "test_sisuo start" << endl;
    // test_sisuo();
    // cout << "test_sisuo end" << endl;


    return 0;
}