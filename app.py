from flask import Flask, render_template, request, redirect

from analyzer import (
    analyze_text,
    analyze_url,
    analyze_email,
    analyze_document
)

from database import (
    create_database,
    save_analysis,
    get_history,
    delete_analysis,
)

import os
import tempfile


app = Flask(__name__)


create_database()


def save_result(analyzer_type, analyzed_content, result):

    if result:

        save_analysis(
            analyzer_type,
            analyzed_content,
            result["level"],
            result["score"],
            result["indicators"],
            result["recommendation"]
        )


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/text", methods=["GET", "POST"])
def text_analyzer():

    result = None
    message = ""

    if request.method == "POST":

        message = request.form["message"]

        result = analyze_text(message)

        save_result(
            "TEXT",
            message,
            result
        )

    return render_template(
        "text.html",
        result=result,
        message=message
    )


@app.route("/url", methods=["GET", "POST"])
def url_analyzer():

    result = None
    url = ""

    if request.method == "POST":

        url = request.form["url"]

        result = analyze_url(url)

        save_result(
            "URL",
            url,
            result
        )

    return render_template(
        "url.html",
        result=result,
        url=url
    )


@app.route("/email", methods=["GET", "POST"])
def email_analyzer():

    result = None

    sender = ""
    subject = ""
    body = ""

    if request.method == "POST":

        sender = request.form["sender"]
        subject = request.form["subject"]
        body = request.form["body"]

        result = analyze_email(
            sender,
            subject,
            body
        )

        email_content = (
            "Sender: " + sender +
            "\nSubject: " + subject +
            "\n\n" + body
        )

        save_result(
            "EMAIL",
            email_content,
            result
        )

    return render_template(
        "email.html",
        result=result,
        sender=sender,
        subject=subject,
        body=body
    )


@app.route("/document", methods=["GET", "POST"])
def document_analyzer():

    result = None

    document_name = ""

    if request.method == "POST":

        uploaded_file = request.files.get("document")

        if uploaded_file and uploaded_file.filename:

            document_name = uploaded_file.filename

            file_extension = os.path.splitext(
                uploaded_file.filename
            )[1]

            temporary_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=file_extension
            )

            temporary_file.close()

            uploaded_file.save(
                temporary_file.name
            )

            try:

                result = analyze_document(
                    temporary_file.name
                )

                save_result(
                    "DOCUMENT",
                    document_name,
                    result
                )

            finally:

                os.remove(
                    temporary_file.name
                )

    return render_template(
        "document.html",
        result=result
    )


@app.route("/history")
def history():

    records = get_history()

    return render_template(
        "history.html",
        records=records
    )


@app.route(
    "/delete-history/<int:record_id>",
    methods=["POST"]
)
def delete_history(record_id):

    delete_analysis(record_id)

    return redirect("/history")


if __name__ == "__main__":

    app.run(debug=True)