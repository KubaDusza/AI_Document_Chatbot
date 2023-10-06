from transformers import pipeline


DEFAULT_EMOTION_EMOTICONS = {
    'anger': '🤬',
    'disgust': '🤢',
    'fear': '😨',
    'joy': '😀',
    'neutral': '🙂',
    'sadness': '😭',
    'surprise': '😲'
}


class EmotionClassifier:
    def __init__(self, emotion_emoticons_dictionary: dict = None):
        if emotion_emoticons_dictionary is None:
            self.emotion_emoticons_dictionary = DEFAULT_EMOTION_EMOTICONS
        else:
            self.emotion_emoticons_dictionary = emotion_emoticons_dictionary

        self.classifier = pipeline("text-classification",
                                   model="j-hartmann/emotion-english-distilroberta-base",
                                   top_k=1)

    def classify(self, text: str):
        return self.emotion_emoticons_dictionary[self.classifier(text)[0][0]['label']]


if __name__ == '__main__':
    ec = EmotionClassifier()

    print(ec.classify("Im sorry for you. in this document..."))


