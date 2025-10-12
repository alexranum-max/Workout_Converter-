import tkinter as tk
import Whats_on_Zwift_Scraper as Scraper
import subprocess
import flask

app = flask.Flask(__name__)

root = tk.Tk()
root.title("Workout Creator")
Width, Height = 400, 170
center_x = (root.winfo_screenwidth() - Width) // 2
center_y = (root.winfo_screenheight() - Height) // 2
root.geometry(f"{Width}x{Height}+{center_x}+{center_y}")

label = tk.Label(root, text="Workout must be from: https://whatsonzwift.com/workouts/", font=("Arial", 12))
label.pack(pady=5)

label = tk.Label(root, text="Enter Workout URL Below", font=("Arial", 12))
label.pack(pady=2)

# Create an Entry widget
URL = tk.Entry(root, width=30)
URL.pack(pady=10)

# Optional: Get the text from the Entry widget
def get_entry_text():
    result = Scraper.Scrape(URL.get())
    get_button.config(text="Download Another Workout?")
    URL.delete(0, tk.END)
    downloaded_label.config(text=result)

get_button = tk.Button(root, text="Download Workout", command=get_entry_text)
get_button.pack()

downloaded_label = tk.Label(root, text="", font=("Arial", 10))
downloaded_label.pack(pady=2)

@app.route("/")
def home():
    return "Welcome to the Workout Creator!"

@app.route("/download", methods=["POST"])
def download_workout():
    url = flask.request.form["url"]
    result = Scraper.Scrape(url)
    return {"message": result}

root.mainloop()