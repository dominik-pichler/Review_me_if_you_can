import pandas as pd
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from .review_translator import translate_reviews


def get_review_feels_like(review):
    # Convert results to DataFrame
    df = pd.DataFrame(results, columns=['ID', 'Review'])

    # Translate reviews using the defined function
    translated_df = translate_reviews(df)

    # Extract translated reviews for topic modeling
    documents = translated_df['Translated Review'].tolist()

    # Define vectorizer and representation models for BERTopic
    vectorizer_model = CountVectorizer(min_df=5, stop_words='english')
    topic_model = BERTopic(nr_topics=10, vectorizer_model=vectorizer_model)

    # Fit the topic model on the documents
    topics, probs = topic_model.fit_transform(documents)


# Function to get topic statistics (unchanged)
def get_topic_stats(topic_model, extra_cols=[]):
    topics_info_df = topic_model.get_topic_info().sort_values('Count', ascending=False)
    topics_info_df['Share'] = 100. * topics_info_df['Count'] / topics_info_df['Count'].sum()
    topics_info_df['CumulativeShare'] = 100. * topics_info_df['Count'].cumsum() / topics_info_df['Count'].sum()
    return topics_info_df[['Topic', 'Count', 'Share', 'CumulativeShare', 'Name', 'Representation'] + extra_cols]


