import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class RacePreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.categorical_cols = ['sex', 'trainer', 'jockey', 'owner', 'horse_name']

    def flatten(self, data):
        raw_data = []
        for race in (data if isinstance(data, list) else [data]):
            race_date = pd.to_datetime(race.date, dayfirst=True)
            for match in race.matches:
                for horse in match.results:
                    raw_data.append({
                        'match_id': match.id, 'date': race_date,
                        'sequence_number': match.sequence_number,
                        'total_runners': len(match.results),
                        'horse_name': horse.name, 'trainer': horse.trainer,
                        'jockey': horse.jockey, 'owner': horse.owner,
                        'weight': horse.weight, 'odds': horse.odds,
                        'placement': horse.placement, 'sex': horse.sex,
                        'age': horse.age, 'is_winner': 1 if horse.placement == 1 else 0
                    })
        return pd.DataFrame(raw_data)

    def fit_transform(self, df):
        # 1. Categorical Encoding (Fit only on training data)
        for col in self.categorical_cols:
            le = LabelEncoder()
            df[f'{col}_id'] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le

        return self._process_pipeline(df, fit=True)

    def transform(self, df):
        if len(self.label_encoders):
            print("Label encoders not fitted")
            return None
        # Apply existing encoders
        for col, le in self.label_encoders.items():
            df[f'{col}_id'] = df[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1)
        return self._process_pipeline(df, fit=False)


    def _process_pipeline(self, df, fit=True):
        df = self._feature_engineering(df)
        df = self._clean_data(df)
        df = self._drop_unused(df)
        return df
    def _feature_engineering(self,df: pd.DataFrame):
        # 1. Weight relative to the average in that specific match
        df['weight_diff_avg'] = df.groupby('match_id')['weight'].transform(lambda x: x - x.mean())
        # 2. Rank of odds (Market favorite = 1)
        df['odds_rank'] = df.groupby('match_id')['odds'].rank(ascending=True)
        # 3. Probability from odds (Implied probability)
        # Avoid division by zero for 0.0 odds (often scratched horses)
        df['implied_prob'] = df['odds'].apply(lambda x: 1/x if x > 0 else 0)
        return df
    def _clean_data(self, df: pd.DataFrame):
        """
        Remove rows of horses that didnt run
        Fill non-weighted horses with a previous weight of him or a mean of horses of same age and sex
        """
        # Sort by horse and date to make ffill based on most recent weight
        df = df.sort_values(by=['horse_name_id', 'date'])
        # Use NaN for horses without weight
        df.loc[df['weight'] <= 0, 'weight'] = np.nan
        # try to foward fill with horse previous weight
        df['weight'] = df.groupby('horse_name_id')['weight'].ffill()
        # try to backwards fill if its first races dont have its weight measured
        df['weight'] = df.groupby('horse_name_id')['weight'].bfill()
        # If still has weights not filled than use a mean based on horses of same sex and age 
        group_means = df.groupby(['sex', 'age'])['weight'].transform('mean')
        df['weight'] = df['weight'].fillna(group_means)
        # return only horses that did run in the race
        return df[df['odds'] > 0].copy()

    def _drop_unused(self, df: pd.DataFrame):
        """Drop unused/bad/useless columns for machine learning training"""
        cols_to_drop = ['horse_name', 'trainer', 'jockey', 'owner', 'date', 'sequence_number','sex']
        return df.drop(columns=[c for c in cols_to_drop if c in df.columns])



