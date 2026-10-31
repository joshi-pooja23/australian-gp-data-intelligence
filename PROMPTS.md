# AI Prompt Engineering Documentation
**Project:** Australian General Practitioner Data Intelligence Pipeline  
**Domain:** Healthcare / Web Scraping & Data Intelligence  

## System Prompt Architecture
> "You are an expert Healthcare AI Entity Extractor. Process unstructured scraped HTML snippets from Australian public health directories and output structured JSON records."

## Iterative Refinement Log
- **Iteration 1:** Extracted free-text fields. *Limitation:* Unstructured paragraphs made programmatic database ingestion fail.
- **Iteration 2:** Enforced strict schema matching with regex fallback rules for postal codes and state normalization, resulting in 100% database compatibility.