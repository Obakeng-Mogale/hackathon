from flask import Flask, render_template, jsonify
import main  # import your algorithm file

app = Flask(__name__, template_folder=".")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run", methods=["GET"])
def run_algorithm():
    # Call the function inside main.py
    # note = main.generate_medical_note()
    note = main.main_("test_medicalAudio.mp3")
    # main.main_()
    return jsonify({"note": note})

if __name__ == "__main__":
    app.run(debug=True)