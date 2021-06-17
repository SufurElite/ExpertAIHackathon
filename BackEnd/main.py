import numpy as np
from PIL import Image, ImageFilter, ImageOps


class Message:
    def __init__(self, top, bottom, left, right, isUser):
       self.top = top
       self.bottom = bottom
       self.left = left
       self.right = right
       self.isUser = isUser
    def getCoords(self):
        return(self.top, self.bottom, self.left, self.right)

def getMessages(imageArray, orig, margin):
    # Find X,Y coordinates of all user pixels
    userY, userX = np.where(np.all(imageArray==[33,185,252],axis=2))
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
    while userInd+1<absoluteBottom or matchInd+1<absoluteBottom:
        if matchInd<len(matchY)-1 and userInd<len(userY)-1:
            print(matchInd, userInd)
            print(matchY[matchInd],userY[userInd])
            if matchY[matchInd]>userY[userInd]:
                isUser = True
            else: 
                isUser = False
        elif matchInd<len(matchY)-1:
            print("Set Match as no more Users")
            isUser = False
        elif userInd<len(userY)-1:
            print("Set User as no more Match")
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
        if top!=bottom and bottom-top>margin:
            # Extract Region of Interest from unblurred original
            ROI = orig[top:bottom, left:right]
            print(len(ROI))

            Image.fromarray(ROI).save('result.png')
            input()
            if isUser:
                userInd+=1
            else:
                matchInd+=1
    return None

def main():
    # Open image and make into Numpy array
    for i in range(1,5):
        im = Image.open(str(i)+'.jpg').convert('RGB')
        na = np.array(im)
        orig = na.copy()    # Save original
        margin = .02*im.size[1]
        L = getMessages(na, orig, margin)    

if __name__ == "__main__":
    main()
