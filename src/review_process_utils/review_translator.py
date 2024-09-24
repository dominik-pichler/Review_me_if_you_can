import pandas as pd
from tqdm import tqdm
import langdetect
from deep_translator import GoogleTranslator

def translate_reviews(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure the DataFrame has the correct structure
    if df.shape[1] != 3:
        raise ValueError("DataFrame must have exactly four columns: 'Appartment', 'Date', 'Review', and 'ID'")

    # Extract columns
    appartments = df.iloc[:, 1]
    dates = df.iloc[:, 2]
    reviews = df.iloc[:, 0]

    translated_reviews = []

    for review in tqdm(reviews):
        translated_review = review  # Default to original review if translation is not needed
        try:
            lang = langdetect.detect(review)
            if lang != 'en':
                try:
                    translated_review = GoogleTranslator(source=lang, target='en').translate(review)
                except Exception as e:
                    print(f"Translation error for review '{review}': {e}")
        except Exception as e:
            print(f"Language detection error for review '{review}': {e}")

        translated_reviews.append(translated_review)

    # Create a new DataFrame with Apartments, Dates, IDs, Reviews, and Translated Reviews
    translated_df = pd.DataFrame({
        'Appartment': appartments,
        'Date': dates,
        'Review': reviews,
        'Translated_Review': translated_reviews,
    })

    return translated_df

# Example usage
# Assuming df is your input DataFrame with columns: 'Apartment', 'Date', 'Review', 'ID'
# translated_df = translate_reviews(df)