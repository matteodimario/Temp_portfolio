#ifndef LIST_H
#define LIST_H
/* List.h
 *
 * doubly-linked, double-ended list with Iterator interface
 */

#include <iostream>
#include <cassert> //assert
#include <cstddef> //NULL


template <typename T>
class List {
  //OVERVIEW: a doubly-linked, double-ended list with Iterator interface
public:

  //constructor, initializes an empty list
  List() : first(nullptr), last(nullptr), list_size(0) { }

  //copy-constructor
  List(const List<T> &other) : first(nullptr), last(nullptr),  list_size(0)
  { copy_all(other); }

  //assignment operator 
  List & operator=(const List rhs) {
    if (this == &rhs) { return *this; }
    clear();
    copy_all(rhs);
    return *this;
  }

  //destructor, deletes all nodes until empty
  ~List() {
    clear();
  }

  //EFFECTS:  returns true if the list is empty
  bool empty() const {
    return !first; 
  }

  //EFFECTS: returns the number of elements in this List
  //HINT:    Traversing a list is really slow.  Instead, keep track of the size
  //         with a private member variable.  That's how std::list does it.
  int size() const {
    return list_size;
  }

  //REQUIRES: list is not empty
  //EFFECTS: Returns the first element in the list by reference
  T & front() {
    return first->datum;
  }

  //REQUIRES: list is not empty
  //EFFECTS: Returns the last element in the list by reference
  T & back() {
    return last->datum;
  }

  //EFFECTS:  inserts datum into the front of the list
  void push_front(const T &datum) {
    ++list_size;
    Node *node = new Node;
    if (list_size != 1) { // i.e. not first element inserted
      first->prev = node; // set original first's prev to this one
    }
    node->datum = datum;
    node->next = first;
    node->prev = nullptr;
    first = node;
    if (list_size == 1) {
      last = node;
    }
  }

  //EFFECTS:  inserts datum into the back of the list
  void push_back(const T &datum) {
    ++list_size;
    Node *node = new Node; 
    if (list_size != 1) { //i.e. not first element inserted
      last->next = node; // set original last's next to this one
    }
    node->datum = datum;
    node->next = nullptr;
    node->prev = last;
    last = node;
    if (list_size == 1) {
      first = node;
    }
  }

  //REQUIRES: list is not empty
  //MODIFIES: may invalidate list iterators
  //EFFECTS:  removes the item at the front of the list
  void pop_front() {
    --list_size;
    Node *temp = first;
    if (list_size != 0) {
      first = first->next;
    }
    else {
      first = last = nullptr;
    }
    delete temp;
  }

  //REQUIRES: list is not empty
  //MODIFIES: may invalidate list iterators
  //EFFECTS:  removes the item at the back of the list
  void pop_back() {
    --list_size;
    Node *temp = last;
    if (list_size != 0) {
      last = last->prev;
    }
    else {
      first = last = nullptr;
    }
    delete temp;
  }

  //MODIFIES: may invalidate list iterators
  //EFFECTS:  removes all items from the list
  void clear() {
    while (!empty()) {
      pop_front();
    }
  }

  // You should add in a default constructor, destructor, copy constructor,
  // and overloaded assignment operator, if appropriate. If these operations
  // will work correctly without defining these, you can omit them. A user
  // of the class must be able to create, copy, assign, and destroy Lists

private:
  //a private type
  struct Node {
    Node *next;
    Node *prev;
    T datum;
  };

  //REQUIRES: list is empty
  //EFFECTS:  copies all nodes from other to this
  void copy_all(const List<T> &other) {
    for (Node *node = other.first; node; node = node->next) {
      push_back(node->datum);
    }
  }

  Node *first;   // points to first Node in list, or nullptr if list is empty
  Node *last;    // points to last Node in list, or nullptr if list is empty
  int list_size; // holds size of list (new), init to 0

public:
  ////////////////////////////////////////
  class Iterator {
    
    //OVERVIEW: Iterator interface to List

    // You should add in a default constructor, destructor, copy constructor,
    // and overloaded assignment operator, if appropriate. If these operations
    // will work correctly without defining these, you can omit them. A user
    // of the class must be able to create, copy, assign, and destroy Iterators.

    // Your iterator should implement the following public operators: *,
    // ++ (prefix), default constructor, == and !=.

  public:
    //default constructor
    Iterator() : node_ptr(nullptr) { }
    // This operator will be used to test your code. Do not modify it.
    // Requires that the current element is dereferenceable.
    Iterator& operator--() {
      assert(node_ptr);
      node_ptr = node_ptr->prev;
      return *this;
    }

    T& operator*() const {
      assert(node_ptr);
      return node_ptr->datum;
    }

    Iterator& operator++() {
      assert(node_ptr);
      node_ptr = node_ptr->next;
      return *this;
    }

    bool operator==(Iterator rhs) const{
      return node_ptr == rhs.node_ptr;
    }

    bool operator!=(Iterator rhs) const{
      return node_ptr != rhs.node_ptr;
    }

  private:
    Node *node_ptr; //current Iterator position is a List node
    // add any additional necessary member variables here

    // add any friend declarations here
    friend class List;
    // construct an Iterator at a specific position
    Iterator(Node *p) : node_ptr(p) { }

  };//List::Iterator
  ////////////////////////////////////////

  // return an Iterator pointing to the first element
  Iterator begin() const {
    return Iterator(first);
  }

  // return an Iterator pointing to "past the end"
  Iterator end() const {
    return Iterator(nullptr);
  }

  //REQUIRES: i is a valid, dereferenceable iterator associated with this list
  //MODIFIES: may invalidate other list iterators
  //EFFECTS: Removes a single element from the list container
  void erase(Iterator i) {
    Node *node = i.node_ptr;
    //case 1: next and previous are not nullptrs
    if (node->next && node->prev) {
      Node *next = node->next;
      Node *prev = node->prev;
      next->prev = prev;
      prev->next = next;
      delete node;
      --list_size;
    }
    
    //case 2: next is not nullptr, prev is (first element)
    else if (node->next && !(node->prev)) {
      pop_front();
    }
    //case 3: next is nullptr, prev is not (last element)
    else if (!(node->next) && node->prev) {
      pop_back();
    }
    //case 4: both next and prev are nullptrs (only element)
    else if (!(node->next) && !(node->prev)) {
      clear();
    }
  }

  //REQUIRES: i is a valid iterator associated with this list
  //EFFECTS: inserts datum before the element at the specified position.
  void insert(Iterator i, const T &datum) {
    Node *node = i.node_ptr;
    //case 1: node is nullptr, (one past the end, or empty list)
    if (!node) {
      push_back(datum);
    }
    //case 2: prev is not nullptr (not first element, not one past end)
    else if (node->prev) {
      Node *n = new Node;
      n->datum = datum;
      Node *prev = node->prev;
      n->prev = prev;
      n->next = prev->next;
      prev->next = n;
      ++list_size;
    }
    //case 3: prev is nullptr (first element)
    else if (!node->prev) {
      push_front(datum);
    }
    
  }

};//List


////////////////////////////////////////////////////////////////////////////////
// Add your member function implementations below or in the class above
// (your choice). Do not change the public interface of List, although you
// may add the Big Three if needed.  Do add the public member functions for
// Iterator.


#endif // Do not remove this. Write all your code above this line.
