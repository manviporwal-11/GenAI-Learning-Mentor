from flask import Flask, request, jsonify
from flask_cors import CORS

from rag_engine import ask_rag
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="frontend")
CORS(app)
@app.route("/")
def home():
    return render_template("dashboard.html")

@app.route("/api/mentor", methods=["POST"])
def mentor():

    try:

        data = request.get_json()

        question = data.get("question", "").strip()
        level = data.get("level", "Beginner")
        learning_style = data.get(
            "learning_style",
            "Simple Explanation"
        )
        subject = data.get(
            "subject",
            "Operating System"
        )

        if not question:

            return jsonify({
                "success": False,
                "error": "Please enter a question."
            }), 400


        answer = ask_rag(
            question,
            level,
            learning_style,
            subject
        )


        return jsonify({
            "success": True,
            "answer": answer
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "GenVI AI backend is running"
    })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )