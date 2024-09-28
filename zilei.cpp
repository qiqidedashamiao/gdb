#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
using namespace std;
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

int main() {
    Base* b = new Derived();
    func(b);
    delete b;
    return 0;
}