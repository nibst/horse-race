import pickle
from domain.race import Race
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from prediction.race_preprocessor import RacePreprocessor
# Helper for Model training
def train_and_evaluate(df, preprocessor: RacePreprocessor):
    X = df.drop('is_winner', axis=1)
    y = df['is_winner']
    
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    
        # 3. Split into training and testing (80% train, 20% test)
    # Shuffle=False is important if you want to test on the "future" 
    # and train on the "past"
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.991, random_state=42, shuffle=False
    )

    print(f" lenght train {len(X_train)}")
    print(f" lenght test {len(X_test)}")
    
    # 4. Initialize and Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Predict and Evaluate
    predictions = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, predictions))
    print(classification_report(y_test, predictions))
    print(confusion_matrix(y_test,predictions))

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_imputed, y)
    return model

def main():
    with open("./data/races_since_01-11-2023", "rb") as f:
        races = pickle.load(f)
    
    print(races)
    preprocessor = RacePreprocessor()
    df = preprocessor.flatten(races)
    df_processed = preprocessor.fit_transform(df)
    
    model = train_and_evaluate(df_processed, preprocessor)
    print("Training complete.")

main()
