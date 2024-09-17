import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import concurrent.futures
import threading

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
    "Rell", "RenataGlasc", "Renekton", "Rengar", "Riven", "Rumble", "Ryze", "Samira", "Sejuani",
    "Senna", "Seraphine", "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir",
    "Skarner", "Smolder", "Sona", "Soraka", "Swain", "Sylas", "Syndra", "TahmKench", "Taliyah",
    "Talon", "Taric", "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere", "TwistedFate",
    "Twitch", "Udyr", "Urgot", "Varus", "Vayne", "Veigar", "VelKoz", "Vex", "Vi", "Viego",
    "Viktor", "Vladimir", "Volibear", "Warwick", "Wukong", "Xayah", "Xerath", "XinZhao",
    "Yasuo", "Yone", "Yorick", "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean", "Zyra", "Zoe"
]
LANES = ['top', 'jng', 'mid', 'bot', 'sup']

class ChampionScraperApp:
    def __init__(self, root):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.root = root
        self.root.title("Champion Scraper")
        
        self.all_data = {lane: {} for lane in LANES}
        self.data_lock = threading.Lock()

        # Create and place widgets
        self.name_entry = tk.Entry(root, width=15)
        self.name_entry.grid(row=0, column=0, columnspan=2, padx=(0, 50), sticky="ew")

        self.search_button = tk.Button(root, text="Start Search", command=self.start_search)
        self.search_button.grid(row=0, column=0, padx=(120, 0), sticky="ew")

        self.reset_button = tk.Button(root, text="Reset", command=self.reset_data)
        self.reset_button.grid(row=0, column=1, padx=(0, 0), sticky="ew")

    

        style = ttk.Style()
        style.configure('Treeview', rowheight=15)
        # Create Treeview for each lane
        self.treeviews = {}
        for i, lane in enumerate(LANES):
            frame = tk.Frame(root)
            frame.grid(row=i, column=2, sticky="nsew")
            tk.Label(frame, text=f"{lane.capitalize()} Lane:").pack(anchor="w")
            tree = ttk.Treeview(frame, columns=("Name", "Popularity", "Games", "Win Rate Difference"), show='headings')
            tree.pack(expand=True, fill='both')
            tree.heading("Name", text="Name")
            tree.heading("Popularity", text="Popularity")
            tree.heading("Games", text="Games")
            tree.heading("Win Rate Difference", text="Win Rate Difference")
            self.treeviews[lane] = tree

        # Bind Enter key to the search function
        self.root.bind('<Return>', lambda event: self.start_search())

    def format_data(self, element):
        """Format data from a given web element."""
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

    def find_full_name(self, short_name):
        """Find the full champion name from a partial input."""
        return next((name for name in CHAMPION_NAMES if short_name.lower() in name.lower()), None)

    def generate_url(self, name):
        """Generate the champion's Lolalytics URL."""
        formatted_name = name.lower().replace(' ', '-')
        return f"https://lolalytics.com/lol/{formatted_name}/build/?tier=diamond_plus"

    def extract_data_role(self, url):
        """Extract data for all roles from the given URL."""
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        driver.get(url)

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "_wrapper_hthxe_1")))
        body = driver.find_element(By.CSS_SELECTOR, 'body')

        for _ in range(2):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

        lane_data = {lane: {} for lane in LANES}

        for i, lane in enumerate(LANES, start=2):
            xpath = f"/html/body/main/div[6]/div[1]/div[{i}]/div[2]/div[1]"
            parent_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            children = parent_element.find_elements(By.XPATH, "./*")

            for element in children:
                data = self.format_data(element)
                name = data.get("Name")
                if name != 'error' and name != 'N/A':
                    lane_data[lane][name] = data

        driver.quit()

        for lane in lane_data:
            lane_data[lane] = dict(sorted(lane_data[lane].items(), key=lambda item: item[1]['win_rate_diff'], reverse=True))

        return lane_data

    def integrate_data(self, existing_data, new_data):
        """Integrate new data into existing data."""
        def parse_number(value):
            return int(value.replace(',', '')) if value != 'N/A' else 0

        def parse_percentage(value):
            return float(value.replace('%', '')) if value != 'N/A' else 0

        existing_games = parse_number(existing_data.get("games", '0'))
        new_games = parse_number(new_data.get("games", '0'))
        total_games = existing_games + new_games

        existing_win_rate = parse_percentage(existing_data.get("win_rate", '0'))
        new_win_rate = parse_percentage(new_data.get("win_rate", '0'))

        weighted_win_rate = ((existing_win_rate * existing_games) + (new_win_rate * new_games)) / total_games if total_games > 0 else 0
        win_rate_diff = round(weighted_win_rate - 50, 2)

        total_popularity = parse_percentage(existing_data.get("popularity", '0')) + parse_percentage(new_data.get("popularity", '0'))

        existing_data.update({
            "games": f"{total_games:,}",
            "win_rate": f"{weighted_win_rate:.2f}%" if total_games > 0 else "N/A",
            "win_rate_diff": f"{win_rate_diff:.2f}" if total_games > 0 else "N/A",
            "popularity": f"{total_popularity:.2f}%" if total_popularity > 0 else "N/A"
        })

        return existing_data

    @staticmethod
    def safe_float(value):
        """Safely convert a value to float, printing a warning if conversion fails."""
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        try:
            return float(value)
        except ValueError:
            print(f"Warning: Value '{value}' could not be converted to float.")
            return 0.0


    def update_results(self):
        """Update the GUI with the results."""
        with self.data_lock:
            all_data = self.all_data.copy()

        for lane, data_dict in all_data.items():
            tree = self.treeviews[lane]
            for item in tree.get_children():
                tree.delete(item)
            
            for name, details in sorted(data_dict.items(), key=lambda item: self.safe_float(item[1].get('win_rate_diff', 0.0)), reverse=False):
                tree.insert("", "end", values=(
                    name,
                    details["popularity"],
                    details["games"],
                    details["win_rate_diff"]
                ))

    def start_search(self):
        """Start the search process."""
        champion_name = self.name_entry.get()
        if not champion_name:
            return

        full_name = self.find_full_name(champion_name)
        if not full_name:
            messagebox.showerror("Error", f"Champion name '{champion_name}' not found.")
            return

        url = self.generate_url(full_name)
        self.executor.submit(self.search_and_update, url)

    def search_and_update(self, url):
        """Perform the search and update the results in the main thread."""
        print("Starting search and update process...")
        self.name_entry.delete(0, tk.END)
        # Extract data from the URL
        data = self.extract_data_role(url)
        print(f"Data extracted")

        with self.data_lock:
            for lane in self.all_data:
                for name, new_data in data[lane].items():
                    if name in self.all_data[lane]:
                        existing_data = self.all_data[lane][name]
                        self.all_data[lane][name] = self.integrate_data(existing_data, new_data)
                    else:
                        self.all_data[lane][name] = new_data

        # Update GUI with the processed data
        self.root.after(0, self.update_results)
        print("Update process completed.")

    def reset_data(self):
        """Reset all data and clear the result text areas."""
        with self.data_lock:
            self.all_data = {lane: {} for lane in LANES}
        for tree in self.treeviews.values():
            for item in tree.get_children():
                tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChampionScraperApp(root)
    root.mainloop()