
#include <iostream>
#include <map>
#include "csvstream.h"
#include <iostream>
#include <string>
#include <set>
#include <tgmath.h> 
#include <bits/stdc++.h>
#include <iomanip>
using namespace std;

class Classifier {
  public:
  map<string, int> label_freq;
  map<string, int> word_freq;
  map<string, map<string, int>> label_word_freq;
  string label_selected;
  int count_posts = 0;

  set<string> unique_words(const string &str) {
  istringstream source(str);
  set<string> words;
  string word;
  while (source >> word) {
    words.insert(word);
  }
  return words;
}

  string get_label_selected() {
    return label_selected;
  }

  void calc_probability_debug(set<string> post) {
    label_selected = "";
    auto it = post.begin();
    for (; it != post.end(); it++) {
      cout << *it;
    }

    cout << "classes:" << endl;
    
    auto it1 = label_word_freq.begin();
    while (it1 != label_word_freq.end()) {
      cout << "  ";
      cout << it1->first << ", " << label_freq[it1->first] << " examples, ";
      cout << "log-prior = " << log(static_cast<double>(label_freq[it1->first]
       / static_cast<double>(count_posts))) << endl;
      ++it1;
    }
    cout << "classifier parameters:" << endl;
    
    auto it2 = label_freq.begin();
    
      while (it2 != label_freq.end()) {
        auto it3 = word_freq.begin();
        while(it3 != word_freq.end()) {
          if (label_word_freq[it2->first][it3->first] != 0) {
          cout << "  " << it2->first << ":" << it3->first;
          cout << ", count = " << label_word_freq[it2->first][it3->first];
          cout << ", log-likelihood = " << log(static_cast<double>(
            label_word_freq[it2->first][it3->first]) / 
            static_cast<double>(label_freq[it2->first]));
          cout << endl;
          }
          ++it3;
        }
      ++it2;
      }
    


    calc_probability(post);
  }

    double calc_probability(set<string> post) {
      
      double probability = 0;
      double final_probability = 0;
      double final_current_probability = -1000000;
      double denominator = 0;
      double numerator = 0;
      auto it = label_word_freq.begin();
      label_selected = "";
      while(it != label_word_freq.end()) {
        probability = 0;
        final_probability = 0;
        denominator = label_freq[it->first];
          auto it2 = post.begin();
          while(it2 != post.end()) {
            
            numerator = label_word_freq[it->first][*it2];
            if (word_freq[*it2] != 0 && numerator == 0) {
              numerator = word_freq[*it2];
              probability = log((static_cast<double>(numerator)) / 
              (static_cast<double>(count_posts)));

            }
            else if (numerator == 0) {
              probability = log(1.0 / (static_cast<double>(count_posts)));
            }
            
            else {
            probability = log(numerator / denominator);
            }
            final_probability = final_probability + probability;
            ++it2;
          }
          final_probability = final_probability + log(static_cast<double>
          (label_freq[it->first]) / static_cast<double>(count_posts));
          
          if (final_probability > final_current_probability) {
            final_current_probability = final_probability;
            label_selected = it->first;
          }
          ++it;
        
          
          
      }
      
            
      return final_current_probability; 
      
      
      
      
      
      
    }

void debug_information(){
  //classes
  cout << "classifier parameters:" << endl;
  // cout << " " << 

}

void train_debug(string file_name) {
      // add error checking
  csvstream csvin(file_name);
  map<string, string> row;
  int count_words = 0;
  set<string> vocabulary;
  
  
  cout << "training data:" << endl;
  while (csvin >> row) {
    cout << "  ";
    string tag = row["tag"];
    string content = row["content"];
    string phrase = content;
    set<string> unique_words = this->unique_words(phrase);
    label_freq[tag]++;
    
    
    // std::stringstream ss(content);
    // while (ss >> content) {
    //   unique_words.insert(content);
    // }

    
      for (auto it = unique_words.begin(); it != unique_words.end(); it++) {
        word_freq[*it]++;
        label_word_freq[tag][*it]++;
        vocabulary.insert(*it);
      }
      cout << "label = " << tag << ", ";
      cout << "content = " << phrase << endl;
    
    count_posts++;
  }
  for (auto it = vocabulary.begin(); it != vocabulary.end(); it++) {
    ++count_words;
  }
  cout << "trained on " << count_posts << " examples" << endl;
  cout << "vocabulary size = " << count_words << endl << endl;
}

void train(string file_name) {
  
    // add error checking
  csvstream csvin(file_name);
  map<string, string> row;
  
  
  

  while (csvin >> row) {
    string label = row["tag"];
    string content = row["content"];
    set<string> unique_words = this->unique_words(content);
    label_freq[label]++;
    
    // std::istringstream ss(content);
    // while (ss >> content) {
    //   unique_words.insert(content);
    // }
      for (auto it = unique_words.begin(); it != unique_words.end(); it++) {
        word_freq[*it]++;
        label_word_freq[label][*it]++;
      }
    
    count_posts++;
  }
  cout << "trained on " << count_posts << " examples" << endl << endl;
}
private:
};

void print_data(string file_name, string file_test, string debug) {
  csvstream csvin(file_name);
  Classifier classifier;
  
  set<string> test_set_words;
  csvstream csvout(file_test);
  map<string, string> row;
  int correct = 0;
  int incorrect = 0;

  if (debug == "--debug") {
     classifier.train_debug(file_name);
  }
  else {
    classifier.train(file_name);
  }

  if (debug == "--debug") {
    classifier.calc_probability_debug(test_set_words);
  }

    cout << endl << "test data:" << endl;
    while (csvout >> row) {
      
      test_set_words.clear();
      string content = row["content"];
      string tag = row["tag"];
      test_set_words = classifier.unique_words(content);
      // std::istringstream ss(content);
      // while (ss >> content) {
      // test_set_words.insert(content);
      // }
      double probability = classifier.calc_probability(test_set_words);
      cout << "  " << "correct = " << tag << ", ";
      cout << "predicted = " << classifier.get_label_selected();
      if (classifier.get_label_selected() == tag) {
        ++correct;
      }
      else {
        ++incorrect;
      }
      cout << ", log-probability score = " << probability << endl;
      cout << "  " <<  "content = " << row["content"] << endl << endl;
      
    }
    cout << "performance: " << correct << " / " << (correct + incorrect);
    cout << " posts predicted correctly" << endl;
}

int main(int argv, char *argc[]) {
  string debug = "";
  if (argv == 4) {
  debug = argc[3];
  }
  if (argv != 3 && argv != 4 && debug != "debug") {
    cout << "Usage: main.exe TRAIN_FILE TEST_FILE [--debug]" << endl;
    return 1;
  }
  cout.precision(3);
  string file_name = argc[1];
  
  
  string file_test = argc[2];

  ifstream file_name_ifstream;
  file_name_ifstream.open(file_name);
  if (!file_name_ifstream) {
    cout << "Error opening file: " << file_name << endl;
    return 1;
  }
  ifstream file_test_ifstream;
  file_test_ifstream.open(file_test);
  if (!file_test_ifstream) {
    cout << "Error opening file: " << file_test << endl;
    return 1;
  }

  print_data(file_name, file_test, debug);
  
  

  
  
  return 0;

}

