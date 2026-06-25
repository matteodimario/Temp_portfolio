# Author

### imports
import sys
import os
import re
from collections import Counter, defaultdict
import math

stop_words = [
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", 
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", 
    "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
    "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", 
    "for", "with", "about", "against", "between", "into", "through", "during", "before", 
    "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", 
    "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", 
    "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", 
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", 
    "just", "don", "should", "now"]

contractions = {
        "I’m": "I am", "you’re": "you are", "he’s": "he is",
        "she’s": "she is", "it’s": "it is", "we’re": "we are",
        "they’re": "they are", "can’t": "cannot", "won’t": "will not",
        "didn’t": "did not", "Sunday’s": "Sunday 's"
    }

def removeSGML(content):
    i = 0
    cleaned_content = ""
    inside_tag = False
    # iterate over each char to remove the SGML given the <...> pattern
    for char in content:
        # print(token)
        if char == "<":
            inside_tag = True
        if char == ">":
            inside_tag = False
        elif not inside_tag:
            cleaned_content += char
    cleaned_content = cleaned_content.strip()
    return cleaned_content

def tokenizeText(content):
    ## cases handled:
    # 1) contractions
    for contraction, expansion in contractions.items():
        content = content.replace(contraction, expansion)
    # 2) tokenization of possessive 's
    content = re.sub(r"(\w)'s", r"\1 's", content)
    # 3) tokenization of dates
    content = re.sub(r"(\d{1,2}/\d{1,2}/\d{2,4})", r" \1 ", content)
    # 4) tokenization of -
    content = re.sub(r"(\w+-\w+(-\w+)?)", r" \1 ", content)
    # 5) tokenization of punctuation . ,
    content = re.sub(r"(?<!\d)\.(?!\d)|,|;", r" ", content)  # Periods outside numbers
    content = re.sub(r"([!?()\"'])", r" \1 ", content)       # Standalone punctuation
    # 6) tokenization of acronyms
    content = re.sub(r"\b(\w(?:\.\w)+)\b", r" \1 ", content)
    # 7) tokenization of whitespace
    content = re.sub(r"\s+", " ", content).strip()
    ## Split the text into a list of tokens
    return content.split()

class PorterStemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a token to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for token to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases token length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]

### a. function that adds a document to the inverted index
def indexDocument(document_id, weighting_scheme_docs, weighting_scheme_query, inverted_index, content):
    p = PorterStemmer()
    frequencies_list = {}
    ## - preprocess the content provided as input
    # remove SGML
    content = removeSGML(content)
    # tokenize text
    tokens = tokenizeText(content)
    # set-up some variables
    token = ''
    max_freq = max(Counter(tokens).values())
    document_id = str(document_id)
    document_id = re.search(r'(\d+)$', document_id)
    document_id = str(int(document_id.group(1)))
    # iterate through all the tokens
    for token in tokens:
        # stem tokens
        output = ''
        output += p.stem(token, 0,len(token)-1)
        # count and store the frequencies of each token in the document 
        if output not in frequencies_list:
            frequencies_list[output] = 0        
        frequencies_list[output] += 1
        token = ''
    ## add the tokens to the inverted index provided as input
    for token in frequencies_list:
        # calculate tf
        tf = frequencies_list[token]
        # add weighting value of each token for the document to the inverted index
        if (weighting_scheme_docs == 'tf.idf'): # if the weighting scheme is tf.idf
            inverted_index[document_id][token] = tf # add tf to inverted index
        if (weighting_scheme_docs == 'n.p'): # if the weighting scheme is n.idf
            inverted_index[document_id][token] = tf / max_freq # add normalized tf to inverted index
    # return
    return inverted_index

### b. function that retrieves information from the index for a given query
def retrieveDocuments(query, inverted_index, weighting_scheme_docs, weighting_scheme_query, cosine_similarity):
    p = PorterStemmer()
    frequencies_list = {}
    retrieved_docs = defaultdict()
    ## - preprocess the query
    # remove SGML
    query = removeSGML(query)
    # tokenize text
    tokens = tokenizeText(query)
    # maximum frequency for weights calculations
    max_freq = max(Counter(tokens).values())
    # store frequencies of the tokens in the query
    for token in tokens:
        # stem tokens
        output = ''
        output += p.stem(token, 0,len(token)-1)
        # count and store the frequencies of each token in the query
        if output not in frequencies_list:
            frequencies_list[output] = 0        
        frequencies_list[output] += 1
        token = ''
    # loop through each token in the query
    for token in frequencies_list:
        # calculate idf for query
        df = sum(1 for doc in inverted_index if token in inverted_index[doc])
        idf = math.log(1400 / (df + 1)) # +1 for smoothing
        p = math.log((1400 - df)/ (df + 1))
        # calculate weight
        if (weighting_scheme_query == 'tf.idf'): # for tf:
            tf = frequencies_list[token] # calculate tf
            frequencies_list[token] = tf * idf # add tf.idf to query index
        if (weighting_scheme_query == 'n.p'): # for n:
            n = frequencies_list[token] / max_freq # calculate normalized tf
            frequencies_list[token] = n * p # add n.idf to query index
    # loop through pair(document, tf) in the inverted index
    for document in inverted_index.items():
        ## - determine the set of documents from the inverted index that include at least one token from the query
        common_terms = set(frequencies_list.keys()).intersection(document[1].keys())
        # exclude stop words
        common_terms = common_terms - set(stop_words)
        ## - calculate the similarity between the query and each of the documents in this set
        df = sum(1 for doc in inverted_index if token in inverted_index[doc])
        idf = math.log(1400 / (df + 1)) # +1 for smoothing
        similarity = 0
        # calcuate similarity
        if (cosine_similarity == '0'): # without cosine similarity
            similarity = sum(frequencies_list[term] * (document[1][term] * idf) for term in common_terms)
        if (cosine_similarity == '1'): # with cosine similarity
            similarity = sum(frequencies_list[term] * (document[1][term] * idf) for term in common_terms)
            query_norm = math.sqrt(sum((frequencies_list[term] * idf) ** 2 for term in frequencies_list))
            doc_norm = math.sqrt(sum((document[1][term] * idf) ** 2 for term in document[1]))
            similarity = similarity / (query_norm * doc_norm)
        # add similarity to retrieved docs dictionary
        if (similarity != 0):
            retrieved_docs[document[0]] = similarity
    # return
    return retrieved_docs

# helper function to produce outputs in vectorspace.output
def produce_outputs(retrieved_docs, query, macro_averages, output_path):
    # setting file path for output, answers, and comparisons
    answers_path = '../Assignment2/cranfield.reljudge'
    my_answers_path = '../Assignment2/vectorspace.answers'
    # initializing variables
    count = 0
    output_answers = set()
    correct_answers = set()
    # reformat query
    query = re.match(r'\d+', query)
    query = query.group(0)
    # open cranfield.relijudge file
    with open(answers_path, "r", encoding="ISO-8859-1") as file:
        # store all relevant docs for later comparison
        for line in file.readlines():
            words = line.split()
            if (words[0] == query):
                correct_answers.add(str(words[1]))
    # open vectorspace.otuput file
    with open(output_path, "a", encoding="ISO-8859-1") as file_output:
        # open vectorspace.answers file
        with open(my_answers_path, "a", encoding="ISO-8859-1") as file_answers: 
            # iterate through ([doc_number], similarity) for each document in ranked order
            for pair in retrieved_docs:
                document = pair[0]
                # write to vectorspace.output file the query, the document number, and the similarity
                file_output.write(f"{query} {document} {pair[1]}\n")
                # keep track of documents otuputted
                output_answers.add(str(document))
                count = count + 1
                ## - macro-averaged precison and recall calculations
                if (count == 10 or count == 50 or count == 100 or count == 500):
                    # calculate true positives
                    TP = sum(1 for x in correct_answers if x in output_answers)
                    # calculate false negatives
                    FN = len(correct_answers) - TP
                    # calculate precision
                    precision = TP / count
                    # calculate recall
                    recall = TP / (TP + FN)
                    # store precision and recall to calculate averages
                    macro_averages[count][query] = (precision, recall)
    # return      
    return macro_averages

