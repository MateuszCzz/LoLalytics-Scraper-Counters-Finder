# LoLalytics Scraper & Counters Finder

**LSCF** is a Python script designed to help you find best champion choice in *League of Legends* by scraping champion data from the *LoLalytics* website and using that data to identify the best counter-picks based on your enemy's teamcomp.

## Features
- Scrapes champion data from *Lolalytics*, into json files.
- Allows you to input enemy champion picks and get suggestions for the best counter-picks based on real-time data.

## Usage

### Part 1: Scraping Data

1. **Run the scraper:**
   The script will open a browser (using Selenium), navigate to the *Lolalytics* page, and retrieve relevant data for all champions.
   
   ```bash
   python scraper.py
   ```
   - You can choose to either run one big long blob of champions or run 5 scripts split into equal parts.
   - The data will be stored in a structured format (e.g., JSON) for easy access during the game lobby phase.

### Part 2: Managing Data in the Game Lobby

1. **Run the lobby manager:**
   ```bash
   python lobby_manager.py
   ```

2. **Input enemy champions:**
   You can input the enemy team's champions as they are selected. The script will recommend optimal champions for your team to pick based on win rate and counter-pick data.
