import pandas as pd
from race import Race
from typing import List
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.impute import SimpleImputer
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows',None)
def preprocess(data:List[Race]):
    df = flatten_into_dataframe(data)
    df = process_categorical(df)
    df = feature_engineering(df)
    df = clean_bad_data(df)
    df = drop_unused(df)
    print(df.columns)
    train_model(df)
    pass


def flatten_into_dataframe(data: List[Race]):
    raw_data = []
    for race in data:
        race_date = pd.to_datetime(race.date, dayfirst=True)
        for match in race.matches:
            match_id = match.id
            seq_num = match.sequence_number
            
            # Determine number of runners in this match (useful feature)
            total_runners = len(match.results)
            
            for horse in match.results:
                # Skip horses that didn't start/finish (placement 0) if you only want to predict outcomes
                # or keep them and mark them as 'lost'
                raw_data.append({
                    'match_id': match_id,
                    'date': race_date,
                    'sequence_number': seq_num,
                    'total_runners': total_runners,
                    'horse_name': horse.name,
                    'trainer': horse.trainer,
                    'jockey': horse.jockey,
                    'owner': horse.owner,
                    'weight': horse.weight,
                    'odds': horse.odds,
                    'placement': horse.placement,
                    'sex': horse.sex,
                    'age': horse.age,
                    'is_winner': 1 if horse.placement == 1 else 0
                })

    df = pd.DataFrame(raw_data)
    return df

def process_categorical(df: pd.DataFrame):
    categorical_cols = ['sex','trainer', 'jockey', 'owner', 'horse_name']
    le = LabelEncoder()
    for col in categorical_cols:
        df[col + '_id'] = le.fit_transform(df[col])
    return df    

def feature_engineering(df: pd.DataFrame):
    # 1. Weight relative to the average in that specific match
    df['weight_diff_avg'] = df.groupby('match_id')['weight'].transform(lambda x: x - x.mean())
    # 2. Rank of odds (Market favorite = 1)
    df['odds_rank'] = df.groupby('match_id')['odds'].rank(ascending=True)

    # 3. Probability from odds (Implied probability)
    # Avoid division by zero for 0.0 odds (often scratched horses)
    df['implied_prob'] = df['odds'].apply(lambda x: 1/x if x > 0 else 0)
    return df

def clean_bad_data(df: pd.DataFrame):
    """
    Remove rows of horses that didnt run
    Fill non-weighted horses with a previous weight of him or a mean of horses of same age and sex
    """
    # Sort by horse and date to make ffill based on most recent weight
    df = df.sort_values(by=['horse_name_id', 'date'])
    # Use NaN for horses without weight
    df.loc[df['weight'] <= 0, 'weight'] = np.nan
    print(df[['horse_name','weight']])
    # try to foward fill with horse previous weight
    df['weight'] = df.groupby('horse_name_id')['weight'].ffill()
    # try to backwards fill if its first races dont have its weight measured
    df['weight'] = df.groupby('horse_name_id')['weight'].bfill()
    print(df['weight'])
    # If still has weights not filled than use a mean based on horses of same sex and age 
    group_means = df.groupby(['sex', 'age'])['weight'].transform('mean')
    df['weight'] = df['weight'].fillna(group_means)

    print(df[['weight','age']])
    # return only horses that did run in the race
    return df[df['odds'] > 0].copy()

def drop_unused(df: pd.DataFrame):
    """Drop unused/bad/useless columns for machine learning training"""
    cols_to_drop = ['horse_name', 'trainer', 'jockey', 'owner', 'date', 'sequence_number','sex']
    # Drop only the ones that exist in the dataframe
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    return df
   
def train_model(df: pd.DataFrame):
    # 1. Define X (features) and y (target)
    # We drop 'is_winner' from X because it is the target
    X = df.drop('is_winner', axis=1)
    y = df['is_winner']
    
    # 2. Check for missing values (Machine Learning models cannot handle NaNs)
    # If any remain after your cleaning, we impute them with the median
    imputer = SimpleImputer(strategy='median')
    X = imputer.fit_transform(X)
    
    # 3. Split into training and testing (80% train, 20% test)
    # Shuffle=False is important if you want to test on the "future" 
    # and train on the "past"
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.9, random_state=42, shuffle=False
    )
    
    # 4. Initialize and Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Predict and Evaluate
    predictions = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, predictions))
    print(classification_report(y_test, predictions))
    print(confusion_matrix(y_test,predictions))
    
    return model

def main():
    import pickle
    safe_date = "01-11-2023"
    with open(f"races_since_{safe_date}", "rb") as f:
        races = pickle.load(f)
    preprocess(races)
    # for race in races:
    #     print("Data: " + race.date)
    #     for match in race.matches:
    #         if not match.results:
    #             continue
    #         print(match.id)
    #         print(match.sequence_number)
    #         print(*match.results, sep="\n")
    #         print("------------")

main()
