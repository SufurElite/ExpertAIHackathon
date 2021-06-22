# BackEnd Development
Here are links I found useful to code &amp; tutorials for the BackEnd.

## Image Manipulation
### Splitting the Image
1. https://stackoverflow.com/questions/60780831/python-how-to-cut-out-an-area-with-specific-color-from-image-opencv-numpy

## Flask
### Connection
1. https://medium.com/android-news/handmade-backend-for-android-app-using-python-flask-framework-b173ba2bb3aa
2. https://stackoverflow.com/questions/48811798/upload-bitmap-from-memory-via-retrofit?noredirect=1&lq=1

## ML Models
### Human Chat Quality Prediction
1. https://medium.com/analytics-vidhya/encoder-decoder-seq2seq-models-clearly-explained-c34186fbf49b
2. https://machinelearningmastery.com/sequence-prediction/
3. https://towardsdatascience.com/how-to-implement-seq2seq-lstm-model-in-keras-shortcutnlp-6f355f3e5639
#### Human Evaluated Data From Facebook
* Paper: https://arxiv.org/abs/1902.08654
* Code: https://github.com/facebookresearch/ParlAI/tree/controllable_dialogue_archive/projects/controllable_dialogue

# To-Do : 
* Need to fix: App Engine started to have issues once I ran tensorflow on it - had to revert back to running the sever locally. 
* Get more human data evaluating conversation attributes to better fine-tune the predictions
* Maybe explore more important factors for communicating with people on tinder (e.g. for a chatbot inquisitiveness and listening is quite useful, but perhaps for tinder there are more pertinent conversation aspects - such as the balance of flirting and outright crude comments)
* Acquire more data from tinder conversations and their result to fine-tune binary ghosted model
* Input a potential line to see what the AI makes of your follow-up
* Currently it's an instantaneous overview of the conversation rather than the full conversation, would like to take prior elements of the conversation into account

