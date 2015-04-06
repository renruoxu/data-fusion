import flask
from werkzeug.utils import secure_filename

from glob import glob
import os
import re
import numpy as np
import json

import models

## remember to start ipcluster in the folder
from IPython import parallel
client = parallel.Client()
dv = client[:]
lb_view = client.load_balanced_view()
print "running %d cores ..." % len(dv)

## load models
decaf = models.DecafModel()
img2word = models.Image2WordModel()
word2vec = models.Word2VecModel()
embedder = models.EmbeddingModel()
dv.push({"decaf": decaf, "img2word": img2word}, block = True, )

IMG_DIR = "static/data/images"
TXT_DIR = "static/data/texts"
IMG_EXT = ["png", "jpeg", "jpg", "bmp"]
TXT_EXT = ["txt"]

app = flask.Flask("img2vec-daas")

print 'server is running'


#-----------------------custom error handlers-------------------------------#
class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

@app.route("/")
def index():
    texts = "|".join(find_words())
    images = "\t".join(find_images())
    return """
    texts: %s <br />
    images: %s
    """ % (texts, images)

@app.route("/upload", methods=["POST"])
def upload_file():
    print "image uploaded ...."
    uploaded_files = flask.request.files.getlist('file')
    print uploaded_files

    #remove all files in IMG_DIR and TXT_DIR
    for d in [IMG_DIR, TXT_DIR]:
        files = glob("%s/*" % d)
        for f in files:
            os.remove(f)

    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        if filename.split('.')[-1] in IMG_EXT:
            uploaded_file_path = os.path.join(IMG_DIR, filename)
        elif filename.split('.')[-1] in TXT_EXT:
            uploaded_file_path = os.path.join(TXT_DIR, filename)
        else:
            raise InvalidAPIUsage("File type .%s not supported" %filename.split('.')[-1], status_code = 400)  

        try:
            #save file to disk
            print uploaded_file_path
            uploaded_file.save(uploaded_file_path)

        except Exception, e:
            err_msg = "Image %s already exists" %filename
            raise InvalidAPIUsage(err_msg, status_code = 400)
         
    return plot()

@app.route("/img2txt")
def temp():
    return flask.render_template('plot.html')

@app.route("/plot")
def plot():
    """plot images and texts in data folder"""
    if flask.request.args.get('perplexity'):
        perplexity = int(flask.request.args.get('perplexity'))
        print "debug: perplexity is set to be %i" %perplexity
    else:
        perplexity = 10

    img_files = find_images()
    imgvecs = np.array(lb_view.map_sync(img2vec, img_files))
    words = find_words()
    wordvecs = np.array([word2vec.transform(word) for word in words])
    print imgvecs.shape, wordvecs.shape
    xys = embedder.transform(np.append(imgvecs, wordvecs, axis = 0), perplexity)
    nimages = len(img_files)
    img_urls = [flask.url_for('static', filename='data/images/'+ img_file) for img_file in os.listdir(IMG_DIR)]
    result = {
         'images': [{'xy': tuple(xy), 'url': url} for xy, url in zip(xys[:nimages, :], img_urls)]
        , 'texts': [{'xy': tuple(xy), 'label': text, 'text': text} for xy, text in zip(xys[nimages:, :], words)]
    }
    #debug_plot(result)
    return flask.jsonify(result)

def find_images():
    img_files = glob("%s/*" % IMG_DIR)
    return map(os.path.abspath, img_files)

def find_words():
    text_files = glob("%s/*" % TXT_DIR)
    content = "\n".join(map(lambda f: open(f).read(), text_files))
    pat_word = re.compile("\w+")
    print pat_word.findall(content)
    return pat_word.findall(content)

def img2vec(imgfile):
    import matplotlib.pyplot as plt
    import models
    img = plt.imread(imgfile)
    vec = img2word.transform(decaf.transform(img))
    return vec


if __name__ == "__main__":
    app.debug = False
    app.run(port = 5001)