### c. function main
def main():
    ## Design Decisions:
    # NOTE: Instead of only passing in the document_id for indexDocument, 
    # I also pass in the content so that I only open the file in the function
    # NOTE: I decided to add a list of stop words to limit the files that are returned,
    # since many files had just some stop words in common and I thought it was better to 
    # not include those in the list. If interested in maintaining the stop words it is possible
    # it is possible by removing the stop_words list at the top and the two places where it is called
    # NOTE: Currently the command line supports tf.idf and n.p as weighting schemes
    # as well as 0 or 1 for cosine similarity

    ## set-up
    # read in the command line
    weighting_scheme_docs = sys.argv[1]
    weighting_scheme_query = sys.argv[2]
    cosine_similarity = sys.argv[3]
    # create output file
    output_path = str(f'../Assignment2/cranfield.{weighting_scheme_docs}.{weighting_scheme_query}.{cosine_similarity}.output')
    if not output_path.endswith('.txt'):
        output_path += '.txt'
    # setting query file path
    file_queries = '../Assignment2/' + sys.argv[5]
    # setting docs directory path
    files_directory_docs = '../Assignment2/' + sys.argv[4]
    files_directory_docs = os.path.abspath(files_directory_docs)
    # clearing output files
    with open(output_path, "w", encoding="ISO-8859-1")as file:
        pass
        file.write("Author\n")
    # initializing variables
    count = 0
    content = ""
    inverted_index = defaultdict(dict)
    macro_averages = defaultdict(dict)
    num_queries = 225
    num_docs = 1400
    ## i. open the folder containing the data collection
    doc_files = sorted(os.listdir(files_directory_docs))
    for doc_path in doc_files:       
        file_path = os.path.join(files_directory_docs, doc_path)
        # only for testing ----------
        # if (count == 1):
        #     break
        # count = count + 1
        # ---------------------------
        ## ii. for each file, obtain the content of the file, and add it to the index
        with open(file_path, "r", encoding="ISO-8859-1") as file:
            document_id = (os.path.basename(file_path))
            content = file.read()
            # add to index with indexDocument
            inverted_index = indexDocument(document_id, weighting_scheme_docs, 
                                                       weighting_scheme_query, inverted_index, content)
    ## iv. open the file with queries, and read one query at a time from this file
    with open(file_queries, "r", encoding="ISO-8859-1") as file:
        # for each query (which is one line)
        for query in file.readlines():
            # only for testing ----------
            # if (count == 224):
            #     break
            count = count + 1
            print(count)
            # ---------------------------
            ## v. for each query, find the list of documents that are relevant, along with their similarity scores
            retrieved_docs = retrieveDocuments(query, inverted_index, weighting_scheme_docs, 
                                               weighting_scheme_query, cosine_similarity)
            # sort retrieved docs according to highest similarity   
            retrieved_docs = sorted(retrieved_docs.items(), key=lambda item: item[1], reverse = True) 
            # NOTE: new format of retrieved_docs: list of pairs (doc_number, similarity) sorted by highest similarity
            # produce outputs in vectorspace.answers and vectorspace.output
            produce_outputs(retrieved_docs, query, macro_averages, output_path)
    ## produce averages for vectorspace.answers
    rankings_num = [10,50,100,500]
    for i in rankings_num:
        average_precision = 0
        average_recall = 0
        for pair in macro_averages[i].values():
            average_precision += pair[0]
            average_recall += pair[1]
        print(f"Top {i} rankings - precision: {average_precision/num_queries}, recall: {average_recall/num_queries}")

# run main
main()