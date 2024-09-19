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
import argparse

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

LANES = ['top', 'jungle', 'middle', 'bottom', 'support']

def generate_url(name, lane):
    formatted_name = name.lower()
    return f"https://lolalytics.com/lol/{formatted_name}/build/?lane={lane}&tier=diamond_plus"

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

def scrape_web(driver, url):
    driver.get(url)

    # Scroll down the page slightly to ensure content is loaded
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    for _ in range(3):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.25)

    # Find the element containing "Pick Rate"
    pick_rate_value = None
    try:
        pick_rate_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Pick Rate')]/preceding-sibling::div[contains(@class, 'font-bold')]"))
        )
        pick_rate_text = pick_rate_element.text
        pick_rate_value = float(pick_rate_text.strip('%'))
        
    except Exception as e:
        # Resource not found
        print(f"Error finding pick rate")

    # If pick rate is not found or is low, skip
    if pick_rate_value is None or pick_rate_value < 0.5:
        print(f"Skip, {url}")
        return

    lane_data = {lane: {} for lane in LANES}
    for i, lane in enumerate(LANES, start=2):
        xpath = f"/html/body/main/div[6]/div[1]/div[{i}]/div[2]"
        parent_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))

        for _ in range(6):
            # Get all the children
            children = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, f"{xpath}/div[1]/*"))
            )

            for element in children:
                data = format_data(element)
                name = data.get("Name")
                
                if name != 'error' and name != 'N/A' and name not in lane_data[lane]:
                    lane_data[lane][name] = data
            
            # Scroll the parent element sideways to load more elements
            driver.execute_script("arguments[0].scrollLeft += 500;", parent_element)
            time.sleep(0.5)

    return lane_data


def save_data(full_name, data, lane):
    """Save the champion's data to a file in the /data directory."""
    filename = f"data/{full_name}_{lane}.json".replace(" ", "_")

    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Champion data saved to {filename}")
    except IOError as e:
        print(f"Error saving data to file: {e}")

def scrape_and_save(driver, full_name):
    for lane in LANES:
        url = generate_url(full_name, lane)

        filename = f"data/{full_name}_{lane}.json".replace(" ", "_")
        
        if os.path.exists(filename):
            print(f"Skip, Data for {full_name} {lane} already exists.")
            continue
        
        data = scrape_web(driver, url)
        
        # if not empty save
        if data:
            print(f"Data extracted for {full_name} {lane} lane")
            save_data(full_name, data, lane)
        

def scrape_and_save_subset(driver, champion_names_subset):
    for champion_name in champion_names_subset:
        scrape_and_save(driver, champion_name)

def split_champion_names(fifth):
    total_names = len(CHAMPION_NAMES)
    part_size = total_names // 5

    start_index = fifth * part_size
    if fifth == 4:  # The last part gets any remainder names
        champion_names_subset = CHAMPION_NAMES[start_index:]
    else:
        champion_names_subset = CHAMPION_NAMES[start_index:start_index + part_size]

    return champion_names_subset


# If errors input your github token
# os.environ['GH_TOKEN'] = "_"

def main(fifth):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    try:
        if fifth == 0:
            scrape_and_save_subset(driver, CHAMPION_NAMES)
        else:
            champion_names_subset = split_champion_names(fifth-1)
            scrape_and_save_subset(driver, champion_names_subset)
    finally:
        driver.quit()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run scraping for a specific subset of champions.")
    parser.add_argument('fifth', type=int, choices=range(6), help="Specify which 1/5th of the list to process (0 for all, 1-5 for subsets).")
    args = parser.parse_args()
    main(args.fifth)
