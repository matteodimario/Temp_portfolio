
#include <cstdint>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <iostream>
#include <sstream>
#include <fstream>
#include <algorithm>
using namespace std;

// User class
class User {
    public:

    User() : user_id(0) {}

    User(unordered_set<string> set_IP_addresses, uint64_t timestamp, string user_id, uint32_t pin, uint32_t balance): 
    set_IP_addresses(set_IP_addresses), timestamp(timestamp), user_id(user_id), pin(pin), balance(balance) {}

    unordered_set<std::string> set_IP_addresses;
    uint64_t timestamp;
    string user_id;
    uint32_t pin;
    uint32_t balance;
};

// Transaction struct
struct Transaction {
    uint64_t timestamp;
    uint32_t id = 0;
    uint32_t fee = 0;
    uint64_t exec_date;
    double amount;
    string sender;
    string recipient; 
    string IP_address;  
    char trans_coverage;
};

// Options class
enum class VerboseOutputType { off, on };
enum class FileOutputType { off, on };

struct Options {
    VerboseOutputType verboseOutputType = VerboseOutputType::off;
    FileOutputType fileOutputType = FileOutputType::off;
    string file_name;
};

struct CompareExecDate {
    bool operator()(const Transaction& t, uint64_t exec_date) const {
        return t.exec_date < exec_date;
    }

    bool operator()(uint64_t exec_date, const Transaction& t) const {
        return exec_date < t.exec_date;
    }
};

// priority queue comparator
struct Comp {
    Comp() {}

    bool operator() (const Transaction &lhs, const Transaction &rhs) const {
        if ((lhs.exec_date) == (rhs.exec_date)) {
            return lhs.id > rhs.id;
        }
        else {
            return (lhs.exec_date > rhs.exec_date);
        }
    }
};

// struct Comp_vec {
//     Comp_vec() {}

//     bool operator() (const Transaction &lhs, const Transaction &rhs);
// }

// parse date
string date_format(const string &timestamp) {
    string timestamp_num = "";
    for (char character : timestamp) {
        if (isdigit(character)) {
            timestamp_num += character;
        }
    }
    return timestamp_num;
}


// Bank class
class Bank {
    public:

    
    
    // Bank constructor
    Bank (unordered_map<string, User> active_users): active_users(active_users) {}

