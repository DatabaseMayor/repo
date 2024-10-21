# SSC-Join

SSC-Join is based on a novel filtering and verification framework to efficiently recognize similar set pairs. In the filtering stage, we propose an element signature-based collection segmentation method, a signature prefix filtering strategy, and a syntactic-semantic co-differential filtering to remove a large number of dissimilar collection pairs. In the validation phase, semantically enhanced set validation strategies are proposed, which can enhance the effectiveness of set filtering based on the length of semantic subsets. Syntactic semantic collaborative filtering only utilizes the length information of the syntactic and semantic subsets of the set, which makes the filtering simple and efficient .

## Installation
- Clone the repository onto your local machine.
- Download anaconda4.10.1.

## Usage
>For SSC-Join
```bash
Give the path to docs and tax.
Initialize the Docs class and the Taxonomy class.
Use the Docs class method sort_by_length on Docs class objects for length ascension.
Run SSC-Join using Docs class object with docs_int, Taxonomy class object, set semantic similarity threshold, element semantic similarity threshold.
```
>For KJOIN
```bash
Same as SSC-Join.
```
>For AdaptJoin
```bash
Give the path to docs and tax.
Initialize the Docs class and the Taxonomy class.
Use Docs class method sort_by_length on Docs class objects for length descending.
Use the Docs class method sort_by_frequency for frequency descending on Docs class objects.
Run AdaptJoin using Docs class object with docs_int, Taxonomy class object, set semantic similarity threshold, and optimal parameter τ.
```
## data
1.fish_tax.txt  --Taxonomy1:FISH

2.fish_data_new2.txt  --dataset1:FISH

3.ohsumed_tax.txt  --Taxonomy2:MeSH

4.ohsumed_new.txt  --dataset2:OHSUMED

5.ohdsumed_new_10w.txt  --Small OHSUMED in comparison with state-of-the-art algorithms.

6.semantic_level_tree_new.txt  --Taxonomy3:DBLP

7.title_clean_new.txt  --dataset3:DBLP

8.title_clean_new_10w.txt  --Small DBLP in comparison with state-of-the-art algorithms.
