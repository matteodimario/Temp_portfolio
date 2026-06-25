import ahocorasick

# List of keywords to match
keywords = ["machine learning", "deep learning", "neural network", "AI"]

# 1️⃣ Build the Aho-Corasick Trie
A = ahocorasick.Automaton()
for keyword in keywords:
    A.add_word(keyword, keyword)  # Store keyword as the output
A.make_automaton()

# 2️⃣ Search for Keywords in a Text
text = "This paper discusses deep learning and neural networks."

found_keywords = set()
for _, found_word in A.iter(text):
    found_keywords.add(found_word)

print(f"Keywords Found: {found_keywords}")
