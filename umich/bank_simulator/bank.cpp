
#include <getopt.h>
#include <cstdint>
#include <iostream>
#include <string>
#include "classes.h"
#include <fstream>
using namespace std;

void GetMode(int argc, char *argv[], Options &options) {
    int choice;  
    option long_options[] = {
        {"verbose", no_argument, nullptr, 'v'},
        {"file", required_argument, nullptr, 'f'},
        {"help", no_argument, nullptr, 'h'},
        {nullptr, 0, nullptr, 0}
    };

    while ((choice = getopt_long(argc, argv, "vf:h", long_options, nullptr)) != -1) {

        switch (choice) {
            case 'v':
                options.verboseOutputType = VerboseOutputType::on;
                break;

            case 'f':
                options.fileOutputType = FileOutputType::on;
                options.file_name = optarg;
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

///////////////////////////////////////////// main ///////////////////////////////////

int main(int argc, char** argv) {
    std::ios_base::sync_with_stdio(false);
    // Initializations
    string first_word;
    bool start_queries = false;
    unordered_map<string, User> active_users;
    Options options;
    GetMode(argc, argv, options);

    // read in registration file
    ifstream file;
    file.open(options.file_name);
    string line;
    while (file.peek() != EOF) {
        string timestamp_str = ""; 
        getline(file, timestamp_str, '|');
        string timestamp = date_format(timestamp_str);
        uint64_t timestamp_num;
        std::istringstream(timestamp) >> timestamp_num;
        string user_id = "";
        getline(file, user_id, '|');
        string pin_str = "";
        getline(file, pin_str, '|');
        uint32_t pin = stoi(pin_str);
        string balance_str = "";
        getline(file, balance_str);
        uint32_t balance = stoi(balance_str);
        unordered_set<std::string> set_IP_addresses = {};
        User userx(set_IP_addresses, timestamp_num, user_id, pin, balance);
        active_users.emplace(user_id, userx);
    }

    // Initialize the bank class
    Bank bank281(active_users);

    // read in cin
    while (start_queries == false && cin) {
        cin >> first_word;
        if (first_word != "$$$") {
            // comment
            if (first_word[0] == '#') {
                string line;
                getline(cin, line);
            }
            // login
            else if (first_word[0] == 'l') {               
                bank281.login(options);
            }
            // logout
            else if (first_word[0] == 'o') {
                bank281.logout(options);
            }
            // place
            else if (first_word[0] == 'p') {
                bank281.place(options);
            }
        }
        else {
            start_queries = true;
        }
    }

    // complete transactions in the pq not executed yet
    bank281.finish_transactions(options);

    cin >> first_word;
    while (cin) {
        // list transactions
        if (first_word == "l") {
            bank281.l_query();
        } 
        // revenue
        else if (first_word == "r") {
            bank281.r_query();
        }
        // customer history
        else if (first_word == "h") {
            bank281.h_query();
        }
        // summarize day
        else if (first_word == "s") {
            bank281.s_query();
            // getline(cin, line);
        }
        cin >> first_word;
    }
}