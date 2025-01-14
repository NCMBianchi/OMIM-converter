# OMIM converter

![banner]()

This streamline JavaScript tool can be added to any website or browser application very easily: it converts [Monarch Initiative](https://monarchinitiative.org)'s IDs for diseases, genes and phenotypes (i.e. respectively 'MONDO:', 'HGNC:' and 'HP:') to [OMIM](https://www.omim.org) IDs -and viceversa.

## How to use

### ```mapper.js``` tool

Once added to your .html configuration, it can accept either Monarch Initiative's IDs or OMIM IDs and convert them. It fetches corresponding IDs from mapping files `monarch-omim.json and `omim-monarch.json`.

![json_files]()

Both are necessary to avoid that when looking for OMIM IDs in the `monarch-omim.json` file, it iterates through each element taking a lot of time.

### `updateMapping.py` script

Mapping files can be generated -or updated by overwriting them- with the following prompts:
- ```python updateMapping.py``` for default functionality (ID mapping files only for diseases)
- ```python updateMapping.py --genes``` ID mapping files for diseases and genes
- ```python updateMapping.py --phenotypes``` ID mapping files for diseases and phenotypes
- ```python updateMapping.py --genes --phenotypes``` ID mapping files for diseases, genes and phenotypes
- ```python updateMapping.py --reverse``` for `omim-monarch.json` file creation based on `monarch-omim.json` mapping file

The ```--reverse``` command overrides any other function of the script, only generating the second mapping file. Otherwise, that file is generated automatically after ```monarch-omim.json```. Mappings are extrapolated using Monarch Initiative's V3 API.

Copies of both mapping files for diseases only are already provided in this repository, updated to January 13th 2025. IDs only for disease were downloaded so far as generating the mapping for [29.916 diseases](https://api-v3.monarchinitiative.org/v3/api/search?category=biolink:Disease&limit=100&offset=0) present on Monarch Initiative's database took 4h21min: downloading those also for [571.154 genes](https://api-v3.monarchinitiative.org/v3/api/search?category=biolink:Gene&limit=100&offset=0) and [151.521 phenotypes](https://api-v3.monarchinitiative.org/v3/api/search?category=biolink:PhenotypicFeature&limit=100&offset=0) might have take too long, and I didn't need them to test the tool. They still can be extrapolated fairly easily though, if run in the background.

### `test.html` as a testing webpage

You can check how the tool work after cloning the repository and running a local web server with Python: ```python -m http.server 8000``` which can then be accessed at `http://localhost:8000/test.html` from any web browser.

This very simple html configuration lacks any CSS embellishment, yet the JavaScript tools allows for any set of UI choices.