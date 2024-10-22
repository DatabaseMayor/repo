# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 09:32:25 2023

@author: 18451
"""

import time
import numpy as np
from Taxonomy_new import Taxonomy
from Docs_new import Docs
from collections import Counter
from scipy.optimize import linear_sum_assignment

 
def join(docs, tax, theta, tau):
    result = set()
    ii = {} # inverted index
    tau_count = {}
    phi = [] #Record the φ for each set
    sim_token = {} #Record the set of similar elements corresponding to each element
    skip = set() #The set corresponds to φ with numerator or denominator ≤ 0, and AdaptJoin cannot be applied.
    candidates_count = 0
    h_len = 0
    

    start = time.time()
    for doc_id, doc in enumerate(docs):
        if (len(doc) - tau + 1) <= 0:
            skip.add(doc_id)
            continue
        elif (theta*len(doc) - tau + 1) <= 0:
            skip.add(doc_id)
            continue
        tau_count = []
            
        nowphi = (theta * len(doc) - tau + 1) / (len(doc) - tau + 1)
        phi.append(nowphi)
        candidates = set()
        candidates_final = set()
       
        for token_id, token in enumerate(doc):
                if token not in sim_token:
                    sim_token[token] = []  
                    tax.make_cache(token,nowphi)
                    if token in tax.cache:
                        sim_token[token] = [
                            k
                            for k, v in tax.cache[token].items()
                            if v >= nowphi
                        ]
                    else:
                        sim_token[token] = [token]
                
                for token_s in sim_token[token]:
                    if token_s in ii:
                        for ii_doc_id in ii[token_s]:
                            if theta*len(docs[ii_doc_id]) >= len(docs[doc_id]):  
                                continue
                            candidates.add(ii_doc_id)
                for ii_id in candidates:
                        tau_count.append(ii_id)
                candidates = set()

        for token_id, token in enumerate(doc):
            if token not in ii:
                ii[token] = set()
            ii[token].add(doc_id)
                
        for key_id,id_value in Counter(tau_count).items():
            if id_value < tau:
                continue
            candidates_final.add(key_id)

        candidates_count += len(candidates_final)

        for ii_doc_id in candidates_final:
            if ii_doc_id == doc_id:
                continue
            h_len = h_len + len(docs[doc_id])
            sim_mat = np.array(tax.get_sim_mat(
                docs[doc_id],
                docs[ii_doc_id]
            ))
            row_in, col_in = linear_sum_assignment(-sim_mat)
            doc_sim = sim_mat[row_in, col_in].sum()
            doc_sim = doc_sim / (max(len(docs[doc_id]),len(docs[ii_doc_id])))
            if doc_sim >= theta:
                result.add((doc_id, ii_doc_id))

    for doc_id in skip:
        for doc_id11 in range(doc_id):
            candidates_count += 1
            h_len = h_len + len(docs[doc_id])
            sim_mat = np.array(tax.get_sim_mat(
                        docs[doc_id],
                        docs[doc_id11]
                    ))
            row_in, col_in = linear_sum_assignment(-sim_mat)
            doc_sim = sim_mat[row_in, col_in].sum()
            doc_sim = doc_sim / (max(len(docs[doc_id]),len(docs[doc_id11])))
            if doc_sim >= theta:
                result.add((doc_id, doc_id11)) 

    end = time.time()
    print('#########################################################')
    print(
        f"AdaptJoin theta:{theta:.2f} tau:{tau:.2f}\n" +
        f"candidates size:{candidates_count:10}\n"  +
        f"results sum:{len(result):5} time:{end-start:.2f}"+
        f"average length{h_len/candidates_count:10.3f}"
    )
    return result

