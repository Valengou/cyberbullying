import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.metrics import ConfusionMatrixDisplay,confusion_matrix
import os
import joblib

def clean_text(text, remove_punctuation=True, lower_text=True,
                remove_numbers=True, remove_stopwords=True, lemmatize=True):

    text = str(text)

    # remove twitter mentions (@) and RT
    regex = r'^@\w+'
    text = re.sub(regex, '', text, flags=re.IGNORECASE)
    text = re.sub(r'RT[\s]+', '', text, flags=re.IGNORECASE)

    # keep only letters
    if remove_punctuation:
        regex = r'[^a-zA-Z]+'
        text = re.sub(regex, ' ', text)

    # lower text
    if lower_text:
        text = text.lower()

    # remove numbers
    if remove_numbers:
        text = ''.join([w for w in text if not w.isdigit()])

    # remove stopwords
    if remove_stopwords:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        text = ' '.join([w for w in word_tokens if not w in stop_words])

    # lemmatize
    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        text = ''.join([lemmatizer.lemmatize(word) for word in text]) # no entiendo por qué no va un espacio

    # remove spam
    regex = r'\b(\w+)(?:\W+\1\b)+'
    text = re.sub(regex, r'\1', text, flags=re.IGNORECASE)

    # remove empty spaces
    text = text.strip()

    return text


def clean_df(df, remove_punctuation=True, lower_text=True,
            remove_numbers=True, remove_stopwords=True, lemmatize=True):

    df = preprocess_x(df)

    df = df.copy()

    #df = df.drop_duplicates()

    df['text'] = df['text'].apply(lambda text: clean_text(text,
                                                        remove_punctuation,
                                                        lower_text,
                                                        remove_numbers,
                                                        remove_stopwords,
                                                        lemmatize))

    #df = df.drop_duplicates()

    #df = df.replace(['', ' '], np.nan)
    #df = df.dropna().reset_index(drop=True)
    df = df.replace(['', np.nan, -np.inf, np.inf], 'a')

    return df


def preprocess_x(X):
    if not isinstance(X, pd.DataFrame):
        if isinstance(X, str):
            X = [X]
        X = pd.DataFrame({'text': X})
    return X


def conf_mx_all(y_test, y_pred):

    cm = confusion_matrix(y_test, y_pred)

    TN = cm[0,0]
    TP = cm[1,1]
    FN = cm[1,0]
    FP = cm[0,1]

    recall = np.round_(TP/(TP+FN),3)
    precision = np.round_(TP/(TP+FP),3)
    accuracy = np.round_((TP+TN)/(TP+TN+FP+FN),3)
    F1= np.round((2*precision*recall)/(precision+recall), 3)

    print(f"Recall: {recall}")
    print(f"Precision: {precision}")
    print(f"Accuracy: {accuracy}")
    print(f"F1-score: {F1}")

    disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=[0,1])
    disp.plot()

    return recall, precision, accuracy, F1

def save_trained_model(model, name='model'):
    """ Save the trained model into a model.joblib file """
    path_file = os.path.dirname(__file__) + f'/../{name}.joblib' # no funciona en jupyter
    joblib.dump(model, path_file)

def get_trained_model(name='model'):
    path_file = os.path.dirname(__file__) + f'/../{name}.joblib' # no funciona en jupyter
    return joblib.load(path_file)

def predict(text):
    model_prediction = get_trained_model('model_prediction')
    model_classifier = get_trained_model('model_classifier')

    response = model_prediction.predict_phrase(text)
    bullying_type = None

    if response['prediction'] == 1:
        bullying_type = model_classifier.predict(text)[0].upper()
        if bullying_type == 'OTHER':
            bullying_type = 'AGGRESSION'

    response['type'] = bullying_type

    return response
