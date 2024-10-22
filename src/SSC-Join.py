# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 14:26:45 2024

@author: 18451
"""

#SSC+去增强协同差

#将结果2放到长度差修剪前，即将语义部分句法相似度单独在外面计算
from __future__ import division
from Taxonomy_new import Taxonomy
from Docs_new import Docs
import math
import time
import numpy as np
from scipy.optimize import linear_sum_assignment

def SSCJoin(docs, tax, theta, phi):
    
    node_signature_count = {} # Record signature frequency
    candidates_count = 0 # Record the number of candidates
    cou = 0 # Record the number of hungarian
    h_len = 0 
    result = set() 
    
    dphi = math.ceil(phi/(1-phi))

    # element and its signature
    Gs = np.array([
        np.array([
            np.array([tax.node_dict[token].Node_Signature(phi), token,0],
                     dtype=object)
            if token in tax.node_path.keys() and (tax.node_dict[token].Node_Signature(phi) != token or (tax.node_dict[token].Node_Signature(phi) == token and tax.node_dict[token].depth == dphi))
            else np.array([token, token,1], dtype=object)
            for token in doc
        ], dtype=object)
        for doc in docs
    ], dtype=object)
    

    for node_signatures in Gs:
        for sign in set(node_signatures[:, 0]):
            if sign not in node_signature_count:
                node_signature_count[sign] = 0
            node_signature_count[sign] += 1

    #In ascending order of signature
    Gs_ = np.array([
        np.array(sorted(
            doc,
            key=lambda x: node_signature_count[x[0]],
            reverse = False
        ), dtype=object)
        for doc in Gs
    ], dtype=object)
    
    #prefix
    Gs_p = np.array([
        np.array(sorted(
            doc,
            key=lambda x: node_signature_count[x[0]],
            reverse = False
        ), dtype=object)[:len(doc) - math.ceil(len(doc)*theta) + 1]
        for doc in Gs
    ], dtype=object)
    
    #syntactic subset
    docs1 = []
    for pairs in Gs_:
        doc_raw1 = []
        for pair in pairs:
            if pair[2] == 1:
                doc_raw1.append(pair[1])
        docs1.append(doc_raw1)
    
    #semantic subset
    docs0 = []
    for pairs in Gs_:
        doc_raw0 = []
        for pair in pairs:
            if pair[2] == 0:
                doc_raw0.append(pair[1])
        docs0.append(doc_raw0)   
    
    ii = {} #inverted index
    
    start = time.time()
    for doc_id, doc in enumerate(docs):
        candidates = set()
        #Take the signature prefix of the doc_idth set
        Gs_i = Gs_p[doc_id][:, 0]
        
        for g in Gs_i:
                if g in ii:
                    #Prefix Filtering
                    for id in ii[g]:
                        #Length Filtering
                        if len(docs[id]) < theta * len(doc):
                            continue

                        docs1_min = min(len(docs1[doc_id]),len(docs1[id]))
                        docs0_min = min(len(docs0[doc_id]),len(docs0[id]))
                        jc = abs(len(docs1[doc_id]) - len(docs1[id]))
                        yc = abs(len(docs0[doc_id]) - len(docs0[id]))
                        #CDF
                        if jc + yc > ((1.0 - theta)/theta)*(docs1_min + docs0_min):
                            continue
                        
                        candidates.add(id) 
                    ii[g].add(doc_id)
                else:
                    ii[g] = set()
                    ii[g].add(doc_id)          
        candidates_count += len(candidates)
        
        for doc_id11 in candidates:
            if doc_id11 == doc_id:
                continue
            al = (theta/(1.0+theta))*(len(docs[doc_id])+len(docs[doc_id11]))
            
            x = 0
            y = 0
            osyn = 0 #Syntax subset overlap
            flag = True
                
            while x < len(docs1[doc_id11]) and y < len(docs1[doc_id]):
                if osyn + min(len(docs1[doc_id11])-x,len(docs1[doc_id])-y)< al-min(len(docs0[doc_id11]),len(docs0[doc_id])):
                    flag = False
                    break
                if docs1[doc_id11][x] == docs1[doc_id][y]:
                    x = x + 1
                    y = y + 1
                    osyn = osyn + 1
                elif node_signature_count[docs1[doc_id11][x]] > node_signature_count[docs1[doc_id][y]]:
                    y = y + 1
                else:
                    x = x + 1
            
            while flag == True:
                cou = cou+1
                h_len = h_len + len(docs0[doc_id11])
                sim_mat = np.array(tax.get_sim_mat(
                    docs0[doc_id],
                    docs0[doc_id11]
                ))
                row_in, col_in = linear_sum_assignment(-sim_mat)
                doc_sim = sim_mat[row_in, col_in].sum()
                if doc_sim >= al - osyn:
                    result.add((doc_id, doc_id11))
                break
                
    end = time.time()
    print("#"*30)
    print(
        f"SSC{end-start:10.3f} candidates{candidates_count:10} hungarian{cou} average length{h_len/cou:10.3f} result{len(result):10} {theta} {phi}")

        

