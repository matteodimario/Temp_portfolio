
#include <getopt.h>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <limits>
#include <cmath>
#include <iomanip>
#include "animal_class.h"
using namespace std;

class ZooMst {
    public:
    ZooMst() {}

    // read in information
    void read_in() {
        cin >> num_edges;
        int row;
        int col;
        uint32_t num_id = 0;
        cin >> row >> col;
        while (cin) {
            Animal animal(row, col, num_id);
            if ((row < 0 && col < 0)) {
                animal.cage_type = 'w';
            }
            else if ((row == 0 && col <= 0) || (col == 0 && row <= 0)) {
                animal.cage_type = 'b';
            }
            else {
                animal.cage_type = 's';
            }
            animals.push_back(animal);
            ++num_id;
            cin >> row >> col;
        }
    }

    // mst
    void mst() {
        size_t count = 0;
        animals[0].cur_best_dist = 0;
        size_t cur_index = 0;
        while (count != animals.size()) {

            for (size_t i = 0; i < animals.size(); ++i) {
                if (animals[i].visited == false) {
                    if (animals[cur_index].visited == true) {
                        cur_index = i;
                    }
                    if (static_cast<double>(animals[cur_index].cur_best_dist) == std::numeric_limits<double>::infinity()) {
                        cur_index = i;
                    }
                    if (animals[cur_index].cur_best_dist > animals[i].cur_best_dist) {
                        cur_index = i;
                    }
                }
            }
            animals[cur_index].visited = true;
            for (size_t i = 0; i < animals.size(); ++i) {
                if (animals[i].visited == false) {
                    if (animals[i].cage_type == animals[cur_index].cage_type || 
                    animals[i].cage_type == 'b' || animals[cur_index].cage_type == 'b') {
                    double distance = calculate_distance(animals[i], animals[cur_index]);
                        if (distance < animals[i].cur_best_dist) {
                            if (animals[i].cur_best_dist != std::numeric_limits<double>::infinity()) {
                                running_weight = running_weight - (animals[i].cur_best_dist - distance);
                            }
                            else {
                                running_weight = running_weight + distance;
                            }
                            animals[i].cur_best_dist = distance;
                            animals[i].parent = &animals[cur_index];
                        }
                    }
                }
                
            }

            if (count == 1) {
                animals[0].parent = &animals[cur_index];
            }
            ++count;
            cur_index = count;
                    
        }

        // print mst result
        cout << std::fixed << std::setprecision(2) << running_weight << "\n";
        for (size_t i = 1; i < animals.size(); ++i) {
            if (animals[i].num_id < animals[i].parent->num_id) {
                cout << animals[i].num_id << " " << animals[i].parent->num_id << "\n";
            }
            else {
                cout << animals[i].parent->num_id << " " << animals[i].num_id << "\n";
            }
        }
    }


    private:
    uint32_t num_edges = 0;
    vector<Animal> animals;
    double running_weight = 0;
};