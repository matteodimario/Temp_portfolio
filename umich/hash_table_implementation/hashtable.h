// A bucket's status tells you whether it's empty, occupied,
// or contains a deleted element.
// enum class Status : uint8_t {
// Empty,
// Occupied,
// Deleted
// };
// template<typename K, typename V, typename Hasher = std::hash<K>>
// class HashTable {
// // used by the autograder; do not change/remove.
//     friend class Verifier;
//     public:
//     // A bucket has a status, a key, and a value.
//     struct Bucket {
//         // Do not modify Bucket.
//         Status status = Status::Empty;
//         K key;
//         V val;
//     };
//     HashTable() {
//         num_elements = 0;
//         num_deleted = 0;
//         // Initialize the buckets vector with a size of 4.
//         buckets.resize(8);
//         // TODO: a default constructor (possibly empty).
//         // You can use the following to avoid implementing rehash_and_grow().
//         // However, you will only pass the AG test cases ending in _C.
//         // To pass the rest, start with at most 20 buckets and implement
//         // rehash_and_grow().
//         // buckets.resize(10000);
//     }
//     size_t size() const {
//         return num_elements;
//     }
//     // returns a reference to the value in the bucket with the key, if it
//     // already exists. Otherwise, insert it with a default value, and return
//     // a reference to the resulting bucket.
//     V& operator[](const K& key) {
//         static V val_default = V{}; // static local variable retains its value

//         Hasher hasher;
//         size_t bucket_index = hasher(key) % buckets.size();

//         // Check if the key already exists in the bucket
//         if (insert(key, val_default)) {
//             // return buckets[bucket_index].val; // Return a reference to the existing value
//             while (buckets[bucket_index].key != key) {
//                 bucket_index += 1;
//             }
//             return buckets[bucket_index].val;
//         }

//         // The key does not exist, so insert a new key-value pair with the default value
        

//         // Now that the key exists (since insert was called), return a reference to the value
//         return buckets[bucket_index].val;
//     }
//     // insert returns whether inserted successfully
//     // (if the key already exists in the table, do nothing and return false).
//     bool insert(const K& key, const V& val) {
//         if (buckets.size() / 2 < num_elements) {
//             rehash_and_grow();
//         }
       
//         Hasher hasher;
//         size_t bucket_searched = hasher(key) % buckets.size();
//         bool insert_status = false;
//         bool already_inserted = false;
//         bool first_free_element = true;
//         K first_key;
//         first_key = buckets[bucket_searched].key;
 
//         size_t desired_bucket = bucket_searched;
//         while (already_inserted == false && insert_status == false) {
//             K key_new = key;
            
//             if (buckets[bucket_searched].status == Status::Deleted && first_free_element) {
//                 first_free_element = false;
//                 desired_bucket = bucket_searched;
//                 bucket_searched += 1;
//                 if (bucket_searched == buckets.size()) {
//                     bucket_searched = 0;
//                 }
//                 if (buckets[bucket_searched].status == Status::Deleted && buckets[bucket_searched].key == first_key) {
//                     desired_bucket = bucket_searched;
//                     insert_status = true;
//                 }
//             }
//             else if (buckets[bucket_searched].status == Status::Occupied) {
//                 // if (buckets[bucket_searched].key == first_key) {
//                 //     return false;
//                 // }
//                 if (buckets[bucket_searched].key == key_new) {
//                     return false;
//                 }
//                 bucket_searched += 1;
//                 if (bucket_searched == buckets.size()) {
//                     bucket_searched = 0;
//                 }
//                 // something to signal that we have wrapped around all buckets
//             }
//             else if (buckets[bucket_searched].status == Status::Empty) {
//                 insert_status = true;
//                 if (first_free_element) {
//                     desired_bucket = bucket_searched;
//                 }
//             }
//             else {
//                 insert_status = false;
//                 already_inserted = true;
//             }

