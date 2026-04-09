from time import strftime

from numpy import ndarray
from domain.race import Race
from sklearn.ensemble import RandomForestClassifier
import pickle
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
class WinnerPredictor:

    def __init__(self, preprocessor, model=None):
        self.preprocessor = preprocessor
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def train(self, races):
        # 1. Flatten and Process
        df = self.preprocessor.flatten_to_df(races)
        df_processed = self.preprocessor.fit_transform(df)
        
        # 2. Split Features/Target
        X = df_processed.drop('is_winner', axis=1)
        y = df_processed['is_winner']
        
        # 3. Impute and Train
        X_imputed = self.preprocessor.imputer.fit_transform(X)
        self.model.fit(X_imputed, y)
        self.is_trained = True
        
    def predict_match(self, match):
        """Returns the probabilty that the horse will win"""
        if not self.is_trained:
            raise Exception("Model not trained yet!")
            
        # Flatten and Process using the SAVED preprocessor state
        today = datetime.now().strftime("%d/%m/%Y")
        df = self.preprocessor.flatten_to_df([Race(date=today,matches=[match])])
        df_processed = self.preprocessor.transform(df)
        # Impute using the SAVED imputer state
        X = df_processed.drop('is_winner', axis=1, errors='ignore')
        X_imputed = self.preprocessor.imputer.transform(X)
        # Get probabilities (model.predict_proba returns [prob_loss, prob_win])
        probabilities = [float(prob[1]) for prob in self.model.predict_proba(X_imputed)]# Get win probability
        # Getting back the horse name
        le = self.preprocessor.label_encoders['horse_name']
        # Assuming 'horse_name_id' is a column in your 'df_processed'
        names = df_processed['horse_name_id'].astype(int)

        return list(zip(names,probabilities))

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

