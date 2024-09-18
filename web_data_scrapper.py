from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import os

CHAMPION_NAMES = [
    "Ahri", "Aatrox", "Akali", "Akshan", "Alistar", "Amumu", "Anivia", "Annie",
    "Aphelios", "Ashe", "AurelionSol", "Aurora", "Azir", "Bard", "BelVeth", "Blitzcrank",
    "Brand", "Braum", "Briar", "Caitlyn", "Camille", "Cassiopeia", "ChoGath", "Corki",
    "Darius", "Diana", "DrMundo", "Draven", "Ekko", "Elise", "Evelynn", "Ezreal", "Fiddlesticks",
    "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar", "Gragas", "Graves", "Gwen",
    "Hecarim", "Heimerdinger", "Hwei", "Illaoi", "Irelia", "Ivern", "Janna", "JarvanIV",
    "Jax", "Jayce", "Jhin", "Jinx", "KSante", "KaiSa", "Kalista", "Karma", "Karthus", "Kassadin",
    "Katarina", "Kayle", "Kayn", "Kennen", "KhaZix", "Kindred", "Kled", "KogMaw", "LeBlanc",
    "LeeSin", "Leona", "Lillia", "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar",
    "Maokai", "MasterYi", "Milio", "MissFortune", "Mordekaiser", "Morgana", "Naafiri", "Nami",
    "Nasus", "Nautilus", "Neeko", "Nidalee", "Nilah", "Nocturne", "Nunu", "Olaf", "Orianna",
    "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn", "Rakan", "Rammus", "RekSai",
    "Rell", "Renata", "Renekton", "Rengar", "Riven", "Rumble", "Ryze", "Samira", "Sejuani",
    "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir",
    "Skarner", "Smolder", "Sona", "Soraka", "Swain", "Sylas", "Syndra", "TahmKench", "Taliyah",
    "Talon", "Taric", "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere", "TwistedFate",
    "Twitch", "Udyr", "Urgot", "Varus", "Vayne", "Veigar", "VelKoz", "Vex", "Vi", "Viego",
    "Viktor", "Vladimir", "Volibear", "Warwick", "Wukong", "Xayah", "Xerath", "XinZhao",
    "Yasuo", "Yone", "Yorick", "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean", "Zyra", "Zoe"
]

LANES = [
     'top', 'jng', 'mid', 'bot', 'sup'
     ]

def generate_url(name):
        formatted_name = name.lower()
        return f"https://lolalytics.com/lol/{formatted_name}/build/?tier=diamond_plus"

def format_data(element):
        text = element.text.replace('\n', ' ').strip().split()
        img_elements = element.find_elements(By.TAG_NAME, 'img')
        img_alt = img_elements[0].get_attribute('alt') if img_elements else 'error'

        try:
            win_rate_value = float(text[0].replace('%', ''))
            win_rate_diff = round(win_rate_value - 50, 2)
        except (ValueError, IndexError):
            win_rate_diff = 'N/A'

        return {
            "Name": img_alt,
            "win_rate": text[0] if len(text) >= 1 else 'N/A',
            "popularity": text[3] if len(text) >= 5 else 'N/A',
            "games": text[4] if len(text) >= 5 else 'N/A',
            "win_rate_diff": win_rate_diff
        }

def scrape_web(url):
        driver = webdriver.Firefox( service=FirefoxService(GeckoDriverManager().install()))
        driver.get(url)

        body = driver.find_element(By.CSS_SELECTOR, 'body')
        for _ in range(2):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.1)

        lane_data = {lane: {} for lane in LANES}

        for i, lane in enumerate(LANES, start=2):
            xpath = f"/html/body/main/div[6]/div[1]/div[{i}]/div[2]/div[1]"
            parent_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            children = parent_element.find_elements(By.XPATH, "./*")

            for element in children:
                data = format_data(element)
                name = data.get("Name")
                if name != 'error' and name != 'N/A':
                    lane_data[lane][name] = data

        driver.quit()

        for lane in lane_data:
            lane_data[lane] = dict(sorted(lane_data[lane].items(), key=lambda item: item[1]['win_rate_diff'], reverse=True))

        return lane_data

def save_data(full_name, data):
    """Save the champion's data to a file in the /data directory."""
    # Create a valid filename by removing invalid characters
    filename = f"data/{full_name}.json".replace(" ", "_")

    # Open the file and write the data
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Champion data saved to {filename}")
    except IOError as e:
        print(f"Error saving data to file: {e}")


def scrape_and_save(full_name):
    url = generate_url(full_name)

    filename = f"data/{full_name}.json".replace(" ", "_")
    
    if os.path.exists(filename):
        print(f"Data for {full_name} already exists. Skipping...")
        return

    data = scrape_web(url)
    print(f"Data extracted for " + full_name)

    save_data(full_name, data)
    print(f"Data saved to {full_name}.json")

if not os.path.exists('data'):
    os.makedirs('data')

def scrape_and_save_subset(champion_names_subset):
    for champion_name in champion_names_subset:
        scrape_and_save(champion_name)

def split_champion_names(fifth):
    total_names = len(CHAMPION_NAMES)
    part_size = total_names // 5

    # Handle the case where the list size isn't perfectly divisible by 5
    start_index = fifth * part_size
    if fifth == 4:  # The last part gets any remainder names
        champion_names_subset = CHAMPION_NAMES[start_index:]
    else:
        champion_names_subset = CHAMPION_NAMES[start_index:start_index + part_size]

    return champion_names_subset

os.environ['GH_TOKEN'] = "_"
# fifth = 0  # Change this to 0, 1, 2, 3, or 4 to process different 1/5th of the list
# champion_names_subset = split_champion_names(fifth)
# scrape_and_save_subset(CHAMPION_NAMES)
