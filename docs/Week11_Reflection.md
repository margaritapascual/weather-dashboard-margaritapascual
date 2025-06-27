# Week11_Reflection.md

## 🔖 Section 0: Fellow Details

| Field                  | Your Entry                   |
|------------------------|------------------------------|
| Name                   | Margarita Pascual            |
| GitHub Username        | margaritapascual             |
| Preferred Feature Track| Interactive                  |
| Team Interest          | Yes — Project Owner          |

---

## ✍️ Section 1: Week 11 Reflection

### Key Takeaways

- This week helped me see the full scope of the capstone—what’s expected and how we’ll build week by week.
- It reminded me that good planning and file structure upfront saves a lot of stress later.
- I feel more confident knowing I can mix features based on what I’m good at and what I want to get better at.
- The project gives me a chance to apply everything I’ve learned so far in a way that’s creative and useful.
- I also understand that submitting progress every week is part of the growth process—not just about having it “perfect.”

### Concept Connections

- I feel solid when it comes to writing functions, handling files, and working with basic APIs.
- I’m comfortable using `.txt`, `.csv`, and `.json` formats for storing data.
- I need more practice with Tkinter layouts and making things look clean and organized.
- Embedding a chart using matplotlib is still something I’m figuring out.
- I’m still wrapping my head around architecture patterns like MVC, but I’m trying to stay modular from the start.

### Early Challenges

- Making sure the API key is hidden correctly and not committed by accident.
- Deciding where each feature should live and making sure the folders make sense.
- Debugging early API requests and learning how to catch and display errors clearly.
- Figuring out what should go in `config.py` versus `main.py` was a small hurdle at first.

### Support Strategies

- I plan to go to office hours, especially to get feedback on my graphing and layout.
- I’ll keep using Slack if I get stuck—especially with plotting and file I/O.
- Looking at past GitHub capstones helps me see how others organized their projects.
- I’m watching short videos to understand how people structure interactive Python apps.

---

## 🧠 Section 2: Feature Selection Rationale

| #  | Feature Name                 | Difficulty (1–3) | Why You Chose It / Learning Goal                                   |
|----|------------------------------|------------------|---------------------------------------------------------------------|
| 1  | Show Historical Weather Data | 2                | I want to practice storing past weather info and displaying it back to the user. |
| 2  | Plot Temperature Graph       | 3                | I want to push myself to use matplotlib inside a Tkinter window.    |
| 3  | Display Current Conditions & Icons | 2         | I like the idea of showing live data and pairing it with visuals.   |
| –  | Theme Switcher (light/dark toggle)| –          | I just think it adds a nice user touch and helps me explore styling in Tkinter. |

---

## 🗂️ Section 3: High-Level Architecture Sketch

My project follows a simple structure that makes it easy to build and test each feature:

**Flow:**

- User enters location → data is validated
- Weather info is fetched using API
- Info is passed to Tkinter app to show the results
- Features like graphs, icons, and history are plugged into the GUI
- An error handler makes sure things don’t crash if something goes wrong

**Folders/Files:**

- `main.py` runs the app
- `config.py` holds keys and settings
- `/features/` includes:
  - `historical_data.py`
  - `temperature_graph.py`
  - `current_conditions_icons.py`
  - `theme_switcher.py`
- `/data/` saves weather history and other info

---

## 📊 Section 4: Data Model Plan

| File/Table Name        | Format   | Example Row                                 |
|------------------------|----------|----------------------------------------------|
| weather_history.txt    | txt      | 2025-06-09,New Brunswick,78,Sunny            |
| temperature_data.csv   | csv      | 2025-06-09,High:85,Low:68                    |
| alerts_log.json        | json     | {"date": "2025-06-09", "alert": "Heat Wave"} |

---

## 📆 Section 5: Personal Project Timeline (Weeks 12–17)

| Week | Monday         | Tuesday          | Wednesday     | Thursday       | Key Milestone           |
|------|----------------|------------------|----------------|----------------|--------------------------|
| 12   | API setup      | Error handling   | Tkinter shell | Buffer day     | Basic working app        |
| 13   | Feature 1      |                 |               | Integrate      | Feature 1 complete       |
| 14   | Feature 2 start|                | Review & test | Finish         | Feature 2 complete       |
| 15   | Feature 3      | Polish UI       | Error passing | Refactor       | All features complete    |
| 16   | Enhancement    | Docs            | Tests         | Packaging      | Ready-to-ship app        |
| 17   | Rehearse       | Buffer          | Showcase      | –              | Demo Day                 |

---

## ⚠️ Section 6: Risk Assessment

| Risk                    | Likelihood | Impact | Mitigation Plan                                      |
|-------------------------|------------|--------|-------------------------------------------------------|
| API Rate Limit          | Medium     | Medium | Add a delay between calls and save recent results locally. |
| Graph not rendering     | Medium     | High   | Test graph code outside the GUI first before adding it in. |
| Layout issues with Tkinter | Low     | Medium | Break GUI into frames and test one part at a time.     |

---

## 🤝 Section 7: Support Requests

- I’ll need help embedding matplotlib graphs inside my app window.
- Might ask how to pass data across multiple feature files.
- I want feedback on the way I’m handling errors and validation.
- I may need a second pair of eyes on how I’m setting up the dark/light theme toggle.

---
