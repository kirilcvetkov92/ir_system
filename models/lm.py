'''
vanilla tf-idf cosine-similairty model
'''

import math
from collections import Counter, defaultdict

import scipy.sparse
import numpy as np 
from sklearn.preprocessing import normalize

from models.model_base import ModelBase


class LM(ModelBase):

	def __init__(self, index_dir_path, alpha):

		ModelBase.__init__(self, index_dir_path)

		self.name = "alpha-uni-lm"
		self.alpha = alpha

		# self.idf = self.get_all_idf()


	def find(self, query, top=1000, log0=-1000):

		# query is a string
		# return a list of tuple (entity, score)

		q_dict = self.query2index(query)
		# q_dict: {word_index: freq}

		word_indices = q_dict.keys()
		docs, corpus_prob = self.get_docs_by_word_id(word_indices)
		# docs: [(doc_id, {word_index: freq})]

		similarities = np.zeros((len(docs)))
		entities = []

		l = 0
		a = 0
		for n, (doc_id, doc) in enumerate(docs):

			for w_id, freq in q_dict.items():
				if w_id in doc:
					weight = (1 - self.alpha) * doc[w_id]  + self.alpha * corpus_prob[w_id]
				else:
					l += 1
					weight = self.alpha * corpus_prob[w_id]
				a += 1

				similarities[n] += np.log(weight) * q_dict[w_id]


			# for w_id, weight in doc.items():

			# 	similarities[n] += np.log((1 - self.alpha) * weight  + self.alpha * corpus_prob[w_id]) * q_dict[w_id]
			
			# other words: prob 0 -> add log0
			similarities[n] += (len(self.w2i) - len(doc)) * log0

			entities.append(self.i2e[doc_id])

		# doc_scores = [(entity, score) for entity, score in zip(entities, similarities)]

		# ranking
		# top_k = sorted(doc_scores, key=lambda x:x[1], reverse=True)[:top]
		top_k = sorted(zip(entities, similarities), key=lambda x:x[1], reverse=True)[:top]

		return top_k


	# def get_all_idf(self):

	# 	# get all document frequency
	# 	# return: {word_index: freq}

	# 	cmd = "SELECT w_id, weight FROM idf"
	# 	r = self.db.execute(cmd).fetchall()

	# 	return {k:v for k, v in r}


	def get_docs_by_word_id(self, word_id):

		# get document contain given a list of word indices
		# NOTICE: only get the frequency of given word index in each document, for fast computation

		# input: int or [int]
		# return: [(doc_id, {term: freq}, sq2)]


		word_id = [str(w) for w in word_id]

		cmd = "SELECT doc_id, w_id, prob FROM doc_word WHERE w_id IN ({})".format(", ".join(word_id))
		# cmd = "SELECT doc_id, w_id, freq FROM word_doc WHERE doc_id IN (SELECT doc_id FROM doc_word WHERE w_id in ({}))".format(", ".join(word_id))
		# cmd = "SELECT doc_id,"
		
		r = self.db.execute(cmd).fetchall()

		docs = defaultdict(dict)

		for doc_id, w_id, weight in r:

			docs[doc_id][w_id] = weight

		cmd = "SELECT w_id, prob FROM corpus_prob WHERE w_id IN ({})".format(", ".join(word_id))
		
		r = self.db.execute(cmd).fetchall()

		corpus_prob = defaultdict(float)
		for w_id, prob in r:
			corpus_prob[w_id] = prob


		return docs.items(), corpus_prob

