    // login function
    void login(Options &options) {  
        uint32_t pin;
        cin >> user_id >> pin >> IP_address;
        
        auto current_id = active_users.find(user_id);
        if (current_id != active_users.end() && pin == active_users[user_id].pin) {
            auto current_IP = current_id->second.set_IP_addresses.find(IP_address);
            if (current_IP == current_id->second.set_IP_addresses.end()) {
                current_id->second.set_IP_addresses.insert(IP_address);
            }
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "User " << user_id << " logged in." << "\n";
            }
        }
        else {
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Failed to log in " << user_id << "." << "\n";
            }
        }       
    }

    // logout function
    void logout(Options &options) {
        cin >> user_id >> IP_address;
        auto current_id = active_users.find(user_id);
        if (current_id != active_users.end()) {
            auto current_IP = current_id->second.set_IP_addresses.find(IP_address);
            if (current_IP != current_id->second.set_IP_addresses.end()) {
                current_id->second.set_IP_addresses.erase(IP_address);
                if (options.verboseOutputType == VerboseOutputType::on) {
                    cout << "User " << user_id << " logged out." << "\n";
                }
            }
            else {
                if (options.verboseOutputType == VerboseOutputType::on) {
                    cout << "Failed to log out " << user_id << "." << "\n";
                }               
            }
        }
        else {
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Failed to log out " << user_id << "." << "\n";
            } 
        }
    }

    // place function
    void place(Options &options) {
        // read in and initialization of transaction
        string timestamp;
        string exec_date;
        cin >> timestamp;
        cin >> transaction.IP_address;
        cin >> transaction.sender;
        cin >> transaction.recipient;
        cin >> transaction.amount;
        cin >> exec_date;
        cin >> transaction.trans_coverage;
        // transform the input in date format
        timestamp = date_format(timestamp);
        std::istringstream(timestamp) >> transaction.timestamp;
        exec_date = date_format(exec_date);
        std::istringstream(exec_date) >> transaction.exec_date;

        bool valid_transaction = true;

        // check if the transaction is valid
        check_transaction_is_valid(valid_transaction, options);

        // transaction is valid
        if (valid_transaction == true) {
            transaction.id = count_id;
            Transaction placed_transaction = transaction;
            
            // check if there are transactions to be executed
            while (!transaction_pq.empty() && transaction_pq.top().exec_date <= placed_transaction.timestamp) {
                transaction = transaction_pq.top();                
                perform_transaction(valid_transaction, options);               
            }  

            // place current transaction
            transaction_pq.push(placed_transaction);
            valid_transaction = false;          
            if (options.verboseOutputType == VerboseOutputType::on) {            
                cout << "Transaction placed at " << (placed_transaction.timestamp) << ":" << " $";
                cout << placed_transaction.amount << " from " << placed_transaction.sender;
                cout << " to " << placed_transaction.recipient << " at " << placed_transaction.exec_date << "." << "\n";
            }
            count_id++;       
        }      
    }

    void check_transaction_is_valid(bool &valid_transaction, Options &options) {
        // checks for valid transaction:
        // 1. transactions is not 3 days within execution
        if ((transaction.exec_date - transaction.timestamp) > 3000000) {
            valid_transaction = false;
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Select a time less than three days in the future." << "\n";
            }
            return;
        }
        // 2. sender is invalid
        auto sender_it = active_users.find(transaction.sender);
        if (sender_it == active_users.end()) {
            valid_transaction = false;
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Sender " << transaction.sender << " does not exist." << "\n";
            }
            return;
        }
        // 3. recipient is invalid
        auto recipient_it = active_users.find(transaction.recipient);
        if (recipient_it == active_users.end()) {
            valid_transaction = false;
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Recipient " << transaction.recipient << " does not exist." << "\n";
            }
            return;
        }
        // 4. user is not registered at time of execution
        if (active_users[transaction.sender].timestamp > transaction.exec_date || 
        active_users[transaction.recipient].timestamp > transaction.exec_date) {
            valid_transaction = false;
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "At the time of execution, sender and/or recipient have not registered." << "\n";
            }
            return;
        } 
        // 5. user is logged in 
        unordered_set<std::string> set_IP_addresses_sender = active_users[transaction.sender].set_IP_addresses;
        if (set_IP_addresses_sender.empty()) {
            valid_transaction = false;
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Sender " << transaction.sender << " is not logged in." << "\n";
            }
            return;
        }
           
        // 6. transaction is fraudulent
        auto IP_address_it = active_users[transaction.sender].set_IP_addresses.find(transaction.IP_address);
        if (IP_address_it == active_users[transaction.sender].set_IP_addresses.end()) {
            valid_transaction = false;
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Fraudulent transaction detected, aborting request." << "\n";
            } 
            return;
        }
    }

    // complete transactions that have remained in the pq
    void finish_transactions(Options &options) {
        bool valid_transaction = false;
        while (!transaction_pq.empty()) {
            transaction = transaction_pq.top();
            perform_transaction(valid_transaction, options);
        }
    }

    // complete transaction
    void perform_transaction(bool &valid_transaction, Options &options) {
        valid_transaction = true;
        calculate_fee(valid_transaction);
        // transaction_map[transaction.id] = transaction;
        
        // if invalid transaction print insufficient funds
        if (valid_transaction == false) {
            if (options.verboseOutputType == VerboseOutputType::on) {
                cout << "Insufficient funds to process transaction " << transaction_pq.top().id << "." << "\n";
                valid_transaction = false;
            }
        }
        // if valid transaction execute it
        else if (valid_transaction) {
            transaction_date_vector.push_back(transaction);
            
            if (transaction.sender == transaction.recipient) {
                transaction_user_map[transaction.sender].push_back(transaction);
            }
            else {
                transaction_user_map[transaction.sender].push_back(transaction);
                transaction_user_map[transaction.recipient].push_back(transaction);
            }
            if (options.verboseOutputType == VerboseOutputType::on) {
                Transaction executed_transaction = transaction_pq.top();
                cout << "Transaction executed at " << executed_transaction.exec_date << ": $" 
                << executed_transaction.amount << " from " << executed_transaction.sender << 
                " to " << executed_transaction.recipient << "." << "\n";
            }
        }
        transaction_pq.pop();
    }

    // calculate fees
    void calculate_fee(bool &valid_transaction) {
        uint32_t  fee_sender = 0;
        uint32_t fee_recipient = 0;

        bool loyalty_cust = false;
        // set if it is a loyal customer
        if (transaction.exec_date - active_users[transaction.sender].timestamp > 50000000000) {
            loyalty_cust = true;
        }

        // fee paid by sender
        if (transaction.trans_coverage == 'o') {
            // calculate fee
            if (transaction.amount * 0.01 < 10) {
                transaction.fee = 10;
            }
            else if (transaction.amount * 0.01 > 450) {
                transaction.fee = 450;
            }
            else if ((transaction.amount * 0.01) >= 10 && (transaction.amount * 0.01) <= 450) {
                transaction.fee = static_cast<int>(transaction.amount * 0.01);
            }
            // if it is loyal customer check balance and make transaction
            if (loyalty_cust && active_users[transaction.sender].balance >= (((transaction.fee * 3) / 4) + transaction.amount)) {
                active_users[transaction.sender].balance -= (transaction.fee * 3) / 4 ;
                transaction.fee = (transaction.fee * 3) / 4;
                active_users[transaction.recipient].balance += static_cast<uint32_t>(transaction.amount);
                active_users[transaction.sender].balance -= static_cast<uint32_t>(transaction.amount);
                revenue += transaction.fee;
                valid_transaction = true;
            }
            // if it is not loyal customer check balance and make transaction
            else if (!loyalty_cust && active_users[transaction.sender].balance >= (transaction.fee + transaction.amount)) {
                active_users[transaction.sender].balance -= transaction.fee;
                active_users[transaction.recipient].balance += static_cast<uint32_t>(transaction.amount);
                active_users[transaction.sender].balance -= static_cast<uint32_t>(transaction.amount);
                revenue += transaction.fee;
                valid_transaction = true;
            }
            // if the balance is not sufficient
            else {
                valid_transaction = false;
            }
        }
        // fee paid by sender and recipient
        if (transaction.trans_coverage == 's') {
            if (transaction.amount * 0.01 < 10) {
                transaction.fee = 10;
            }
            else if (transaction.amount * 0.01 > 450) {
                transaction.fee = 450;
            }
            else if (transaction.amount * 0.01 >= 10 && transaction.amount * 0.01 <= 450) {
                transaction.fee = static_cast<int>(transaction.amount * 0.01);
            } 
            // if it is loyal customer          
            if (loyalty_cust) {
                transaction.fee = (transaction.fee * 3) / 4;
                if (transaction.fee % 2 == 1) {
                    fee_sender = transaction.fee / 2 + 1;
                    fee_recipient = transaction.fee / 2;
                }
                else {
                    fee_sender = transaction.fee / 2;
                    fee_recipient = transaction.fee / 2;
                }
            }
            // if it is not loyal customer
            else {
                if (transaction.fee % 2 == 1) {
                    fee_sender = transaction.fee / 2 + 1;
                    fee_recipient = transaction.fee / 2;
                }
                else {
                    fee_sender = transaction.fee / 2;
                    fee_recipient = transaction.fee / 2;
                }
            }
            // check balance and make transaction
            if ((active_users[transaction.sender].balance >= (fee_sender + transaction.amount)) && 
            (active_users[transaction.recipient].balance >= fee_recipient)) {
                active_users[transaction.sender].balance -= fee_sender;
                active_users[transaction.recipient].balance -= fee_recipient;
                transaction.fee = fee_sender + fee_recipient;
                active_users[transaction.recipient].balance += static_cast<uint32_t>(transaction.amount);
                active_users[transaction.sender].balance -= static_cast<uint32_t>(transaction.amount);
                valid_transaction = true;
                revenue += fee_sender + fee_recipient;
            }
            // if the balance is not sufficient
            else {
                valid_transaction = false;
            }
        }
    }

    void l_query() {
        int count = 0;
        string x;
        string y;
        cin >> x >> y;
        x = date_format(x);
        y = date_format(y);
        string y_str; string x_str;
        uint64_t x_num;
        uint64_t y_num;
        std::istringstream(x) >> x_num;
        std::istringstream(y) >> y_num;
        auto transaction_it = std::lower_bound(transaction_date_vector.begin(), transaction_date_vector.end(), x_num, CompareExecDate());
        if (transaction_it == transaction_date_vector.end()) {
            cout << "There were 0 transactions that were placed between time " << x_num << " to " << y_num << "." << "\n";
            return;
        }
        string dollars = " dollars";
        while (transaction_it < transaction_date_vector.end() && transaction_it->exec_date < y_num) {
            Transaction transaction1 = *transaction_it;
            if (transaction1.amount == 1) {dollars = " dollar";}
            cout << transaction1.id << ": " << transaction1.sender << " sent " << transaction1.amount;
            cout << dollars << " to " << transaction1.recipient << " at " << transaction1.exec_date << "." << "\n";
            ++count;
            dollars = " dollars";
            transaction_it++;            
        }
        string be_str = "were ";
        string transactions_str = " transactions";
        if (count == 1) {be_str = "was "; transactions_str = " transaction";}
        cout << "There " << be_str << count << transactions_str << " that " << be_str 
        << "placed between time " << x_num << " to " << y_num << "." << "\n";
    }

    void r_query() {
        int revenue_date = 0;
        string x;
        string y;
        cin >> x >> y;
        x = date_format(x);
        y = date_format(y);
        string y_str; string x_str;
        uint64_t x_num; 
        uint64_t y_num;
        std::istringstream(x) >> x_num;
        std::istringstream(y) >> y_num;
        auto transaction_it = std::lower_bound(transaction_date_vector.begin(), transaction_date_vector.end(), x_num, CompareExecDate());
        // if (transaction_it == transaction_date_vector.end()) {
        //     transaction_it->exec_date = y_num + 1;
        // }
        while (transaction_it < transaction_date_vector.end() && transaction_it->exec_date < y_num) {
            Transaction transaction1 = *transaction_it;
            revenue_date += transaction1.fee;  
            transaction_it++;             
        }

        string years = "years"; string months = "months"; string days = "days"; 
        string hours = "hours"; string minutes = "minutes"; string seconds = "seconds";
        cout << "281Bank has collected " << revenue_date << " dollars in fees over";
        uint64_t result = y_num - x_num;
        if (((result / 10000000000) % 100) != 0) {
            cout << " ";   
            cout << (result / 10000000000) % 100;
            if ((result / 10000000000) % 100 == 1) {years = "year";}
            cout << " " << years;
        }
        if (((result / 100000000) % 100) != 0) {  
            cout << " ";         
            cout << (result / 100000000) % 100;
            if ((result / 100000000) % 100 == 1) {months = "month";}
            cout << " " << months;
        }
        if (((result / 1000000) % 100) != 0) {  
            cout << " ";           
            cout << (result / 1000000) % 100;
            if ((result / 1000000) % 100 == 1) {days = "day";}
            cout << " " << days;
            
        }
        if (((result / 10000) % 100) != 0) { 
            cout << " ";              
            cout << (result / 10000) % 100; 
            if ((result / 10000) % 100 == 1) {hours = "hour";}
            cout << " " << hours;
        }
        if (((result / 100) % 100) != 0) {   
            cout << " ";           
            cout << (result / 100) % 100; 
            if ((result / 100) % 100 == 1) {minutes = "minute";}
            cout << " " << minutes;
        }
        if (((result % 100)) != 0) {   
            cout << " ";           
            cout << (result % 100);
            if ((result % 100) == 1) {seconds = "second";}
            cout << " " << seconds; 
        }
        cout << "." << "\n";
    }

    void h_query() {
        string in_user_id;
        cin >> in_user_id;
        auto user_id_it = active_users.find(in_user_id);
        if (user_id_it == active_users.end()) {
            cout << "User " << in_user_id << " does not exist." << "\n";
        }
        else {
            cout << "Customer " << in_user_id << " account summary:" << "\n";
            cout << "Balance: $" << active_users[in_user_id].balance << "\n";
            vector<Transaction> sender_tr;
            vector<Transaction> recipient_tr;
            int count_tr_in = 0;
            int count_tr_out = 0;
            vector<Transaction> customer_transactions = transaction_user_map[in_user_id];
            for (size_t i = 0; i < customer_transactions.size(); ++i) {
                if (customer_transactions[i].sender == customer_transactions[i].recipient) {
                    count_tr_in++;
                    count_tr_out++;
                    sender_tr.push_back(customer_transactions[i]);
                    recipient_tr.push_back(customer_transactions[i]);
                }
                else if (customer_transactions[i].sender == in_user_id) {
                    count_tr_out++;
                    sender_tr.push_back(customer_transactions[i]);
                }
                else if (customer_transactions[i].recipient == in_user_id) {
                    count_tr_in++;
                    recipient_tr.push_back(customer_transactions[i]);
                }
                
            }

            cout << "Total # of transactions: " << count_tr_in + count_tr_out << "\n";
            cout << "Incoming " << count_tr_in << ":" << "\n";
            int i = 0;
            bool transactions_num = false;
            string dollar = " dollars";
            int count = 0;
            size_t max_transactions = 10;
            if ((recipient_tr.size()) > max_transactions) {
                i = static_cast<int>(recipient_tr.size()) - 10;
            }
            while (static_cast<size_t>(i) < recipient_tr.size() && transactions_num == false && count < 10) {  
                if (!recipient_tr.empty() && recipient_tr[i].amount == 1) {
                    dollar = " dollar";
                }         
                cout << recipient_tr[i].id << ": " << recipient_tr[i].sender << " sent " << 
                recipient_tr[i].amount << dollar << " to " << recipient_tr[i].recipient << " at " << recipient_tr[i].exec_date << "." << "\n";
                ++i;
                dollar = " dollars";
                ++count;
            }
            cout << "Outgoing " << count_tr_out << ":" << "\n";
            i = 0;
            transactions_num = false;
            dollar = " dollars ";
            count = 0;
            if ((sender_tr.size()) > max_transactions) {
                i = static_cast<int>(sender_tr.size()) - 10;
            }
            while (static_cast<size_t>(i) < sender_tr.size() && transactions_num == false && count < 10) {
                if (!sender_tr.empty() && sender_tr[i].amount == 1) {
                    dollar = " dollar ";
                }           
                cout << sender_tr[i].id << ": " << sender_tr[i].sender << " sent " << 
                sender_tr[i].amount << dollar << "to " << sender_tr[i].recipient << " at " << sender_tr[i].exec_date << "." << "\n";
                ++i;
                count++;
                dollar = " dollars ";
            }
        }       
    }

    void s_query() {
        string date;
        cin >> date;
        date = date_format(date);
        uint64_t date_num;
        std::istringstream(date) >> date_num;
        uint64_t date_num1 = date_num;
        uint64_t date_num2 = date_num + 1000000;
        date_num1 = (date_num1 / 1000000) * 1000000;
        date_num2 = (date_num2 / 1000000) * 1000000;
        cout << "Summary of [" << date_num1 << ", " << date_num2 << "):" << "\n";
        // vector<Transaction> transactions_date;
        auto transaction_it = std::lower_bound(transaction_date_vector.begin(), transaction_date_vector.end(), date_num1, CompareExecDate());
        if (transaction_it == transaction_date_vector.end()) {
            cout << "There were a total of 0 transactions, 281Bank has collected 0 dollars in fees." << "\n";
            return;
        }
        int count = 0;
        double total_fees = 0;
        string dollars = " dollars";
        while ( transaction_it < transaction_date_vector.end() && transaction_it->exec_date < date_num2) {
            Transaction t = *transaction_it;
            if (t.amount == 1) {
                dollars = " dollar";
            }
            total_fees += t.fee;
            cout << t.id << ": " << t.sender << " sent " << t.amount 
            << dollars << " to " << t.recipient << " at " << t.exec_date << "." << "\n";
            ++ count;
            dollars = " dollars";
            transaction_it++;
        }
        
        string transaction_str = "transactions";
        string be_str = "were";
        if (count == 1) {
            transaction_str = "transaction";
            be_str = "was";
        }  
        cout << "There " << be_str << " a total of " << count << " " << transaction_str 
        << ", 281Bank has collected " << total_fees << " dollars in fees." << "\n"; 
    }

    private:
    unordered_map<string, User> active_users;
    std::priority_queue<Transaction, std::vector<Transaction>, Comp> transaction_pq;
    unordered_map<string, vector<Transaction>> transaction_user_map;
    vector<Transaction> transaction_date_vector;
    Transaction transaction;
    string user_id;
    string IP_address;
    string timestamp;
    int amount;
    string exec_date;
    char trans_coverage;
    uint32_t count_id = 0;
    int revenue = 0;
};



