
#include <getopt.h>
#include <iostream>
#include <string>
#include <fstream>
#include "zoo_opttsp.h"
using namespace std;

struct Options {
    string mode = "";
};

void GetMode(int argc, char *argv[], Options &options) {
    int choice;  
    option long_options[] = {
        {"mode", required_argument, nullptr, 'm'},
        {"help", no_argument, nullptr, 'h'},
        {nullptr, 0, nullptr, 0}
    };

    while ((choice = getopt_long(argc, argv, "m:h", long_options, nullptr)) != -1) {

        switch (choice) {
            case 'm':
                options.mode = optarg;
                break;

            case 'h':
                // Print help message and exit
                std::cout << "Error" << '\n';
                exit(0);

            default:
                std::cerr << "Error: invalid option" << '\n';
                exit(1);
        }           
    }
}

int main(int argc, char* argv[]) {
    std::ios_base::sync_with_stdio(false);
    Options options;
    GetMode(argc, argv, options);

    // mst case
    if (options.mode == "MST") {
        ZooMst zoo_mst;
        zoo_mst.read_in();
        zoo_mst.mst();
    }

    // fasttsp case
    if (options.mode == "FASTTSP") {
        ZooFasttsp zoo_fasttsp;
        zoo_fasttsp.read_in();
        zoo_fasttsp.fasttsp();
    }

    // opttsp case
    if (options.mode == "OPTTSP") {
        ZooOpttsp zoo_opttsp;
        zoo_opttsp.read_in();
        zoo_opttsp.opttsp();
    }

}

