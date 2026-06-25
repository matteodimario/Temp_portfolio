# Eco-Search

A semantic search engine for clothing products, built from a web crawler and a fine-tuned MiniLM sentence transformer.

## Parts

- `crawler.py` — crawls seed URLs, matches positive/negative keywords, and saves results
- `Retrieval1.py` — Flask backend that encodes queries and returns ranked results
- `templates/index.html` + `static/app.js` — simple frontend
- `fine_tune_model.ipynb` — notebook for preprocessing and fine-tuning MiniLM
- `Project.ipynb` — older model experiments
- `seedURLs.txt`, `pos_keywords.txt`, `neg_keywords.txt` — crawler inputs

## Requirements

```bash
pip install -r requirements.txt
```

## Crawler

```bash
python crawler.py seedURLs.txt pos_keywords.txt neg_keywords.txt 10
```

Outputs:
- `output_pos.txt` — URLs with matched positive keywords
- `output_neg.txt` — URLs with matched negative keywords

The crawler stays within the domains of the seed URLs, skips non-HTML files, and checks `robots.txt`.

## Search engine

`Retrieval1.py` serves a Flask app. It needs a fine-tuned model and embeddings file to run:

```bash
python Retrieval1.py
```

> **Note:** `Retrieval1.py` expects `./fine_tuned_model` and `./website_embeddings.pt` in this folder. Those are not included because they are large model artifacts. The notebook `fine_tune_model.ipynb` shows how to build them from crawled data.

## Tests

```bash
python Retrieval_tests.py
```

