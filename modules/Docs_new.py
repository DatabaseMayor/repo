# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 14:09:36 2024

@author: 18451
"""

import math
import Taxonomy
from collections import Counter
import random


class Docs(object):
    def __init__(self, file_path=None, init_docs=None, sample=0):
        self.file_path = file_path
        self.docs = []
        self.docs_int = []
        self.int_dict = {}
        self.token_count = {}
        self.doc_count = 0
        if init_docs is not None:
            self.docs.extend(init_docs)
        if file_path is not None:
            with open(file_path, "r", encoding='utf-8') as f:
                index=0
                for line in f.readlines():
                    #OHSUMED and FISH
                    doc_raw = line.lower().strip().split(";")
                    #DBLP
                    #doc_raw = line.lower().strip().split(" ")

                    doc_int_raw = []
                    for token in doc_raw:
                        self.doc_count += 1
                        if token not in self.int_dict:
                            doc_int_raw.append(index)
                            self.int_dict[token] = index
                            self.token_count[index] = 0
                        else: 
                            doc_int_raw.append(self.int_dict[token])
                        self.token_count[self.int_dict[token]] += 1
                       
                        index = index + 1
                        
                    self.docs.append(doc_raw)
                    self.docs_int.append(doc_int_raw)
                        
    def find_extoken(self, taxonomy: Taxonomy):
        external_t = set()
        for doc in self.docs_int:
            for token in doc:
                if token not in taxonomy.node_dict.keys():
                    external_t.update(token)
        return external_t
        

    def chongfu(self):
        p = False
        tcount = {}
        for doc_id, doc in enumerate(self.docs_int):
           for value in Counter(doc).values() :
               if value > 1:
                   p = True
        if p == True:
            print(f"There are sets with duplicate elements")
        
    def sort_by_length(self, reverse=False):
        self.docs_int = sorted(self.docs_int,
                           key=lambda x: len(x),
                           reverse=reverse)

    def sort_by_frequency(self, reverse=False):
        self.docs_int = [
            sorted(doc,
                   key=lambda x: self.token_count[x],
                   reverse=reverse)
            for doc in self.docs_int
        ]

    def sort_by_similarity_nodes(self, taxonomy: Taxonomy, phi=0.1, reverse=False):
        if taxonomy.cached:
            self.docs_int = [
                sorted(doc,
                       key=lambda x: len(taxonomy.cache[x])
                       if x in taxonomy.cache else 0,
                       reverse=reverse)
                for doc in self.docs_int
            ]
        else:
            taxonomy.sim_node_cache(phi)
            self.docs_int = [
                sorted(doc,
                       key=lambda x: len(taxonomy.sim_node[x])
                       if x in taxonomy.node_dict else 0,
                       reverse=reverse)
                for doc in self.docs_int
            ]

    def split_docs(self, taxonomy: Taxonomy):
        for doc_id, doc in self.docs_int:
            doc_1 = [token for token in doc if token in taxonomy.node_dict]
            doc_2 = [token for token in doc if token not in taxonomy.node_dict]
            self.docs_int[doc_id] = (doc_1, doc_2)

    def clean_not_leaf(self, tax):
        for i in range(len(self.docs_int)):
            self.docs_int[i] = [e for e in self.docs_int[i] if e in tax.leaf]
        self.docs_int = [doc for doc in self.docs_int if len(doc) > 0]

    def clean_not_taxed(self, tax):
        for i in range(len(self.docs_int)):
            self.docs_int[i] = [e for e in self.docs_int[i] if e in tax.node_dict]
        self.docs_int = [doc for doc in self.docs_int if len(doc) > 0]

    def info(self):
        print(f'Docs len:{len(self.docs_int)}')
        print(f'Docs avg:{sum([len(d) for d in self.docs_int])/len(self.docs_int)}')
        print(f'Docs max:{max([len(doc) for doc in self.docs_int])}')
        print(f'Docs min:{min([len(doc) for doc in self.docs_int])}')
        print(f"element number{self.doc_count}")
        print(f"Number of independent elements{len(self.token_count.keys())}")


def doc_prefix(doc: list, threshold: float):
    return len(doc) - math.ceil(len(doc)*threshold) + 1