import pandas as pd
from tqdm import tqdm
import langdetect
from deep_translator import GoogleTranslator


def translate_reviews(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure the DataFrame has the correct structure
    if df.shape[1] != 2:
        raise ValueError("DataFrame must have exactly two columns: 'ID' and 'Review'")

    # Extract IDs and reviews
    ids = df.iloc[:, 0]
    reviews = df.iloc[:, 1]

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

    # Create a new DataFrame with IDs and translated reviews
    translated_df = pd.DataFrame({'ID': ids, 'Translated Review': translated_reviews})

    return translated_df


# Example usage
data = {'ID': [1, 2, 3], 'Review': ['Bonjour', 'Hello', 'Hola']}
df = pd.DataFrame(data)

translated_df = translate_reviews(df)
print(translated_df)