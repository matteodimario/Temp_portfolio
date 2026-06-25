# Makefile
# Build rules for Naive Bayes classifier

CXX ?= g++
CXXFLAGS ?= --std=c++11 -Wall -Werror -pedantic -g -Wno-sign-compare -Wno-comment

main.exe: main.cpp BinarySearchTree.h Map.h csvstream.h
	$(CXX) $(CXXFLAGS) main.cpp -o main.exe

.PHONY: clean
clean:
	rm -vrf *.o *.exe *.gch *.dSYM *.stackdump *.out.txt
