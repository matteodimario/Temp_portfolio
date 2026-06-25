# Imports
import sys
import os
import math

# function to train model
def trainBigramLanguageModel(content):
    unigram_dict = dict()
    bigram_dict = dict()
    i = 0
    previous_char = ""
    # for each char in the file: 
    for char in content:
        # add to unigram dictionary
        if char not in unigram_dict:
            unigram_dict[char] = 0
        unigram_dict[char] += 1
        # add to bigram dictionary
        if previous_char:
            bigram = previous_char + char
            if bigram not in bigram_dict:
                bigram_dict[bigram] = 0
            bigram_dict[bigram] += 1
        previous_char = char
    return unigram_dict, bigram_dict 

# function to identify the language     
def identifyLanguage(content_test_line, languages_list, unigram_dict_list, bigram_dict_list):
    # set variables
    i = 0
    max_prob = -1
    likely_language = ""
    # iterate over each language (English, French, Italian)
    for language in languages_list:
        previous_char = ""
        prob_tot = 1
        # for each char in the file:
        for char in content_test_line:
            bigram = previous_char + char
            # calculate the conditional probability of the char and its previous one
            if bigram not in bigram_dict_list[i] and char not in unigram_dict_list[i]:
                prob = 1/(len(unigram_dict_list))
            elif bigram not in bigram_dict_list[i]:
                prob = 1/(unigram_dict_list[i][char]+len(unigram_dict_list))
            else:
                prob = (bigram_dict_list[i][bigram]+1)/(unigram_dict_list[i][char]+len(unigram_dict_list))          
            previous_char = char
            prob_tot = prob_tot * prob
        # select highest probability language
        if (prob_tot > max_prob):
            max_prob = prob_tot
            likely_language = language       
        i = i + 1
    return likely_language

# main
def main():
    # TODO: the command line should be of a form with training and test
    # and take these as input rather than hardcoding them here
    # TODO: Please assume the special token <start> at the beginning of each line. 
    # How do I implement this?
    # TODO: Ask how the file paths should be: should they be global or should
    # they be inputted entirely from the command line

    # sets os filepaths to current filepath
    file_path_training = os.getcwd() + "/languageIdentification.data/languageIdentification.data/training/"
    file_path_out = os.getcwd()
    file_path_test = os.getcwd() + "/languageIdentification.data/languageIdentification.data/test"
    # Steps to select appropriate language:
    # 1) open files to train the model
    likely_language = ""
    unigram_dict_list = list()
    bigram_dict_list = list()
    for filename in os.listdir(file_path_training):
        file_path = os.path.join(file_path_training, filename)
        with open(file_path, "r", encoding="ISO-8859-1") as file:
            content_training = file.read()
            unigram_dict = dict()
            bigram_dict = dict()
            # 2) train the model
            unigram_dict, bigram_dict = trainBigramLanguageModel(content_training)
            unigram_dict_list.append(unigram_dict)
            bigram_dict_list.append(bigram_dict)
    # 3) open files to test the model
    with open(file_path_test, "r", encoding="ISO-8859-1") as file:
        content_test = file.read()
    
    # 4) open file to output the results of the model
    count = 1
    content_test_lines = content_test.splitlines()
    output_file_path = os.path.join(file_path_out, 'languageIdentification.output')
    with open(output_file_path, 'w') as file:
        # 5) iterate over each line in the test
        for line in content_test_lines:
            if count > - 1:
                # 6) select most likely language for each line of the test
                likely_language = identifyLanguage(line, 
                                                ["English", "French", "Italian"],
                                                unigram_dict_list,
                                                bigram_dict_list,
                                                )
            # 7) output most likely language in output file
            file.write(str(count) + " " + likely_language + "\n")
            count = count + 1

# run main
main()