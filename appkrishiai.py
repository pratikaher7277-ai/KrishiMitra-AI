from dotenv import load_dotenv
import google.generativeai as genai
import os

from flask import Flask, render_template, request

app = Flask(__name__)

# -------------------------
# ENV + GEMINI
# -------------------------

load_dotenv()
print("KEY=", os.getenv("GEMINI_API_KEY"))
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# -------------------------
# APP CONFIG
# -------------------------

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

crop_registered = False


# -------------------------
# AI FUNCTION
# -------------------------

def analyze_crop_disease():

    prompt = """
You are Krishimitra AI.

Analyze uploaded crop condition.

Return in format:

Disease:
Treatment:
Water Requirement:
Yield Impact:

Keep response simple and farmer friendly.
"""

    response = model.generate_content(
        prompt
    )

    return response.text


# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/crop")
def crop():

    global crop_registered

    if crop_registered:

        return render_template(
            "result.html"
        )

    return render_template(
        "crop_journey.html"
    )


@app.route("/result")
def result():

    global crop_registered

    crop_registered = True

    return render_template(
        "result.html"
    )


@app.route(
    "/doctor",
    methods=["GET", "POST"]
)

def doctor():

    if request.method == "POST":

        image = request.files["crop_image"]

        if image:

            save_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                image.filename
            )

            image.save(save_path)

            ai_result = analyze_crop_disease()

            return render_template(
                "doctor_result.html",
                result=ai_result
            )

    return render_template(
        "doctor.html"
    )


@app.route("/market")
def market():

    return render_template(
        "market.html"
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )