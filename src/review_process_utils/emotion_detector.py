import pandas as pd
from transformers import pipeline

def detect_emotions(english_reviews:pd.DataFrame) -> pd.DataFrame:
    # Load the pre-trained emotion detection model
    emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
    t_reviews = english_reviews["Translated_Review"].tolist()
    # Detect emotions
    emotions = emotion_classifier(t_reviews)
    # Prepare data for DataFrame
    data = {
        "Text": [],
        "Emotion": [],
        "Score": []
    }

    # Populate the data dictionary
    for text, emotion in zip(t_reviews, emotions):
        data["Text"].append(text)
        data["Emotion"].append(emotion['label'])
        data["Score"].append(emotion['score'])

    # Create a DataFrame
    df = pd.DataFrame(data)
    df.to_csv('../db_test.csv', index=False)
    # Display the DataFrame
    return df