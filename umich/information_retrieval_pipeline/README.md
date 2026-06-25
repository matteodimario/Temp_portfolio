# Information Retrieval Pipeline

Three standalone Python scripts for text processing, vector-space retrieval, and web ranking. They were written for a course using the Cranfield document collection, so some paths and evaluation code assume that dataset.

## 01_language_id

Text preprocessing: SGML removal, tokenization, and BPE encoding.

```bash
cd 01_language_id
python preprocess.py
```

Expects a `cranfieldDocs/` folder with `.sgml` files. A couple of sample files are included.

## 02_tf_idf

Vector-space retrieval with TF-IDF weighting, Porter stemming, and cosine similarity.

```bash
cd 02_tf_idf
python vectorspace.py <doc_weight> <query_weight> <cosine> <docs_dir> <queries_file>
```

Example:
```bash
python vectorspace.py tf.idf tf.idf 1 cranfieldDocs queries.txt
```

> This script also reads a relevance-judgements file for evaluation. If you don't have the Cranfield collection, you can still read the code to see the indexing and scoring logic.

## 03_crawler_pagerank

Web crawler and PageRank calculator.

**Crawler:**
```bash
cd 03_crawler_pagerank
python crawler.py <seed_file> <max_urls>
```

Example:
```bash
python crawler.py sample_urls.txt 10
```

Outputs `crawler.output` (URLs found) and `links.output` (source-target pairs).

**PageRank:**
```bash
python pagerank.py <urls_file> <links_file> <threshold>
```

Example:
```bash
python pagerank.py sample_urls.txt sample_links.txt 0.001
```

Outputs `pagerank.output` with ranked URLs.

## Key concepts

- Text preprocessing and tokenization
- TF-IDF vector space model
- Web crawling and graph traversal
- PageRank algorithm
