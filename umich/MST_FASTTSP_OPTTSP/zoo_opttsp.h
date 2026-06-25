
#include <getopt.h>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <limits>
#include <cmath>
#include "zoo_fasttsp.h"

class ZooOpttsp {
    public:
    uint32_t num_edges = 0;
    double tentative_sol = 0;
    double upper_bound = 0;
    double best_cur_sol = 0;
    vector<Animal> animals;
    // vector<Animal> animals_left;
    std::vector<uint32_t> best_path;
    std::vector<uint32_t> path;

    ZooOpttsp() {};

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
            animals.emplace_back(animal);
            ++id;
            cin >> row >> col;
        }
    }

    void pst_upper_bound() {
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

        // update animals vector
        int cur_index = 0;
        path.reserve(animals.size());
        for (size_t i = 0; i < animals.size(); ++i) {
            upper_bound += animals[i].cur_best_dist;
            path.push_back(animals[cur_index].num_id);
            cur_index = animals[cur_index].parent->num_id;
        }

        best_cur_sol = upper_bound;
        best_path = path;
    }  

    double calculate_mst(vector<Animal> &animals_left) {
        double running_weight = 0;
        size_t count = 0;
        animals_left[0].cur_best_dist = 0;
        size_t cur_index = 0;
        while (count != animals_left.size()) {

            for (size_t i = 0; i < animals_left.size(); ++i) {
                if (animals_left[i].visited == false) {
                    if (animals_left[cur_index].visited == true || animals_left[cur_index].cur_best_dist > animals_left[i].cur_best_dist) {
                        cur_index = i;
                    }
                    // if (static_cast<double>(animals_left[cur_index].cur_best_dist) == std::numeric_limits<double>::infinity()) {
                    //     cur_index = i;
                    // }
                    // if (animals_left[cur_index].cur_best_dist > animals_left[i].cur_best_dist) {
                    //     cur_index = i;
                    // }
                }
            }
            animals_left[cur_index].visited = true;
            for (size_t i = 0; i < animals_left.size(); ++i) {
                if (animals_left[i].visited == false) {
                    // if (animals_left[i].cage_type == animals_left[cur_index].cage_type || 
                    // animals_left[i].cage_type == 'b' || animals_left[cur_index].cage_type == 'b') {
                    double distance = calculate_distance(animals_left[i], animals_left[cur_index]);
                    if (distance < animals_left[i].cur_best_dist) {
                        if (animals_left[i].cur_best_dist != std::numeric_limits<double>::infinity()) {
                            running_weight = running_weight - (animals_left[i].cur_best_dist - distance);
                        }
                        else {
                            running_weight = running_weight + distance;
                        }
                        animals_left[i].cur_best_dist = distance;
                        // animals_left[i].parent = &animals_left[cur_index];
                    }
                    // }
                }
                
            }

            // if (count == 1) {
            //     animals_left[0].parent = &animals_left[cur_index];
            // }
            ++count;
            cur_index = count;
                    
        }

        return running_weight;
    } 

    void opttsp() {
        pst_upper_bound();
        gen_perms(1);

        cout << std::fixed << std::setprecision(2) << best_cur_sol << "\n";
        for (size_t i = 0; i < path.size(); ++i) {
            cout << best_path[i] << " ";
        }
    }

    void gen_perms(size_t perm_length) {
        if (perm_length == path.size()) {
            // compare with best current solution
            double intermediate_tent_sol = calculate_distance(animals[path[perm_length - 1]], animals[path[0]]);
            tentative_sol += intermediate_tent_sol;
            if (best_cur_sol > tentative_sol) {
                best_cur_sol = tentative_sol;
                best_path = path;
            }
            tentative_sol -= intermediate_tent_sol;
            return;
        }
        if (!promising(perm_length)) {
            return;
        }
        for (size_t i = perm_length; i < path.size(); ++i) {
            // double updated_distance = calculate_distance(animals[path[perm_length - 1]], animals[path[perm_length]]);
            std::swap(path[perm_length], path[i]);
            // animals_left.pop_back();
            double partial_sol = calculate_distance(animals[path[perm_length-1]], animals[path[perm_length]]);
            tentative_sol += partial_sol;
            gen_perms(perm_length + 1);
            // animals_left.push_back(animals[static_cast<int>(i)]);
            tentative_sol -= partial_sol;
            std::swap(path[perm_length], path[i]);
        }
    }

    bool promising(size_t perm_length) {
        if (path.size() - perm_length < 5) {
            return true;
        }
        vector<Animal> animals_left;
        animals_left.reserve(perm_length);
        for (size_t i = perm_length; i < path.size(); ++i) {
            animals_left.push_back(animals[path[i]]);
            // get rid of these lines
            animals_left[animals_left.size() - 1].cur_best_dist = std::numeric_limits<double>::infinity();
            animals_left[animals_left.size() - 1].visited = false;
            animals_left[animals_left.size() - 1].parent = nullptr;

        }

        double min_a = std::numeric_limits<double>::infinity();
        // int i_a = path[0];
        double min_b = std::numeric_limits<double>::infinity();
        // int i_b = path[0];
        for (size_t i = 0; i < animals_left.size(); ++i) {
            Animal ith_animal = animals_left[i];
            double distance_squared_a = calculate_distance_squared(ith_animal, animals[path[0]]);
            if (distance_squared_a < min_a) {
                min_a = distance_squared_a;
                // i_a = i;
            }
            double distance_squared_b = calculate_distance_squared(ith_animal, animals[path[perm_length - 1]]);
            if (distance_squared_b < min_b) {
                min_b = distance_squared_b;
                // i_b = i;
            }
        }
        min_a = sqrt(min_a);
        min_b = sqrt(min_b);
        double mst = calculate_mst(animals_left);
        return (((mst + tentative_sol + min_a + min_b) < best_cur_sol));
        return true;
    }
    
};

