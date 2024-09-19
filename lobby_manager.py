import tkinter as tk
from tkinter import messagebox, ttk
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

LANES = ['top', 'jungle', 'middle', 'bottom', 'support']

class ChampionScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Champion Scraper")
        self.all_data = {lane: {} for lane in LANES}

        # Create and place widgets
        # name input
        self.name_entry = tk.Entry(root, width=20)
        self.name_entry.grid(row=0, column=0, sticky="ew")

        # lane input
        self.lane_combobox = ttk.Combobox(root, values=LANES, state="readonly", width=10)
        self.lane_combobox.grid(row=0, column=1, sticky="ew")
        self.lane_combobox.set("Select Lane")

        self.search_button = tk.Button(root, text="Start Search", command=self.start_search)
        self.search_button.grid(row=0, column=2, sticky="ew")
        self.root.bind('<Return>', lambda _: self.start_search()) # Bind Enter key to also search

        self.reset_button = tk.Button(root, text="Reset", command=self.reset_data)
        self.reset_button.grid(row=0, column=3, sticky="ew")

        # Listbox for loaded champions
        tk.Label(root, text="Loaded Champions:").grid(row=1, column=0, columnspan=2, sticky="wn")
        self.champion_listbox = tk.Listbox(root, height=7)
        self.champion_listbox.grid(row=1, column=0, columnspan=2, sticky="wn", pady=25)

        # Filter by game count
        tk.Label(root, text="Filter Data by Game Count:").grid(row=1, column=1, columnspan=2, sticky="wn")
        self.game_amount_entry = tk.Entry(root, width=17)
        self.game_amount_entry.grid(row=1, column=1, columnspan=2, sticky="wn", pady=26)
        self.game_amount_entry.insert(0, "200")
        self.filter_button = tk.Button(root, text="Filter", command=self.filter_by_games)
        self.filter_button.grid(row=1, column=1, columnspan=2, sticky="ne", pady=25)

        style = ttk.Style()
        style.configure('Treeview', rowheight=15)

        # Create Treeview for each lane
        self.treeviews = {}
        for i, lane in enumerate(LANES):
            frame = tk.Frame(root)
            frame.grid(row=i + 1, column=4, sticky="nsew")
            tk.Label(frame, text=f"{lane.capitalize()} Lane:").pack(anchor="w")
            tree = ttk.Treeview(frame, columns=("Name", "Popularity", "Games", "Win Rate Difference"), show='headings')
            tree.pack(expand=True, fill='both')
            tree.heading("Name", text="Name")
            tree.heading("Popularity", text="Popularity")
            tree.heading("Games", text="Games")
            tree.heading("Win Rate Difference", text="Win Rate Difference")
            self.treeviews[lane] = tree

    def start_search(self):
        champion_name = self.name_entry.get()
        lane = self.lane_combobox.get().lower()

        # Find the full champion name
        full_name = next((name for name in CHAMPION_NAMES if champion_name.lower() in name.lower()), None)

        # Show error if the champion is not found
        if not full_name:
            messagebox.showerror("Error", f"Champion name '{champion_name}' not found.")
            return
        
        # Clean input fields
        self.name_entry.delete(0, tk.END)

        # Extract data from json file
        filename = f"data/{full_name}_{lane}.json".replace(" ", "_")
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading data from {filename} {e}")
            return

        # Add the champion to the loaded list
        self.champion_listbox.insert(tk.END, f"{full_name}_{lane}")

        for lane in self.all_data:
            for name, new_data in data.get(lane, {}).items():
                if name in self.all_data[lane]:
                    existing_data = self.all_data[lane][name]
                    self.all_data[lane][name] = self.integrate_data(existing_data, new_data)
                else:
                    self.all_data[lane][name] = new_data

        self.update_GUI()

    def reset_data(self):
        self.all_data = {lane: {} for lane in LANES}
        self.champion_listbox.delete(0, tk.END)

        for tree in self.treeviews.values():
            for item in tree.get_children():
                tree.delete(item)

    def update_GUI(self):
        for lane, data_dict in self.all_data.items():
            tree = self.treeviews[lane]
            for item in tree.get_children():
                tree.delete(item)
            
            for name, details in sorted(data_dict.items(), key=lambda item: float(item[1].get('win_rate_diff', 0.0)), reverse=False):
                tree.insert("", "end", values=(
                    name,
                    details["popularity"],
                    details["games"],
                    details["win_rate_diff"]
                ))
    def filter_by_games(self):
        try:
            min_games = int(self.game_amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for games.")
            return

        # Filter the data
        filtered_data = {lane: {} for lane in LANES}
        for lane, champions in self.all_data.items():
            for name, details in champions.items():
                if int(details["games"]) >= min_games:
                    filtered_data[lane][name] = details

        # Update the all_data with the filtered result and refresh the GUI
        self.all_data = filtered_data
        self.update_GUI()


    def integrate_data(self, existing_data, new_data):
        existing_games = int(existing_data.get("games", '0'))
        new_games = int(new_data.get("games", '0'))
        total_games = existing_games + new_games

        existing_win_rate = float(existing_data.get("win_rate", '0'))
        new_win_rate = float(new_data.get("win_rate", '0'))

        weighted_win_rate = (
            ((existing_win_rate * existing_games) + (new_win_rate * new_games)) 
            / total_games if total_games > 0 else 0
        )
        
        win_rate_diff = round(weighted_win_rate - 50, 2)
        
        total_popularity = float(existing_data.get("popularity", '0')) + \
                        float(new_data.get("popularity", '0'))

        existing_data.update({
            "games": f"{total_games}",
            "win_rate_diff": f"{win_rate_diff:.2f}",
            "popularity": f"{total_popularity:.2f}"
        })

        return existing_data


if __name__ == "__main__":
    root = tk.Tk()
    app = ChampionScraperApp(root)
    root.mainloop()