//         }
//         if (already_inserted == false) {
//             buckets[desired_bucket].val = val;
//             buckets[desired_bucket].key = key;
//             buckets[desired_bucket].status = Status::Occupied;
//             num_elements++;
//         }
//         return insert_status;
//     }
//     // erase returns the number of items remove (0 or 1)
//     size_t erase(const K& key) {
//         Hasher hasher;
//         size_t bucket_searched = hasher(key) % buckets.size();
//         num_deleted = 2;
//         // while 
//         while (num_deleted == 2) {
//             if (buckets[bucket_searched].status == Status::Empty || buckets[bucket_searched].status == Status::Deleted) {
//                 num_deleted = 0;
//             } 
//             else if (buckets[bucket_searched].key == key) {
//                 buckets[bucket_searched].status = Status::Deleted;
//                 num_deleted = 1;
//                 num_elements--;
//             }
//             else {
//                 bucket_searched += 1;
//                 if (bucket_searched == buckets.size()) {
//                     bucket_searched = 0;
//                 } 
//             }
//             // case if the hash table is full???
//         }
//         return num_deleted;
//     }
//     private:
//     size_t num_elements = 0;
//     size_t num_deleted = 0; // OPTIONAL: you don't need to use num_deleted to pass
//     std::vector<Bucket> buckets;
//     void rehash_and_grow() {
//         size_t new_bucket_size = buckets.size(); // Double the bucket size
//         std::vector<Bucket> buckets_new(new_bucket_size);
//         buckets_new = buckets;
//         buckets.resize(buckets.size() * 2);
//         static V val_default = V{};
//         static K key_default = K{};
//         for (size_t i = 0; i < buckets.size(); ++i) {
//             buckets[i].status = Status::Empty;
//             buckets[i].key = key_default;
//             buckets[i].val = val_default;
//         }
//         for (size_t i = 0; i < buckets_new.size(); ++i) {

//             if (buckets_new[i].status == Status::Occupied) {
//                 insert(buckets_new[i].key, buckets_new[i].val);
//                 // Calculate the new bucket index based on the updated size
//             }
//         }

//         // Update the hash table with the new buckets and size
// }

//     // You can add methods here if you like.
//     // TODO
// };
// #endif // HASHTABLE_H
 

#ifndef HASHTABLE_H
#define HASHTABLE_H


// INSTRUCTIONS:
// fill out the methods in the class below.

// You may assume that the key and value types can be copied and have default
// constructors.

// You can also assume that the key type has (==) and (!=) methods.

// You may assume that Hasher is a functor type with a
// size_t operator()(const Key&) overload.

// The key/value types aren't guaranteed to support any other operations.

// Do not add, remove, or change any of the class's member variables.
// The num_deleted counter is *optional*. You might find it helpful, but it
// is not required.

// Do not change the Bucket type.

// SUBMISSION INSTRUCTIONS:
// Submit this file, by itself, in a .tar.gz.
// Other files will be ignored.

#include <cstdint>
#include <functional> // where std::hash lives
#include <vector>
#include <cassert> // useful for debugging!

// A bucket's status tells you whether it's empty, occupied, 
// or contains a deleted element.
enum class Status : uint8_t {
    Empty,
    Occupied,
    Deleted
};

template<typename K, typename V, typename Hasher = std::hash<K>>
class HashTable {
    // used by the autograder; do not change/remove.
    friend class Verifier;
public:
    // A bucket has a status, a key, and a value.
    struct Bucket {
        // Do not modify Bucket.
        Status status = Status::Empty;
        K key;
        V val;
    };

    HashTable() {
        buckets.resize(20);

        // You can use the following to avoid implementing rehash_and_grow().
        // However, you will only pass the AG test cases ending in _C.
        // To pass the rest, start with at most 20 buckets and implement rehash_and_grow().
        //    buckets.resize(10000);
    }

    size_t size() const {
        return num_elements;
    }

    // returns a reference to the value in the bucket with the key, if it
    // already exists. Otherwise, insert it with a default value, and return
    // a reference to the resulting bucket.
    V& operator[](const K& key) {
        rehash_and_grow();
        Hasher h;
        size_t c = h(key) % buckets.size();
        bool dF = false;
        bool found = false;
        size_t dK;
        for(size_t i = 0; i < buckets.size(); i++)
        {
            switch(buckets[c].status)
            {

                case Status::Empty :
                {
                    if(dF)
                    {
                        c = dK;
                    }
                    found = true;
                    break;
                }
                case Status::Occupied :
                {
                    if(buckets[c].key == key){
                        return buckets[c].val;
                    }
                    break;
                }
                case Status::Deleted :
                {
                    if(!dF)
                    {
                        dK = c;
                        dF = true;
                    }
                    break;
                }
            }
            if(found)
            {
                break;
            }
            else
            {
                c = (c+1) % buckets.size();
            }
        }
        if(found)
        {
            buckets[c].status = Status::Occupied;
            buckets[c].key = key;
            buckets[c].val = V();
            num_elements++;
            return buckets[c].val;
        }
        else
        {
            buckets[dK].status = Status::Occupied;
            buckets[dK].key = key;
            buckets[dK].val = V();
            num_elements++;
            return buckets[dK].val;
        }
    }

    // insert returns whether inserted successfully
    // (if the key already exists in the table, do nothing and return false).
    bool insert(const K& key, const V& val) {
        rehash_and_grow();
        Hasher h;
        size_t c = h(key) % buckets.size();
        bool dF = false;
        bool found = false;
        size_t dK;
        for(size_t i = 0; i < buckets.size(); i++)
        {
            switch(buckets[c].status)
            {

                case Status::Empty :
                {
                    if(dF)
                    {
                        c = dK;
                    }
                    found = true;
                    break;
                }
                case Status::Occupied :
                {
                    if(buckets[c].key == key){
                        return false;
                    }
                    break;
                }
                case Status::Deleted :
                {
                    if(!dF)
                    {
                        dK = c;
                        dF = true;
                    }
                    break;
                }
            }
            if(found)
            {
                break;
            }
            else
            {
                c = (c+1) % buckets.size();
            }
        }
        if(found)
        {
            buckets[c].status = Status::Occupied;
            buckets[c].key = key;
            buckets[c].val = val;
        }
        else
        {
            buckets[dK].status = Status::Occupied;
            buckets[dK].key = key;
            buckets[dK].val = val;
        }
        num_elements++;
        return true;
    }
    // erase returns the number of items remove (0 or 1)
    size_t erase(const K& key) {
        Hasher h;
        size_t c = h(key) % buckets.size();
        bool dF = false;
        bool breakO = false;
        size_t n = 0;
        for(size_t i = 0; i < buckets.size(); i++)
        {
            switch(buckets[c].status)
            {

                case Status::Empty :
                {
                    breakO = true;
                    break;
                }
                case Status::Occupied :
                {
                    if(buckets[c].key == key){
                        dF = true;
                    }
                    break;
                }
                case Status::Deleted :
                {
                    break;
                }
            }
            if(dF)
            {
                buckets[c].status = Status::Deleted;
                num_elements--;
                n = 1;
                break;
            }
            else if(breakO)
            {
                break;
            }
            else
            {
                c = (c+1) % buckets.size();
            }
        }
        return n;
    }

private:
    size_t num_elements = 0;
    size_t num_deleted = 0; // OPTIONAL: you don't need to use num_deleted to pass
    std::vector<Bucket> buckets;

    void rehash_and_grow()
    {
        if(num_elements * 2 > buckets.size())
        {
            std::vector<Bucket> h = buckets;
            buckets.clear();
            buckets.resize(h.size() * 2);
            for(size_t i = 0; i < h.size(); i++)
            {
                if(h[i].status == Status::Occupied){
                    insert(h[i].key, h[i].val);
                    num_elements--;
                }
            }

        }
    }

    // You can add methods here if you like.
    // TODO
};

#endif // HASHTABLE_H
