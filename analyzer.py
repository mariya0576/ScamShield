import os
import pandas as pd
import joblib

from pypdf import PdfReader
from docx import Document

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# ---------------- TEXT MODEL ----------------

data = pd.read_csv(
    "SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "message"]
)

X = data["message"]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

vectorizer = TfidfVectorizer()

X_train_tfidf = vectorizer.fit_transform(X_train)

model = LogisticRegression()
model.fit(X_train_tfidf, y_train)


def get_recommendation(risk_level):

    if risk_level == "HIGH RISK":
        return (
            "Do not click links or share personal information. "
            "Verify the message through an official source."
        )

    elif risk_level == "SUSPICIOUS":
        return (
            "Be cautious. Avoid clicking links or sharing sensitive "
            "information until the message is verified."
        )

    else:
        return (
            "No major scam signals were detected, but always verify "
            "unexpected requests."
        )


def analyze_text(message):

    message_tfidf = vectorizer.transform([message])

    probability = model.predict_proba(message_tfidf)[0]

    spam_probability = probability[1]

    risk_score = int(spam_probability * 100)

    if risk_score >= 60:
        risk_level = "HIGH RISK"

    elif risk_score >= 30:
        risk_level = "SUSPICIOUS"

    else:
        risk_level = "LOW RISK"

    indicators = []

    message_lower = message.lower()

    if "otp" in message_lower:
        indicators.append("Requests an OTP")

    if "urgent" in message_lower or "immediately" in message_lower:
        indicators.append("Uses urgent language")

    if "won" in message_lower or "prize" in message_lower:
        indicators.append("Contains a prize or reward claim")

    if "click" in message_lower or "link" in message_lower:
        indicators.append("Contains a link or click instruction")

    if not indicators:
        indicators.append("No common scam indicators detected")

    return {
        "score": risk_score,
        "level": risk_level,
        "indicators": indicators,
        "recommendation": get_recommendation(risk_level)
    }


# ---------------- URL MODEL ----------------

url_model_data = joblib.load("url_model.pkl")

url_model = url_model_data["model"]
url_vectorizer = url_model_data["vectorizer"]


def analyze_url(url):

    url_features = url_vectorizer.transform([url])

    probabilities = url_model.predict_proba(url_features)[0]

    phishing_probability = probabilities[0]

    risk_score = int(phishing_probability * 100)

    if risk_score >= 70:
        risk_level = "HIGH RISK"

    elif risk_score >= 30:
        risk_level = "SUSPICIOUS"

    else:
        risk_level = "LOW RISK"

    indicators = []

    url_lower = url.lower()

    if not url_lower.startswith("https://"):
        indicators.append("Does not use HTTPS")

    if "@" in url:
        indicators.append("Contains an @ symbol")

    if len(url) > 75:
        indicators.append("Unusually long URL")

    if url_lower.count("-") >= 3:
        indicators.append("Contains multiple hyphens")

    if any(word in url_lower for word in [
        "login",
        "verify",
        "account",
        "secure",
        "password"
    ]):
        indicators.append("Contains sensitive account-related terms")

    if not indicators:
        indicators.append("No major URL-based indicators detected")

    if risk_level == "HIGH RISK":
        recommendation = (
            "Avoid opening this URL or entering personal information. "
            "Verify the website through an official source."
        )

    elif risk_level == "SUSPICIOUS":
        recommendation = (
            "Be cautious with this URL. Do not enter sensitive "
            "information until the website is verified."
        )

    else:
        recommendation = (
            "The URL appears legitimate based on the model analysis, "
            "but always verify unfamiliar websites before sharing information."
        )

    return {
        "score": risk_score,
        "level": risk_level,
        "indicators": indicators,
        "recommendation": recommendation
    }


# ---------------- EMAIL MODEL ----------------

email_model_data = joblib.load("email_model.pkl")

email_model = email_model_data["model"]
email_vectorizer = email_model_data["vectorizer"]


def analyze_email(sender, subject, body):

    email_text = subject + " " + body

    email_features = email_vectorizer.transform(
        [email_text]
    )

    probabilities = email_model.predict_proba(
        email_features
    )[0]

    spam_probability = probabilities[1]

    ml_score = int(spam_probability * 100)

    indicators = []

    text_lower = email_text.lower()
    sender_lower = sender.lower()

    if any(word in text_lower for word in [
        "urgent",
        "immediately",
        "action required",
        "act now",
        "final warning"
    ]):
        indicators.append("Uses urgent or threatening language")

    if any(word in text_lower for word in [
        "won",
        "winner",
        "prize",
        "reward",
        "congratulations",
        "lottery"
    ]):
        indicators.append("Contains a prize or reward claim")

    if any(word in text_lower for word in [
        "payment",
        "pay",
        "transfer",
        "bank account",
        "credit card",
        "money"
    ]):
        indicators.append("Contains a financial request")

    if any(word in text_lower for word in [
        "password",
        "otp",
        "one time password",
        "verification code",
        "pin"
    ]):
        indicators.append("Requests sensitive information")

    if any(word in text_lower for word in [
        "click",
        "click here",
        "open the link",
        "visit the link"
    ]):
        indicators.append("Contains a link or click instruction")

    if any(word in sender_lower for word in [
        "noreply",
        "support",
        "admin",
        "security"
    ]):

        if any(word in text_lower for word in [
            "verify",
            "account",
            "password",
            "login",
            "security"
        ]):
            indicators.append(
                "Sender address uses a common service-related name"
            )

    indicator_score = min(
        len(indicators) * 12,
        60
    )

    risk_score = min(
        ml_score + indicator_score,
        100
    )

    if risk_score >= 60:
        risk_level = "HIGH RISK"

    elif risk_score >= 30:
        risk_level = "SUSPICIOUS"

    else:
        risk_level = "LOW RISK"

    if not indicators:
        indicators.append(
            "No common email scam indicators detected"
        )

    if risk_level == "HIGH RISK":

        recommendation = (
            "Do not reply, click links, open unexpected attachments, "
            "or share personal information. Verify the sender through "
            "an official source."
        )

    elif risk_level == "SUSPICIOUS":

        recommendation = (
            "Be cautious with this email. Avoid clicking links or "
            "sharing sensitive information until the sender and request "
            "are verified."
        )

    else:

        recommendation = (
            "No major scam signals were detected, but verify unexpected "
            "emails before taking action."
        )

    return {
        "score": risk_score,
        "level": risk_level,
        "indicators": indicators,
        "recommendation": recommendation
    }


# ---------------- DOCUMENT ANALYZER ----------------

def extract_document_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()


    # TXT file

    if extension == ".txt":

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            return file.read()


    # PDF file

    elif extension == ".pdf":

        reader = PdfReader(file_path)

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)


    # DOCX file

    elif extension == ".docx":

        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                paragraphs.append(
                    paragraph.text
                )

        return "\n".join(paragraphs)


    return ""


def analyze_document(file_path):

    document_text = extract_document_text(
        file_path
    )

    if not document_text.strip():

        return {
            "score": 0,
            "level": "NO TEXT FOUND",
            "indicators": [
                "No readable text was found in the document"
            ],
            "recommendation": (
                "The document could not be analyzed because "
                "no readable text was detected."
            )
        }


    return analyze_text(document_text)