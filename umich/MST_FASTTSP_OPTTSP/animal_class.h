
#include <cstdint>
#include <getopt.h>
#include <iostream>
#include <string>
#include <fstream>
#include <limits>
#include <cmath>
using namespace std;

class Animal {
public:
    Animal(int row, int col, uint32_t num_id)
        : row(row), col(col), num_id(num_id) {}

    int row;
    int col;
    uint32_t num_id;
    uint32_t cage_type;
    bool visited = false;
    Animal *parent;
    double cur_best_dist = std::numeric_limits<double>::infinity();
};

double calculate_distance(const Animal &animal1, const Animal &animal2) {
    double row_diff = animal1.row - animal2.row;
    double col_diff = animal1.col - animal2.col;

    return sqrt(row_diff * row_diff + col_diff * col_diff);
}

double calculate_distance_squared(const Animal &animal1, const Animal &animal2) {
    double row_diff = animal1.row - animal2.row;
    double col_diff = animal1.col - animal2.col;

    return row_diff * row_diff + col_diff * col_diff;
}