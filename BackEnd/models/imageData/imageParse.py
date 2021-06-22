import json, sys
import os, re, io, glob
from google.cloud import vision
from google.cloud import storage
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from expertai.nlapi.cloud.client import ExpertAiClient

# Set Expert AI variables
os.environ['EAI_USERNAME'] = ''
os.environ['EAI_PASSWORD'] = ''

TaxonomyFeatures = ["Anger", "Irritation", "Exasperation", "Anxiety","Fear","Stress","Worry","Disgust","Repulsion","Guilt","Shame","Embarrassment","Regret","Boredom", "Hatred", "Offence", "Jealousy", "Envy","Sadness","Torment","Suffering","Disappointment","Disillusion", "Resignation", "Surprise","Happiness","Excitement","Joy","Amusement","Well-Being","Satisfaction","Relief","Like","Trust","Affection","Love","Passion","Empathy","Compassion","Asociality","Impoliteness","Ungratefulness","Emotionality","Isolation","Disagreement","Seriousness","Introversion","Unreservedness","Humour","Sexuality","Extroversion","Pleasantness","Trustfulness","Gratefulness","Empathy","Sedentariness","Passivity","Calmness","Initiative","Dynamism","Rejection","Apathy","Apprehension","Traditionalism","Conformism","Negativity","Bias","Cautiousness","Progressiveness","Acceptance","Courage","Positivity","Curiosity","Superficiality","Unawareness","Disorganization","Insecurity","Ignorance","Illusion","Awareness","Spirituality","Concern","Knowledge","Self-confidence","Organization","Violence","Extremism","Discrimination","Dishonesty","Neglect","Unlawfulness","Irresponsibility","Honesty","Compassion","Commitment","Lawfulness","Solidarity","Inclusiveness","Lack of intelligence","Inexperience","Incompetence","Rationality","Smartness","Creativity","Competence","Dissoluteness","Gluttony","Materialism","Addiction","Healthy lifestyle","Self-restraint"]

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

def getFeatures(fpath):
    print("Getting features for ", fpath)
    x = [0 for i in range(len(TaxonomyFeatures)+3)]
    aiClient = ExpertAiClient()
    
    im = Image.open(fpath).convert('RGB')
    na = np.array(im)
    orig = na.copy()    # Save original
    imageWidth = im.size[0]
    imageHeight = im.size[1]
    cutoffMargin = .02*imageHeight
    inwardMargin = int(.12*imageWidth)
    rightwardMargin = int(.07*imageWidth)
    L = getMessages(na, orig, cutoffMargin, inwardMargin, rightwardMargin)     
    totalText = ""
    if len(L)==0:
        return ""
    for i in L:
        totalText+=i.getText() + ". "
    aiClient = ExpertAiClient()
    output = aiClient.specific_resource_analysis(
                body={"document": {"text": totalText}}, 
                params={'language': "en", 'resource': 'sentiment'
    })
    sentiment = output.sentiment.overall
    output = aiClient.classification(body={"document": {"text": totalText}}, params={'taxonomy': "behavioral-traits", 'language': "en"})
    for category in output.categories:
        x[TaxonomyFeatures.index(category.hierarchy[len(category.hierarchy)-1])]=1
    output = aiClient.classification(body={"document": {"text": totalText}}, params={'taxonomy': "emotional-traits", 'language': "en"})
    for category in output.categories:
        x[TaxonomyFeatures.index(category.hierarchy[len(category.hierarchy)-1])]=1
    x[len(TaxonomyFeatures)] = sentiment
    x[len(TaxonomyFeatures)+1] = len(L)
    x[len(TaxonomyFeatures)+2] = len(totalText)/len(L)
    return x

def createTrainingData():
    X_data = []
    y = []
    newData = {}
    num = 1
    for subdir, dirs, files in os.walk(os.getcwd()):
        for file in files:
            fpath = os.path.join(subdir, file)
            if(fpath[-3:]=="png"):
                print(num)
                x = getFeatures(fpath)
                X_data.append(x)
                if os.path.dirname(fpath).find("Positive")>-1:
                    y.append(1)
                else:
                    y.append(0)
                num+=1
    data = {"X":X_data, "y":y}
    with open("data.json","w+") as f:
        json.dump(data, f)
    print(X_data)
    print(y)
        
createTrainingData()