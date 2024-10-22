# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 14:23:46 2024

@author: 18451
"""

import math
import numpy as np
from Docs_new import Docs
from scipy.optimize import linear_sum_assignment


class TaxonomyNode(object):
    def __init__(self, parent, name, depth):
        self.name = name
        self.parent = parent
        self.depth = depth
        self.children = {}
        self.partition = None
        self.ap_index = []
        self.pt_index = []

    def clean(self):
        self.ap_index = []
        self.pt_index = []
        self.partition = None

    def add_child_by_path(self, path):
        c = self
        for p in path:
            c = c.add_child(p)
        return c


    def add_child(self, child_id):
        #
        if child_id in self.children:
            return self.children[child_id]
        else:
            self.children[child_id] = TaxonomyNode(self, None, self.depth+1)
            return self.children[child_id]

    def neighbours(self):
        neighbours = list()
        if self.name == 'Root':
            return neighbours
        if self.parent.name != 'Root':
            neighbours.append(self.parent)
        neighbours.extend(self.children.values())
        return neighbours

    def Node_Signature(self, phi):
        d = math.ceil(phi/(1-phi))
        if self.depth < d:
            return self.name
        else:
            backward_depth = self.depth - d 
            p = self
            for _ in range(backward_depth):
                p = p.parent
            return p.name
   

    def select_children(self, stop=1):
        if stop <= 0:
            return [self]
        result = [[self]]
        node_traced = set([self])
        for _ in range(stop):
            next_node = [
                child
                for node in result[-1]
                for child in node.children.values()
                if child not in node_traced
            ]
            node_traced.update(next_node)
            result.append(next_node)
            
        return [i for r in result for i in r]
    


    def select_jaccard_sim_node(self, phi):
        sim_node = set()
        di = self.depth * phi
        d = self.depth
        p = self
        while p.depth >= di:
            j = math.ceil((p.depth-phi*d)/phi)
            sim_node.update(p.select_children(stop=j))
            p = p.parent
        return list(sim_node)

    def bfs_nodes(self, phi, with_level=False):
        max_depth = math.ceil(
            (1.0-phi)/phi*self.depth
        )
        result = [[self]]
        node_traced = set([self])
        for _ in range(max_depth):
        
            next_node = [
                neighbour

                for node in result[-1]
                for neighbour in node.neighbours()
                if neighbour not in node_traced
            ]

            node_traced.update(next_node)
            result.append(next_node)
        if with_level:
            return result
        else: 
            return [i for r in result for i in r]


class Taxonomy(object):
    def __init__(self, docs,file_path):
        self.root = TaxonomyNode(None, "Root", 0)
        self.node_dict = {}
        self.node_path = {}
        
        self.cache = {}
        self.cached = False

        with open(file_path, "r", encoding='utf-8') as f:
            
            num=0
            not_docs = {}
            for line in f.readlines():
                #OHSUMED AND FISH
                tax_path, tax_name = line.strip().split("\t")
                #DBLP
                #tax_path, tax_name = line.strip().split(": ")
                tax_path = tuple(tax_path.strip().split("."))
                tax_name = tax_name.lower()
                
                if tax_name in docs.int_dict.keys():
                    uuid_tax_name = docs.int_dict[tax_name]
                else:
                    if tax_name not in not_docs:
                        num+=1
                        not_docs[tax_name] = len(docs.int_dict.keys()) + num
                        uuid_tax_name = len(docs.int_dict.keys()) + num
                    else:
                        uuid_tax_name = not_docs[tax_name]
        
                        
                child_node = self.root.add_child_by_path(tax_path)
                child_node.name = uuid_tax_name
                self.node_dict[uuid_tax_name] = child_node
                self.node_path[uuid_tax_name] = tax_path
            
        self.leaf = set()
        for nodename in self.node_dict:
            if len(self.node_dict[nodename].children) == 0:
                self.leaf.add(nodename)
        self.create_partition_info()


    def clean_all(self):
        self.cache = {}
        self.cached = False

        for node in self.node_dict.values():
            node.clean()


    def create_partition_info(self):
        for node in self.node_dict.values():
            p = node
            while p.parent.name != "Root":
                p = p.parent
            node.partition = p.name

    def sim_node_cache(self, phi):
        self.sim_node = {}
        for node_name, node in self.node_dict.items():
            self.sim_node[node_name] = set()
            for snode in node.bfs_nodes(phi):
                x_path = self.node_path[node_name]
                y_path = self.node_path[snode.name]
                overlap = 0.0
                for i in range(min(len(x_path), len(y_path))):
                    if x_path[i] == y_path[i]:
                        overlap += 1
                    else:
                        break
                if overlap/(len(x_path)+len(y_path)-overlap) >= phi:
                    self.sim_node[node_name].add(snode)


    def make_cache(self, tokens, phi):
            token_need_cached = set([tokens]) & set(self.node_dict)
            for x in token_need_cached:
                self.cache[x] = {}
                for y in self.node_dict[x].bfs_nodes(phi):
                    self.cache[x][y.name] = self.similarity(x, y.name)

    def similarity(self, x: str, y: str):
        
        if self.cached:
            if x in self.cache and y in self.cache[x]:
                return self.cache[x][y]
            elif y in self.cache and x in self.cache[y]:
                return self.cache[y][x]
            elif x == y:
                return 1
            else:
                return 0
        
        else:
            
            if x == y:
                return 1
            elif x not in self.node_path or y not in self.node_path:
                return 0
 
            x_path = self.node_path[x]
            y_path = self.node_path[y]
    
            overlap = 0.0
            for i in range(min(len(x_path), len(y_path))):
                
                if x_path[i] == y_path[i]:
                    overlap += 1
                else:
                    break
            
            return overlap/max(len(x_path), len(y_path))

    def get_sim_mat(self, doc_x, doc_y):
        if not doc_x:
            return [[]]
        mat = [
            [
                self.similarity(token_x, token_y)
                for token_y in doc_y
            ]
            for token_x in doc_x
        ]

        return mat


    def info(self):

        min_depth = math.inf
        max_depth = -1 * math.inf
        total_depth = 0.0
        total_leaf_count = 0

        min_fanout = math.inf
        max_fanout = -1 * math.inf
        total_fanout = 0.0
        total_fanout_count = 0
        total_node = len(self.node_dict)
        print(total_node)
        for node in self.node_dict:
            if len(self.node_dict[node].children) == 0:
                d = self.node_dict[node].depth
                if d < min_depth:
                    min_depth = d
                if d > max_depth:
                    max_depth = d
                total_depth += d
                total_leaf_count += 1
            else:
                f = len(self.node_dict[node].children)
                if f < min_fanout:
                    min_fanout = f
                if f > max_fanout:
                    max_fanout = f
                total_fanout += f
                total_fanout_count += 1
        print(
            f"┌────────────────────┬────────────────────┐\n" +
            f"│ Depth              │ Fanout             │\n" +
            f"├──────┬──────┬──────┼──────┬──────┬──────┤\n" +
            f"│  min │  avg │  max │  min │  avg │  max │\n" +
            f"├──────┼──────┼──────┼──────┼──────┼──────┤\n" +
            f"│{min_depth:6.1f}│{total_depth/total_leaf_count:6.1f}│{max_depth:6.1f}" +
            f"│{min_fanout:6.1f}│{total_fanout/total_fanout_count:6.1f}│{max_fanout:6.1f}│\n"
            f"└──────┴──────┴──────┴──────┴──────┴──────┘"
        )