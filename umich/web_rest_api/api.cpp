
#include <iostream>
#include <list>
#include <string>
#include "json.hpp"

using nlohmann::json;
using namespace std;

class OHQueue {
public:
string path;

//Need to make sure it returns 0 for bad request!!!!!
void read_request() {
    string request_type;
    
    cin >> request_type;
    cin >> path;
    if (request_type == "GET") {
        
         
        
        if (path != "/api/" && path != "/api/queue/" && path != 
        "/api/queue/head/") {
            is_path_bad_request();
            return;
        }
        
        if (path == "/api/") {
            is_get_api();
            
            //read routes
        }
        else if (path == "/api/queue/") {
            if (queue.empty()) {
               is_path_empty();
               return;
            }
            is_get_api_queue();
            //read all queue positions
        }
        else if (path == "/api/queue/head/") {
            // check if list is empty
            if (queue.empty()) {
                is_path_bad_request_empty();
                return;
            }
            is_get_api_queue_head();
            //read first queue position
        }
    
    }
    else if (request_type == "POST") {
        
        if (path != "/api/queue/tail/") {
            is_path_bad_request();
            return;
        }
        
        
        is_post();
        //post
    }
    else if (request_type == "DELETE") {
        
    
        if (path != "/api/queue/head/") {
            is_path_bad_request();
            return;
        }
        if (queue.empty()) {

            is_path_bad_request_delete_empty();
            return;
        }
        is_delete();
    }
    
}

void is_path_bad_request() {
    string junk;
    while(junk != "Content-Length:"){
        cin >> junk;
    }
    cin >> junk;
    json junk_json;
    cin >> junk_json;
    cout << "HTTP/1.1 400 Bad Request" << endl;
    cout << "Content-Type: application/json; charset=utf-8" << endl;
    cout << "Content-Length: 0" << endl << endl;
    
    // should return 0
    // to implement!!!!
}

void is_path_bad_request_delete_empty() {
    string junk;
    while(junk != "charset=utf-8") {
        cin >> junk;
    }
    cout << "HTTP/1.1 400 Bad Request" << endl;
    cout << "Content-Type: application/json; charset=utf-8" << endl;
    cout << "Content-Length: 0" << endl << endl;
}

void is_path_bad_request_empty() {
    string junk;
    while(junk != "Content-Length:"){
        cin >> junk;
    }
    cin >> junk;
    cout << "HTTP/1.1 400 Bad Request" << endl;
    cout << "Content-Type: application/json; charset=utf-8" << endl;
    cout << "Content-Length: 0" << endl << endl;
    
    // should return 0
    // to implement!!!!
}

void is_get_api() {
    cout << "HTTP/1.1 200 OK" << endl;
            cout << "Content-Type: application/json; charset=utf-8" << endl;
            cout << "Content-Length: 160" << endl << endl;
            json j1;
            {
            j1["queue_head_url"] = "http://localhost/queue/head/";
            j1["queue_list_url"] = "http://localhost/queue/";
            j1["queue_tail_url"] = "http://localhost/queue/tail/";
            }
        string str2 = j1.dump(4) + "\n";  // dump with indentation using 4 spaces
        cout << str2;
}

void is_get_api_queue() {
    string junk;
            int count = 0;
            while (count != 8) {
               cin >> junk;
               ++count;
            }
            json jstudents;
            cout << "HTTP/1.1 200 OK" << endl;
            cout << "Content-Type: application/json; charset=utf-8" << endl;
            cout << "Content-Length: 412" << endl << endl;
            Student s1 = queue.front();
            for (std::list<Student>::iterator i1 = queue.begin(); i1 != 
            queue.end();++i1) {
                jstudents.push_back(i1->jdata);
            
            }
            json joutput;
            joutput["count"] = queue.size();
            //joutput.push_back(jstudents);
            joutput["results"] = jstudents;
            string str2 = (joutput).dump(4) + "\n";
            cout << str2;      
}

void is_get_api_queue_head() {
    string junk;
    if (queue.empty()) {
        is_path_bad_request();
        return;
    }
            int count = 0;
            while (count != 8) {
               cin >> junk;
               ++count;
            }
            Student s1 = queue.front();
            string str2 = (s1.jdata).dump(4) + "\n";
            cout << "HTTP/1.1 200 OK" << endl;
            cout << "Content-Type: application/json; charset=utf-8" << endl;
            cout << "Content-Length: " << str2.length() << endl << endl;
            
            cout << str2;
}

void is_post() {
    json j1;
        Student s1;
        s1.position = queue.size() + 1;
        string junk;
        int count = 0;
        while (count != 8) {
            cin >> junk;
            ++count;
        }
        cin >> j1;
        j1["position"] = s1.position;
        s1.jdata = j1;
        queue.push_back(s1);
        string str2 = j1.dump(4) + "\n"; 
        cout << "HTTP/1.1 201 Created" << endl;
        cout << "Content-Type: application/json; charset=utf-8" << endl;
        cout << "Content-Length: " << str2.length() << endl << endl;
         // dump with indentation using 4 spaces
        cout << str2;
}

void is_delete() {
        queue.pop_front();
            for (std::list<Student>::iterator i1 = queue.begin(); i1 != 
            queue.end();++i1) {
                --i1->position;
                i1->jdata["position"] = i1->position;
            
            }
        cout << "HTTP/1.1 204 No Content" << endl;
        cout << "Content-Type: application/json; charset=utf-8" << endl;
        cout << "Content-Length: 0" << endl << endl;
        //delete
}

void is_path_empty() {
    cout << "HTTP/1.1 200 OK" << endl;
    cout << "Content-Type: application/json; charset=utf-8" << endl;
    cout << "Content-Length: 40" << endl << endl;
    json joutput;
    joutput["count"] = 0;
    //joutput.push_back(jstudents);
    joutput["results"] = nullptr;
    string str2 = joutput.dump(4) + "\n";  
    // dump with indentation using 4 spaces
    cout << str2;
}



private:
  struct Student {
    json jdata;
    int position;
  };

  std::list<Student> queue;
};

int main () {
    OHQueue queue;
    while (cin) {
        queue.read_request();
    }
}