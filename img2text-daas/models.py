import numpy as np

class VectorModel(object):
	def transform(self, obj): 
		raise Exception("Abstract Class")



from decaf.scripts.imagenet import DecafNet
class DecafModel(VectorModel):
	def __init__(self, decaf_folder = None):
		if decaf_folder == None:
			decaf_folder = "vecmodels/decaf"
		weight_file = "%s/imagenet.decafnet.epoch90" % decaf_folder
		meta_file = "%s/imagenet.decafnet.meta" % decaf_folder
		self.model = DecafNet(weight_file, meta_file)
		self.feature_layer = 'fc7_cudanet_out'
	def transform(self, img):
		self.model.classify(img.astype('uint8'), center_only = True)
		vec = self.model.feature(self.feature_layer).flatten()
		return vec

from gensim.models import Word2Vec
class Word2VecModel(VectorModel):
	def __init__(self, model_file = None):
		if model_file is None:
			model_file = "vecmodels/word2vec.bin"
		self.model = Word2Vec.load_word2vec_format(model_file, binary = True)
	def transform(self, word):
		return self.model[word]

import cPickle
class Image2WordModel(VectorModel):
	def __init__(self, img2txt_file = None):
		if img2txt_file == None: 
			img2txt_file = "vecmodels/img2txt.pkl"
		self.model = cPickle.load(open(img2txt_file, "r"))
	def transform(self, imgvec):
		return self.model(imgvec)

from sklearn.manifold import TSNE
class EmbeddingModel(VectorModel):
	def __init__(self, dim = None, **kwargs):
		if dim is None: dim = 2
		self.tsne = TSNE(n_components = dim, learning_rate = 5, perplexity = 20, verbose=1, early_exaggeration = 10.0)
	def transform(self, X, perplexity):
		self.tsne.set_params(perplexity = perplexity)
		print self.tsne.get_params()
		XX = self.tsne.fit_transform(X)
		return XX
