# LoLalytics Scraper & Counters Finder

**LSCF** is a Python script designed to help you find the best champion choices in *League of Legends* by scraping champion data from the *LoLalytics* website. The data is then used to identify the best counter-picks based on the enemy team's composition.

## Features
- Scrapes champion data from *Lolalytics* into JSON files.
- Allows you to input enemy champion picks and receive suggestions for the best counter-picks based on real-time data.

## Usage

### Part 1: Scraping Data

1. **Run the scraper:**
   The script will open a browser (using Selenium), navigate to the *Lolalytics* page, and retrieve relevant data for all champions.
   
   ```bash
   python scraper.py X
   ```
   - X should be an integer between 0 and 5.
   - 0 means data for all champions will be scraped.
   - Numbers between 1 and 5 represent subsets of champions, allowing you to split the scraping into 5 simultaneous scripts.

   - The data will be stored in a structured format for easy access later.

### Part 2: Managing Data in the Game Lobby

1. **Run the lobby manager:**
   ```bash
   python lobby_manager.py
   ```

2. **Input enemy champions:**
   You can input the enemy team's champions as they are selected. The script will recommend optimal champions for your team to pick based on win rate and counter-pick data.
