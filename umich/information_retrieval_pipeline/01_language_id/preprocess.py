# Imports
import sys
import os
import re

# read in from command line
cmd_line = sys.argv
print(cmd_line)

# function to remove SGML
# TODO: Add <start> at the beginning of each line
def removeSGML(content):
    # print(0)
    i = 0
    cleaned_content = ""
    inside_tag = False
    for char in content:
        # print(word)
        if char == "<":
            inside_tag = True
        if char == ">":
            inside_tag = False
        elif not inside_tag:
            cleaned_content += char
    cleaned_content = cleaned_content.strip()
    return cleaned_content

# function to tokenize text
# TODO: to complete the rules for tokenization
def tokenizeText(content):
    # tokens = []
    # token = ""
    # for char in content:
    #     word = ""
    #     if char != " ":
    #         token += char
    #     else:
    #         tokens.append(token)
    #         token = ""
    # return tokens
    # Expand contractions (e.g., "I’m" -> "I am", "Sunday’s" -> "Sunday 's")
    contractions = {
        "I’m": "I am", "you’re": "you are", "he’s": "he is",
        "she’s": "she is", "it’s": "it is", "we’re": "we are",
        "they’re": "they are", "can’t": "cannot", "won’t": "will not",
        "didn’t": "did not", "Sunday’s": "Sunday 's"
    }
    for contraction, expansion in contractions.items():
        content = content.replace(contraction, expansion)

    # Separate possessives ('s) from words
    content = re.sub(r"(\w)'s", r"\1 's", content)

    # Ensure dates remain intact (e.g., "01/22/2021")
    content = re.sub(r"(\d{1,2}/\d{1,2}/\d{2,4})", r" \1 ", content)

    # Handle hyphenated words or phrases (e.g., "father-in-law")
    content = re.sub(r"(\w+-\w+(-\w+)?)", r" \1 ", content)

    # Tokenize punctuation, excluding those in numbers
    content = re.sub(r"(?<!\d)\.(?!\d)|,|;", r" ", content)  # Periods outside numbers
    content = re.sub(r"([!?()\"'])", r" \1 ", content)       # Standalone punctuation

    # Preserve acronyms and abbreviations (e.g., "U.S.A.")
    content = re.sub(r"\b(\w(?:\.\w)+)\b", r" \1 ", content)

    # Normalize whitespace
    content = re.sub(r"\s+", " ", content).strip()

    # Split the text into a list of tokens
    return content.split()

# function to perform BPE encoding  
# TODO: to finish    
def BPE(tokens, vocabSize):
    print(0)
    BPE_tokens_list = []
    BPE_tokens_dict = dict()
    for token in tokens:
        BPE_tokens_list.append(token)
        if token not in BPE_tokens_dict:
            BPE_tokens_dict[token] = 0 
        BPE_tokens_dict[token] += 1
    while (len(BPE_tokens_list) < vocabSize):
        prev_token = ""
        for token in tokens:
            cur_token = token
            if prev_token+cur_token not in BPE_tokens_dict:
                BPE_tokens_dict[prev_token+cur_token]
            BPE_tokens_dict[prev_token+cur_token] += 1
            token_to_add = max(BPE_tokens_dict.values())
            BPE_tokens_list.append(token_to_add)
    # BPE_tokens = list(set(BPE_tokens_list))
    print(BPE_tokens_list)
    return BPE_tokens_list


# main
def main():
    files_directory = os.getcwd() + "/cranfieldDocs/"
    # print(files_directory)
    count = 0
    content = ""
    final_content = ""
    # TODO: to make variable for vocabSize (currently hard-coded)
    vocabSize = 100
    for filename in os.listdir(files_directory):
        # open file
        file_path = os.path.join(files_directory, filename)
        # print(file_path)
        # remove SGML

        if (count == 2):
            return
        count = count + 1
        # with open(current_directory)
        with open(file_path, "r") as file:
            content = file.read()
            # print(content)
            content = removeSGML(content)
            # print(content)
            tokens = tokenizeText(content)
            # print(tokens, vocabSize)
            BPE(tokens, vocabSize)



main()