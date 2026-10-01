import os
import email
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


# Dataset paths

ham_folder = os.path.expanduser(
    "~/Downloads/20030228_easy_ham/easy_ham"
)

spam_folder = os.path.expanduser(
    "~/Downloads/20030228_spam/spam"
)


emails = []
labels = []


# Extract useful text from an email

def extract_email_text(file_path):

    with open(
        file_path,
        "r",
        encoding="latin-1"
    ) as file:

        message = email.message_from_file(file)


    subject = message.get("Subject", "")

    body_parts = []


    if message.is_multipart():

        for part in message.walk():

            if part.get_content_type() == "text/plain":

                payload = part.get_payload(
                    decode=True
                )

                if payload:

                    body_parts.append(
                        payload.decode(
                            "latin-1",
                            errors="ignore"
                        )
                    )

    else:

        payload = message.get_payload(
            decode=True
        )

        if isinstance(payload, bytes):

            body_parts.append(
                payload.decode(
                    "latin-1",
                    errors="ignore"
                )
            )

        elif payload:

            body_parts.append(str(payload))


    body = " ".join(body_parts)

    return subject + " " + body


# Read legitimate emails

for filename in os.listdir(ham_folder):

    file_path = os.path.join(
        ham_folder,
        filename
    )

    if os.path.isfile(file_path):

        try:

            text = extract_email_text(file_path)

            if text.strip():

                emails.append(text)
                labels.append(0)

        except Exception:

            continue


# Read spam emails

for filename in os.listdir(spam_folder):

    file_path = os.path.join(
        spam_folder,
        filename
    )

    if os.path.isfile(file_path):

        try:

            text = extract_email_text(file_path)

            if text.strip():

                emails.append(text)
                labels.append(1)

        except Exception:

            continue


print("EMAIL DATASET")
print("-------------")

print("Total emails:", len(emails))
print("Legitimate emails:", labels.count(0))
print("Spam emails:", labels.count(1))


# Split the dataset

X_train, X_test, y_train, y_test = train_test_split(
    emails,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)


# Convert email text into numerical features

vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_features=150000,
    sublinear_tf=True
)


X_train_tfidf = vectorizer.fit_transform(X_train)

X_test_tfidf = vectorizer.transform(X_test)


# Train the model

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(
    X_train_tfidf,
    y_train
)


# Test the model

predictions = model.predict(X_test_tfidf)


print()
print("EMAIL MODEL RESULTS")
print("-------------------")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Legitimate",
            "Spam"
        ]
    )
)


# Save the model

joblib.dump(
    {
        "model": model,
        "vectorizer": vectorizer
    },
    "email_model.pkl"
)


print("Email model saved successfully!")