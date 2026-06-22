from dotenv import load_dotenv
from google import genai
from PIL import Image
import os
from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = "krishimitra"

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

crop_registered = False

def analyze_crop_disease(image_path):
    image = Image.open(image_path)
    prompt = """You are Krishimitra AI. Analyze uploaded crop image. Return ONLY:
Disease:
Treatment:
Water Requirement:
Yield Impact:
Keep answer short."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, prompt]
    )
    return response.text

def market_ai(crop, district, qty, grade):
    try:
        revenue = int(qty) * 3000
    except:
        revenue = 0
    return f"Crop: {crop}\n\nQuality Grade:\n{grade}\n\nExpected Demand:\nHigh\n\nRecommended Market:\n{district} Main Market\n\nExpected Price:\n₹2800–₹3400 per quintal\n\nSelling Advice:\nMarket demand looks positive.\nConsider selling within 3–5 days.\n\nEstimated Revenue:\n₹{revenue}"

@app.route("/")
def home():
    farmer_name = session.get("farmer_name", "Farmer")
    location = session.get("location", "Nashik")
    weather_info = f"{location} • 31°C • Rain chance low • Best irrigation time: early morning"
    return render_template("index.html", farmer_name=farmer_name, weather_info=weather_info)

@app.route("/crop", methods=["GET", "POST"])
def crop():
    if request.method == "POST":
        crop_type = request.form.get("crop_type", "Onion")
        variety = request.form.get("variety", "N-53")
        return render_template(
            "result.html",
            crop=crop_type,
            variety=variety,
            stage="Growth",
            plan1="Check soil moisture",
            plan2="Irrigation Required",
            plan3="Apply Nutrients",
            sug1="Moderate irrigation recommended",
            sug2="Nitrogen monitoring advised"
        )
    return render_template("crop_journey.html")

@app.route("/result")
def result():
    return render_template(
        "result.html",
        crop="Onion",
        variety="N-53",
        stage="Growth",
        plan1="Check soil moisture",
        plan2="Irrigation Required",
        plan3="Apply Nutrients",
        sug1="Moderate irrigation recommended",
        sug2="Nitrogen monitoring advised"
    )

@app.route("/doctor", methods=["GET", "POST"])
def doctor():
    if request.method == "POST":
        image = request.files.get("crop_image")
        if image:
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(save_path)
            result = analyze_crop_disease(save_path)
            return render_template("doctor_result.html", result=result)
    return render_template("doctor.html")

@app.route("/market")
def market():
    return render_template("market.html")

@app.route("/market-result")
def market_result():
    crop = request.args.get("crop")
    district = request.args.get("district")
    qty = request.args.get("qty")
    grade = request.args.get("grade")
    result = market_ai(crop, district, qty, grade)
    return render_template("market_result.html", result=result)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        name = request.form.get("farmer_name")
        loc = request.form.get("location")
        if name:
            session["farmer_name"] = name
        if loc:
            session["location"] = loc
        return redirect("/")
    return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True)