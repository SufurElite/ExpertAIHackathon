from flask import Flask, request
import os, re, io
from werkzeug.utils import secure_filename
from google.cloud import vision
from google.cloud import storage
import numpy as np
import ghostPredict
from PIL import Image, ImageFilter, ImageOps
from expertai.nlapi.cloud.client import ExpertAiClient

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
# Set environment variables
os.environ['EAI_USERNAME'] = ''
os.environ['EAI_PASSWORD'] = ''

class Message:
    def __init__(self, top, bottom, left, right, isUser, text, overallSentiment, positiveSentiment, negativeSentiment):
       self.top = top
       self.bottom = bottom
       self.left = left
       self.right = right
       self.isUser = isUser
       self.text = text
       self.overallSentiment = overallSentiment
       self.positiveSentiment = positiveSentiment
       self.negativeSentiment = negativeSentiment
    def getCoords(self):
        return(self.top, self.bottom, self.left, self.right)
    def setText(self, text):
        self.text = text
    def getText(self):
        return self.text
    def isUser(self):
        return self.isUser
    def getOverallSentiment(self):
        return self.overallSentiment
    def getSentimentAsText(self):
        return "Overall sentiment: "+str(self.overallSentiment)#+", positivity: " + str(self.positiveSentiment)+", negativity: " + str(self.negativeSentiment) 

@app.route('/')
def hello():
    """Default/Root Return a friendly HTTP greeting."""
    return 'Hello World!'

def getMessages(imageArray, orig, cutoffMargin, inwardMargin, rightwardMargin):
    # Find X,Y coordinates of all user pixels
    userY, userX = np.where(np.all(imageArray==[33,185,252],axis=2))
    if len(userX)==0:
        return []   
    userLeft = min(userX)
    userRight = max(userX)

    matchY, matchX = np.where(np.all(imageArray==[229,229,229],axis=2))
    matchLeft = min(matchX)
    matchRight = max(matchX)

    absoluteBottom = max(len(userY),len(matchY))
    conversation = []
    
    top = userY[0]
    bottom = userY[0]
    userInd = 0
    matchInd = 0
    visionClient = vision.ImageAnnotatorClient()
    
    while userInd+1<absoluteBottom or matchInd+1<absoluteBottom:
        if matchInd<len(matchY)-1 and userInd<len(userY)-1:
            #print(matchInd, userInd)
            #print(matchY[matchInd],userY[userInd])
            if matchY[matchInd]>userY[userInd]:
                isUser = True
            else: 
                isUser = False
        elif matchInd<len(matchY)-1:
            #print("Set Match as no more Users")
            isUser = False
        elif userInd<len(userY)-1:
            #print("Set User as no more Match")
            isUser = True
        else: 
            break
        if isUser:
            top = userY[userInd]
            bottom = userY[userInd]
            left = userLeft
            right = userRight
            while userY[userInd]<=bottom+1:
                #print(userInd, userY[userInd])
                bottom = userY[userInd]
                userInd+=1
                if userInd>len(userY)-1:
                    break
        else:
            top = matchY[matchInd]
            bottom = matchY[matchInd]
            left = matchLeft
            right = matchRight
            while matchY[matchInd]<=bottom+1:
                bottom = matchY[matchInd]
                matchInd+=1
                if matchInd>len(matchY)-1:
                    break
        if top!=bottom and bottom-top>cutoffMargin:
            # Extract Region of Interest from unblurred original
            if not isUser:
                left+=inwardMargin
                right-=rightwardMargin
            ROI = orig[top:bottom, left:right]
            if isUser:
                userInd+=1
            else:
                matchInd+=1
            
            im = Image.fromarray(ROI)
            # Convert the Array of Integers to bytes
            # then to the cloud vision array 
            # and then finally retrieve the text
            imgByteArr = io.BytesIO()
            im.save(imgByteArr, format='PNG')
            imgByteArr = imgByteArr.getvalue()
            image = vision.Image(content=imgByteArr)

            response = visionClient.document_text_detection(image=image)
            text = response.full_text_annotation.text
            
            conversation.append(Message(top, bottom, left, right, isUser, text, 0, 0, 0))
    return conversation

@app.route('/getImageText/<path>')
def loadImageText(path):
    gcs_source_uri = "gs://chadvice.appspot.com/images/"+path
    
    storage_client = storage.Client()
    
    match = re.match(r'gs://([^/]+)/(.+)', gcs_source_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)
    print("bucket_name : ",bucket_name)
    print("prefix : ",prefix)
    bucket = storage_client.get_bucket(bucket_name)
    # List objects with the given prefix.
    blob_list = list(bucket.list_blobs(prefix=prefix))
    
    print('Output files:')
    files = []
    for blob in blob_list:
        files.append(blob)
    blob = files[0]
    print(blob.name) 
    print("downloading picture")
    blobString = blob.download_as_string()
    blobBytes = io.BytesIO(blobString)
    im = Image.open(blobBytes)
    im = Image.open(blobBytes).convert('RGB')
    na = np.array(im)
    orig = na.copy()    # Save original
    imageWidth = im.size[0]
    imageHeight = im.size[1]
    cutoffMargin = .02*imageHeight
    inwardMargin = int(.12*imageWidth)
    rightwardMargin = int(.07*imageWidth)
    L = getMessages(na, orig, cutoffMargin, inwardMargin, rightwardMargin)     
    res = ""
    totalText = ""
    if len(L)==0:
        return ""
    for i in L:
        if i.isUser:
            res+="User : " + i.getText()+"<br/>"
        else:
            res+="Match : " + i.getText()+"<br/>"
        totalText+=i.getText() + ". "
    ghostedLikelihood = ghostPredict.predict(totalText,len(L))
    if ghostedLikelihood == 0:
        ghostedLikelihood+=1
    res+="Likelihood of getting ghosted : " + str(ghostedLikelihood) + "<br/>"
    return res

# GET
@app.route('/users/<user>')
def hello_user(user):
    """
    this serves as a demo purpose
    """
    return "Hello %s!" % user

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)