Hey there, I am building this agent using langgraph to learn langgraph, so below is the PRD. I want you to build this with the purpose in mind which is to learn langgraph. Hence ensure the code is explainable, well commented and use a beginner friendly/understandable approach. Be ready to later give a walkthrough of the code. Let's build. 

⸻

🧥 Problem Statement: LangGraph-Powered AI agent powered by a simple Web App

🎯 Goal

Create a LangGraph-based AI stylist that:
	•	Recommends personalized outfits based on user inputs like height, gender, mood, occasion, and current weather (based on selected Indian state)
	•	Collects user feedback (rating 1–10)
	•	Improves recommendations in a loop (max 5 times) until a rating ≥ 7 is achieved
	•	Provides a transparent, running log of all internal LangGraph decisions and steps

⸻

🧩 Inputs

Step 1 – Initial Inputs:
	•	Height (number)
	•	Gender (dropdown: Male / Female / Other)

Step 2 – Contextual Inputs:
	•	Location (dropdown: Indian states)
	•	Occasion (dropdown: Party / Date / Formal / Daily Casual / Vacation)
	•	Mood (dropdown: Confident / Minimal / Romantic / Bold / Relaxed / Streetwear)

⸻

💡 Output
	•	A natural language outfit recommendation generated via LLM
	•	Feedback prompt: “Rate this recommendation (1–10)”
	•	Loop and regenerate recommendation if rating < 7, up to 5 times
	•	Final congratulatory message once a satisfactory outfit is found

⸻

🔁 Flow Summary

Start
 ↓
Ask for Height + Gender
 ↓
Ask for Location + Occasion + Mood
 ↓
Fetch weather for location
 ↓
Generate outfit recommendation using LLM
 ↓
Ask user for rating (1–10)
 ↓
IF rating >= 7:
    → Display final message: "Perfect outfit found 🎉"
ELSE:
    → Retry recommendation (max 5 attempts)
        → If still < 7 after 5 attempts: "Sorry, we tried our best 💔"



⸻

⚙️ LangGraph Nodes (Example)

Node ID	Function
collect_base_info	Ask height + gender
collect_context	Ask location + occasion + mood
fetch_weather	Simulate API call for weather based on location
generate_outfit	Use LLM to suggest an outfit using context + weather
rate_outfit	Ask for user rating
retry_or_finish	Decide to retry (if < 7 and attempts < 5) or finish
final_message	Show final congratulation or exit message



⸻

🖥️ Frontend Requirements
	•	Simple web interface (can be Streamlit or basic React/Vite)
	•	Steps appear one-by-one (like a wizard flow)
	•	Each recommendation is shown with a rating slider or input box
	•	Live, running log pane showing:
	•	LangGraph node currently executing
	•	Any LLM call (with input/output)
	•	Decisions (e.g., “Retrying because rating = 6”)
	•	Final output summary

⸻

📊 Weather Logic (Simulated)
	•	 use an open API like OpenWeatherMap (optional)

⸻

🧪 Scope of MVP
	•	Full LangGraph-based backend logic
	•	Web frontend with input fields and live log
	•	Rating-based decision control (retry/max attempts)
	•	LLM-generated outfit suggestion using prompt engineering

⸻

