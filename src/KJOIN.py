# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 10:14:00 2023

@author: 18451
"""

from Taxonomy_new import Taxonomy
from Docs_new import Docs
import math
import time
import numpy as np
from scipy.optimize import linear_sum_assignment


def KJoin(docs, tax, theta, phi):
    
    candidates_count = 0
    result = set()
    cou = 0
    h_len = 0
    node_signature_count = {}

    #element and signature
    Gs = np.array([
        np.array([
            np.array([tax.node_dict[token].Node_Signature(phi), token],
                     dtype=object)
            if token in tax.node_path.keys()
            else np.array([">UNKONWN<", token], dtype=object)
            for token in doc
        ], dtype=object)
        for doc in docs
    ], dtype=object)
    
    for node_signatures in Gs:
        for sign in set(node_signatures[:, 0]):
            if sign not in node_signature_count:
                node_signature_count[sign] = 0
            node_signature_count[sign] += 1
    
    #Signature frequency in ascending order
    Gs_ = np.array([
        np.array(sorted(
            doc,
            key=lambda x: node_signature_count[x[0]],
            reverse = False
        ), dtype=object)[:len(doc) - math.ceil(len(doc)*theta) + 1]
        for doc in Gs
    ], dtype=object)
    
    ii = {} #inverted index
    partition_index = {}
    start = time.time()
    for doc_id, doc in enumerate(docs):
        candidates = set()
        Gs_i = Gs_[doc_id][:, 0]
        for g in Gs_i:
            if g == ">UNKONWN<":
                continue
            if g in ii:
                candidates.update(ii[g])
            else:
                ii[g] = set()
            ii[g].add(doc_id)

        
        partition_index[doc_id] = {}
        for g in Gs[doc_id]:
            if g[0] not in partition_index[doc_id]:
                partition_index[doc_id][g[0]] = []
            partition_index[doc_id][g[0]].append(g[1])

        candidates_count += len(candidates)
        

        for ii_doc_id in candidates:
            if ii_doc_id == doc_id:
                continue
            ii_doc = docs[ii_doc_id]
            doc_partition = partition_index[doc_id]
            ii_doc_partition = partition_index[ii_doc_id]

            partition_sum = {}
            for k, v in doc_partition.items():
                if k not in partition_sum:
                    partition_sum[k] = (set(), set())
                partition_sum[k][0].update(v)
            for k, v in ii_doc_partition.items():
                if k not in partition_sum:
                    partition_sum[k] = (set(), set())
                partition_sum[k][1].update(v)
            
            ub = 0
            for key in partition_sum.keys():
                x = partition_sum[key][0]
                y = partition_sum[key][1]
                ub += len(x & y)
                
                p1 = sum(
                    [
                        tax.node_dict[token_x].depth /
                        (tax.node_dict[token_x].depth+1.0)
                        for token_x in x - y
                        if token_x in tax.node_dict
                    ]
                )
                
                p2 = sum(
                    [
                        tax.node_dict[token_y].depth /
                        (tax.node_dict[token_y].depth+1.0)
                        for token_y in y - x
                        if token_y in tax.node_dict
                    ]
                )
                ub += min(p1, p2)   
            
            T = (theta/(1.0+theta))*(len(doc)+len(ii_doc))
            if ub < T:
                continue
            
            h_len = h_len + len(docs[ii_doc_id])
            cou = cou +1
            sim_mat = np.array(tax.get_sim_mat(
                docs[doc_id],
                docs[ii_doc_id]
            ))
            row_in, col_in = linear_sum_assignment(-sim_mat)
            doc_sim = sim_mat[row_in, col_in].sum()
            doc_sim = doc_sim / (len(docs[doc_id]) + len(docs[ii_doc_id]) - doc_sim)
            if doc_sim >= theta:
                result.add((
                min(doc_id, ii_doc_id),
                max(doc_id, ii_doc_id)
            ))                        
    end = time.time()
    print("#"*30)
    print(
        f"KJOIN{end-start:10.3f} candidates{candidates_count:10} hungarian{cou} average length{h_len/cou} results{len(result):10} {theta} {phi}")

