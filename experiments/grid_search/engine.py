from multiprocessing import Manager, Pool
import os
import pickle
import random
from sets import Set
import sys
from time import clock
from traceback import print_exception

# from resources.resource_builder import *
# from models.adapters import GensimLdamodel
# from gensim_mod.models.ldamodel import LdaModel as LdaModel_mod
# from models.interfaces import TopicModel

class PerplexityEval():
    def __init__(self, documents):
        self.docs = documents

    def __str__(self): return 'perplexity'

    def __call__(self, model): pass
        # if not isinstance(model, (TopicModel, LdaModel_mod)): raise TypeError
        # if isinstance(model, TopicModel): return model.perplexity(self.docs)
        # else: return GensimLdamodel(model).perplexity(self.docs)


class CoherenceEval(): pass
    # def __init__(self, docs, M = 20):
    #     self.docs = docs
    #     self.M = M
    #     self.buildWordToDocMap()
    #
    # def __str__(self): return 'coherence'
    #
    # def __call__(self, model):
    #     if not isinstance(model, (TopicModel, LdaModel_mod)): raise TypeError
    #     if isinstance(model, LdaModel_mod):
    #         model = GensimLdamodel(model)
    #     coh = 0.0; T = len(model.topic_indices())
    #     for i in model.topic_indices() :
    #         topind = model.top_word_indices(i, self.M)
    #         c = 0; pairs = 0
    #         for j in range(len(topind))[1:] :
    #             for k in range(len(topind))[:j] :
    #                 wj = topind[j]; wk = topind[k]
    #                 if wk in self.w2doc and wj in self.w2doc:
    #                     denom = float(len(self.w2doc[wk]))
    #                     nom = len(self.w2doc[wj].intersection(self.w2doc[wk]))
    #                     c += np.log((nom+1)/denom)
    #                     pairs += 1
    #         c /= pairs # average over (j,k) word pairs
    #         coh += c
    #     coh /= T # average over topics
    #     return coh
    #
    #
    #
    # def buildWordToDocMap(self):
    #     'build word index -> containing document set  map for bow corpus'
    #     self.w2doc = {}
    #     for di, doc in enumerate(self.docs):
    #         for wi, _ in doc:
    #             if not wi in self.w2doc: self.w2doc[wi] = Set()
    #             self.w2doc[wi].add(di)
    #
