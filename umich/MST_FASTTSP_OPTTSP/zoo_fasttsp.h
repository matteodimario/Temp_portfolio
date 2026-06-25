
#include <getopt.h>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <limits>
#include <cmath>
#include <iomanip>
#include "zoo_mst.h"
using namespace std;

class ZooFasttsp {
    public:
    ZooFasttsp() {}

    // read in information
    void read_in() {
        cin >> num_edges;
        int row;
        int col;
        uint32_t id = 0;
        // char cage_type;
        cin >> row >> col;
        while (cin) {
            Animal animal(row, col, id);
            // set cage_type
            if ((row < 0 && col < 0)) {
                animal.cage_type = 'w';
            }
            else if ((row == 0 && col < 0) || (col == 0 && row < 0)) {
                animal.cage_type = 'b';
            }
            else {
                animal.cage_type = 's';
            }
            animals.push_back(animal);
            ++id;
            cin >> row >> col;
        }
    }

    void fasttsp() {
        animals[0].parent = &animals[2];
        animals[0].cur_best_dist = calculate_distance(animals[0], animals[1]);
        animals[1].parent = &animals[0];
        animals[1].cur_best_dist = calculate_distance(animals[1], animals[2]);
        animals[2].parent = &animals[1];
        animals[2].cur_best_dist = calculate_distance(animals[0], animals[2]);
        size_t index = 3;
        double cur_min_dist = std::numeric_limits<double>::infinity();
        double tent_dist = std::numeric_limits<double>::infinity();
        size_t j_to_insert = 0;
        for (size_t i = 3; i < animals.size(); ++i) {
            cur_min_dist = std::numeric_limits<double>::infinity();
            j_to_insert = 0;
            for (size_t j = 0; j < index; ++j) {
                    tent_dist = calculate_distance(animals[j], animals[index]) + calculate_distance(animals[index], *animals[j].parent) - animals[j].parent->cur_best_dist;
                    if (tent_dist < cur_min_dist) {
                        j_to_insert = j;
                        cur_min_dist = tent_dist;
                    }
            }
            animals[index].parent = animals[j_to_insert].parent;
            animals[j_to_insert].parent = &animals[index];
            animals[animals[index].parent->num_id].cur_best_dist = calculate_distance(animals[index], *animals[index].parent);
            animals[index].cur_best_dist = calculate_distance(animals[index], animals[j_to_insert]);
            tent_dist = std::numeric_limits<double>::infinity();
            ++index;
        }

        // print fasttsp information
        int cur_index = 0;
        double total_weight = 0;
        for (size_t i = 0; i < animals.size(); ++i) {
            total_weight += animals[i].cur_best_dist;
        }
        cout << std::fixed << std::setprecision(2) << total_weight << "\n";
        for (size_t i = 0; i < animals.size(); ++i) {
            cout << animals[cur_index].num_id << " ";
            cur_index = animals[cur_index].parent->num_id;
        }
    }   

    private:
    uint32_t num_edges = 0;
    vector<Animal> animals;
};