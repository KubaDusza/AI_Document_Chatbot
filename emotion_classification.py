from transformers import pipeline
import streamlit as st


@st.cache_data
def get_emotion_dict():
    return {
        'anger': '🤬',
        'disgust': '🤢',
        'fear': '😨',
        'joy': '😀',
        'neutral': '🙂',
        'sadness': '😭',
        'surprise': '😲'
    }


@st.cache_resource(show_spinner=False)
def get_pipeline():
    return pipeline(task="text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    top_k=1)

class EmotionClassifier:
    def __init__(self, emotion_emoticons_dictionary: dict = None):
        if emotion_emoticons_dictionary is None:
            self.emotion_emoticons_dictionary = get_emotion_dict()
        else:
            self.emotion_emoticons_dictionary = emotion_emoticons_dictionary

        self.classifier = get_pipeline()

    def classify(self, text: str):
        return self.emotion_emoticons_dictionary[self.classifier(text)[0][0]['label']]


if __name__ == '__main__':
    ec = EmotionClassifier()

    print(ec.classify("Im sorry for you. in this document..."))


