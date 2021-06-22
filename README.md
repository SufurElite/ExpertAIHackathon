# Chadvice

## Inspiration

As any college-aged individual will attest, for better or worse, dating apps are now the norm for meeting people. But, trying to engage in conversation can be daunting: toeing the line of asking too many questions vs answering too many, brevity vs detail, worrying about being ghosted, etc. That's where Chadvice comes in. Chadvice is an app that provides analysis of your dating app conversations in real-time, gauging their interest and the likelihood of ghosting. 

## How I built it

### Overview
I built the Front-End for the Android Application in Java and the back-end in python. The app uses media projection to record the screen and programmatically take a screenshot, which using retrofit2 is sent to the back-end. The backend is hosted on Google App Engine and the user authentication is done through Firebase. Once the screenshot has been sent to the backend, it splits the image into just the text messages in the correct order and uses google-cloud-vision to apply ocr to the images. The machine learning models are applied to the conversations and the values are returned to the user, so they have insight into their conversation.

### Models
When determining how to approach the problem of giving advice/insight on dating converations (or really conversatios at large), I discovered various research papers on the evaluation of Chatbots. The two most influential in my approaches are Facebook AI Research's _ What makes a good conversation _ and Zurich University's _ Towards a Metric for Automated COnversational Dialogue System Evaluation and Improvement _ (See github for these and other useful papers). 

In the former paper, they had humans evaluate their chatbots on a scale of 1 to 4 on things like repetition, whether the conversation was interesting, etc, and they had intended this to illustrate the progress of their chatbot, but I inturn decided to create a model to predict what the human evaluation would be given the text. 

The second main model predicts the likelihood of being ghosted in a conversation (based on the idea of discerning between good and bad conversation through a binary classifier akin to the second paper). It is here predominantly that the Expert AI API is being used, as features for a binary classifier - namely, the categories from the emotional-traits taxonomy & behavioral-traits taxonomy and the sentiment of the converasation. 

Consequently, there were two primary datasets that I used for this project: Facebook AI's Human Evaluated Chatbot Json and a collection of conversations on tinder pooled from my friends (from successful and nonsuccesful conversations) - for the sake of anonymity, I have not uploaded the latter. 

## Challenges I ran into
* I had difficulty with the media projection on Android. (also not being able to have media projection twice made recording the phone screen for the demo harder)
* My Android Emulator has continually refused to co-operate with me (I suspect because of a clashing Cordova android installation). 

## Accomplishments that I'm proud of
While this is still a proof of concept, I developed an app from start to a publishable state that isn't dependent on running locally on a machine (i.e. the backend is deployed and works smoothly with the Front-End). Also, it has been almost 4 years since I have done any extensive Java development and all my prior Android App Development has been through web wrappers.   

## What I learned
Don't start a conversation "hey", but, whilst that's true, on a more serious note I did learn a lot about App Development.

## What's next for Chadvice
* Add more analysis (currently only three aspects of conversation) and perhaps more targeted dating aspects to conversation (e.g. striking the right balance of flirting vs just talking)
* Entire conversation analysis - currently Chadvice provides instantaneous analysis of a conversation without taking in context or information from earlier in the conversation
* Pool more data on conversations from friends to better tune the models
* Related to the above, maybe make it possible for users to mark conversations as a positive result to collect additional data from training
* Much farther down the line, should add a generative suggestion as to what to say or subject to talk about