#include "String.h"
#include <iostream>

int main() {
    String s1("Hello");
    String s2 = s1;
    s1 += " World";
    std::cout << s1.c_str() << std::endl;
    std::cout << "Size: " << s1.size() << std::endl;
    std::cout << "Find 'World': " << s1.find(String("World")) << std::endl;
    std::cout << "Substring: " << s1.substr(6, 5).c_str() << std::endl;
    return 0;
}
