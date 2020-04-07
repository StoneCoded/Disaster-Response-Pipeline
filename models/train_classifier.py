# importing libraries
import nltk
nltk.download(['punkt', 'wordnet','averaged_perceptron_tagger'])
import sys
import pandas as pd
import numpy as np
import pickle
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sqlalchemy import create_engine
import re
from sklearn.metrics import classification_report,accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.multioutput import MultiOutputClassifier

import sys
sys.path.append('../')
import utils


def load_data(database_filepath):
    """ 
    Loading Data From Database. 
  
    Splitting X And Y Columns And Returning Them Also Returning
    Category Names. 
  
    Parameters: 
    database_filepath (str): Filepath Where Database Is Located.
    
    Returns: 
    X (DataFrame): Feature Columns
    Y (DataFrame): Label Columns
    category_names (List): Category Names List
    """
    
    # loading data from database
    db_name = 'sqlite:///{}'.format(database_filepath)
    engine = create_engine(db_name)

    # using pandas to read table from database
    df = pd.read_sql_table('DisasterResponse',engine)

    # splitting X and Y
    X = df['message'].values
    Y = df.iloc[:,4:]

    # finding category names from Y DataFrame
    category_names = list(Y.columns)
    
    return X , Y , category_names



def build_model():
    """
    Build Model Function.
    
    This Function's Output Is A Scikit ML Pipeline That Process Text Messages
    According To NLP Best-Practice And Apply A Classifier.

    Returns: 
    model (GridSearchCV or Scikit Pipelin Object) : ML Model
    """
    # creating multioutput classifier pipeline
    pipeline = Pipeline([
        ('features', FeatureUnion([

            ('text_pipeline', Pipeline([
                ('vect', CountVectorizer(tokenizer=tokenize)),
                ('tfidf', TfidfTransformer())
            ])),

            ('starting_verb', utils.StartingVerbExtractor())
        ])),

        ('clf', MultiOutputClassifier(AdaBoostClassifier()))
    ])
    
    # parameters to grid search
    parameters = { 'clf__estimator__n_estimators' : [50] }
    
    # initiating GridSearchCV method
    model = GridSearchCV(pipeline, param_grid=parameters)

    return model


def evaluate_model(model, X_test, Y_test, category_names):
    """ 
    Model Evaluation Function. 
  
    Cleaning The Data And Tokenizing Text. 
  
    Parameters:
    model (GridSearchCV or Scikit Pipelin Object) : Trained ML Model
    X_test (DataFrame) : Test Features
    Y_test (DataFrame) : Test Labels
    category_names (List): Category Names List
    
    """

    # predict on test data
    Y_pred = model.predict(X_test)
    for i in range(len(category_names)):
        print("Category:", category_names[i],"\n", classification_report(Y_test.iloc[:, i].values, Y_pred[:, i]))
        print('Accuracy of %25s: %.2f' %(category_names[i], accuracy_score(Y_test.iloc[:, i].values, Y_pred[:,i])))


def save_model(model, model_filepath):
    """
    Save Model function
    
    This Function Saves Trained Model As Pickle File, To Be Loaded Later.
    
    Parameters:
    model (GridSearchCV or Scikit Pipelin Object) : Trained ML Model
    model_filepath (str) : Destination Path To Save .pkl File
    
    """
    filename = model_filepath
    pickle.dump(model, open(filename, 'wb'))
    

def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()
