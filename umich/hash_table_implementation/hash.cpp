#include "hashtable.h"
#include <string>
#include <iostream>
int main() {
// VERY BASIC EXAMPLE (will likely not compile with default/empty hashtable.h
// file)
HashTable<std::string, int> midterm;
std::cout << midterm.insert("sam", 50) << " ";
std::cout << midterm.insert("fee", 100) << " ";
std::cout << midterm.insert("milo", 95) << " ";
std::cout << midterm.insert("gabe", 88) << " \n";
std::cout << midterm["sam"] << " ";
std::cout << midterm["fee"] << " ";
std::cout << midterm["milo"] << " ";
std::cout << midterm["gabe"] << " \n";
std::cout << midterm.erase("sam") << " ";
std::cout << midterm["sam"] << "\n";
// ADD MORE TESTS OF YOUR OWN

HashTable<std::string, int> hash;
std::cout << hash.insert("C", 6);
std::cout << hash.insert("D", 6);
std::cout << hash.insert("E", 5);
std::cout << hash.insert("F", 4);
std::cout << hash.insert("G", 3);
std::cout << hash.insert("H", 6);
std::cout << hash.insert("I", 8);
std::cout << hash.insert("A", 2);
return 0;
}
