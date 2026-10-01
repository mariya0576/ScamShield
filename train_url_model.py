import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


# Load the dataset
data = pd.read_csv("PhiUSIIL_Phishing_URL_Dataset.csv")


# 0 = phishing
# 1 = legitimate
X = data["URL"].astype(str)
y = data["label"]


# Split the URLs
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# Convert URL characters into numerical features
vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 5),
    min_df=2,
    sublinear_tf=True,
    max_features=100000
)


X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)


# Create the ML model
model = LogisticRegression(
    max_iter=1000
)


# Train the model
model.fit(X_train_tfidf, y_train)


# Test the model
predictions = model.predict(X_test_tfidf)

print("URL MODEL RESULTS")
print("-----------------")

print(classification_report(y_test, predictions))


# Save both the model and vectorizer
joblib.dump(
    {
        "model": model,
        "vectorizer": vectorizer
    },
    "url_model.pkl"
)


print("URL model saved successfully!")