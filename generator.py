import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
from itertools import permutations, combinations
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
import math
from collections import defaultdict
import pandas as pd


# Constants
POSITIONS = ['top', 'jgl', 'mid', 'bot', 'sup']
RANKS = ['iron', 'bronze', 'silver', 'gold', 'platinum', 'emerald', 'diamond', 'master', 'grandmaster', 'challenger']
SERVERS = ['others', 'korea', 'china']
HIGH_SKILL_SERVERS = {'korea', 'china'}

RANKS_POINT_DICT = {
    'challenger' : {
        'top': 46, 
        'jgl': 51, 
        'mid': 50, 
        'bot': 44, 
        'sup': 43
    },
    'grandmaster' : {
        'top': 43, 
        'jgl': 47, 
        'mid': 46, 
        'bot': 40, 
        'sup': 40
    },
    'master' : {    #Diamond 1
        'top': 39, 
        'jgl': 47, 
        'mid': 46, 
        'bot': 40, 
        'sup': 40
    },
    'diamond' : {   #Diamond 3
        'top': 31, 
        'jgl': 34, 
        'mid': 34, 
        'bot': 28, 
        'sup': 30
    },
    'emerald' : {   #mean(Diamond 4 + Platinum1)
        'top': 28, 
        'jgl': 31, 
        'mid': 31, 
        'bot': 25, 
        'sup': 27
    }, 
    'platinum': {   #Platinum3
        'top': 23, 
        'jgl': 25, 
        'mid': 24, 
        'bot': 21, 
        'sup': 23
    },  
    'gold' : {   #Gold 2
        'top': 19, 
        'jgl': 17, 
        'mid': 16, 
        'bot': 16, 
        'sup': 19
    }, 
    'silver': {   #Silver 2
        'top': 13, 
        'jgl': 8, 
        'mid': 10, 
        'bot': 8, 
        'sup': 13
    }, 
    'bronze': {   # Silver3 -3 
        'top': 8, 
        'jgl': 4, 
        'mid': 8, 
        'bot': 7, 
        'sup': 11
    }, 
    'iron': {   # Silver3 -3 
        'top': 8, 
        'jgl': 4, 
        'mid': 8, 
        'bot': 7, 
        'sup': 11
    }
}

#####

@dataclass
class PositionPreference:
    main_roles: List[str]
    secondary_roles: List[str]
    tertiary_roles: List[str]

    def __post_init__(self):
        # Validate that each position appears only once
        all_positions = self.main_roles + self.secondary_roles + self.tertiary_roles
        if len(all_positions) != len(set(all_positions)):
            raise ValueError("A position cannot appear in multiple tiers")
        
        # Validate that all positions are valid
        for pos in all_positions:
            if pos not in POSITIONS:
                raise ValueError(f"Invalid position: {pos}")

    def get_all_positions(self) -> List[str]:
        """Return all positions the player can play"""
        return list(set(self.main_roles + self.secondary_roles + self.tertiary_roles))

    def get_position_tier(self, position: str) -> int:
        """
        Returns the tier of the position (1 for main, 2 for secondary, 3 for tertiary)
        Returns -1 if position is not in any tier
        """
        if position in self.main_roles:
            return 1
        elif position in self.secondary_roles:
            return 2
        elif position in self.tertiary_roles:
            return 3
        return -1

    def __str__(self):
        return (f"Main: {', '.join(self.main_roles) if self.main_roles else 'None'} | "
                f"Secondary: {', '.join(self.secondary_roles) if self.secondary_roles else 'None'} | "
                f"Tertiary: {', '.join(self.tertiary_roles) if self.tertiary_roles else 'None'}")

#####
    
@dataclass
class Player:
    name: str
    rank: str
    position_preference: PositionPreference
    server: str
    order_capable: bool = False

    @property
    def rank_points(self) -> float:
        base_points = RANKS.index(self.rank.lower()) + 1
        
        server_bonus = 1 if self.server.lower() in HIGH_SKILL_SERVERS else 0
    
        return base_points + server_bonus
    
    def rank_points(self, assigned_position: str) -> float:
        tier = self.position_preference.get_position_tier(assigned_position)        
        server_bonus = 1 if self.server.lower() in HIGH_SKILL_SERVERS else 0
        weighted_points = 0.0
        if tier == 1:  # Main role
            weighted_points = RANKS_POINT_DICT[self.rank][self.position_preference.main_roles[0]]
        elif tier == 2:  # Secondary role
            weighted_points = RANKS_POINT_DICT[self.rank][self.position_preference.secondary_roles[0]]
        elif tier == 3:  # Tertiary role
            weighted_points = RANKS_POINT_DICT[self.rank][self.position_preference.tertiary_roles[0]]
        
        return server_bonus + weighted_points
    
    def position_penalty(self, assigned_position: str) -> float:
        tier = self.position_preference.get_position_tier(assigned_position)
        if tier == 1:  # Main role
            return +2.5
        elif tier == 2:  # Secondary role
            return -1.5
        elif tier == 3:  # Tertiary role
            return -5.0
        return float('-inf')  # Position not in any tier
    
    def position_penalty_advanced(self, assigned_position: str) -> float:
        tier = self.position_preference.get_position_tier(assigned_position)
        if tier == 1:  # Main role
            return float(self.rank_points(assigned_position) * 0.02)
        elif tier == 2:  # Secondary role
            return float(self.rank_points(assigned_position) * -0.02)
        elif tier == 3:  # Tertiary role
            return float(self.rank_points(assigned_position) * -0.30)
        return float('-inf')  # Position not in any tier

    @property
    def order_points(self) -> float:
        return 0.5 if self.order_capable else 0

    @property
    def position_flexibility(self) -> int:
        """Return the total number of positions the player can play"""
        return len(self.position_preference.get_all_positions())
#####

def create_position_preference(positions: Dict[str, List[str]]) -> PositionPreference:
    """
    Create a PositionPreference object from a dictionary of positions.
    
    :param positions: A dictionary with keys 'main', 'secondary', 'tertiary'
                     containing lists of positions for each tier
    :return: A PositionPreference object
    """
    return PositionPreference(
        main_roles=positions.get('main', []),
        secondary_roles=positions.get('secondary', []),
        tertiary_roles=positions.get('tertiary', [])
    )

def save_players_to_excel(players: List[Player]):
    """Save player list to Excel file"""
    try:
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("csv files", "*.csv")]
        )
        if not filename:
            return


        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx", 
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filename:
            return

        # Convert players to a list of dictionaries for DataFrame
        player_data = []
        for player in players:
            player_dict = {
                'Name': player.name,
                'Rank': player.rank,
                'Server': player.server,
                'Order Capable': player.order_capable,
                'Main Roles': ', '.join(player.position_preference.main_roles),
                'Secondary Roles': ', '.join(player.position_preference.secondary_roles),
                'Tertiary Roles': ', '.join(player.position_preference.tertiary_roles)
            }
            player_data.append(player_dict)

        df = pd.DataFrame(player_data)
        df.to_excel(filename, index=False)
        messagebox.showinfo("Success", f"Players saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save players: {str(e)}")

def load_players_from_excel(add_player_callback):
    """Load players from Excel file"""
    try:
        filename = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not filename:
            return []

        df = pd.read_excel(filename)
        loaded_players = []

        for _, row in df.iterrows():
            # Parse roles
            positions = {
                'main': row['Main Roles'].split(', ') if pd.notna(row['Main Roles']) else [],
                'secondary': row['Secondary Roles'].split(', ') if pd.notna(row['Secondary Roles']) else [],
                'tertiary': row['Tertiary Roles'].split(', ') if pd.notna(row['Tertiary Roles']) else []
            }

            # Create PositionPreference
            position_preference = create_position_preference(positions)

            # Create Player
            player = Player(
                name=row['Name'],
                rank=row['Rank'],
                position_preference=position_preference,
                server=row['Server'],
                order_capable=row['Order Capable']
            )

            # Add player and track
            add_player_callback(player)
            loaded_players.append(player)

        messagebox.showinfo("Success", f"Loaded {len(loaded_players)} players from {filename}")
        return loaded_players
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load players: {str(e)}")
        return []

def generate_valid_position_assignments(team_players: List[Player]) -> List[Dict[str, Player]]:
    """
    Generate all possible valid position assignments for a team of 5 players
    
    :param team_players: List of 5 players to assign positions
    :return: List of dictionaries representing valid position assignments
    """
    valid_assignments = []
    
    # Try all permutations of players
    for perm in permutations(team_players):
        # Check if this permutation can be a valid position assignment
        current_assignment = {}
        is_valid_assignment = True
        
        for position, player in zip(POSITIONS, perm):
            # Check if the player can play this position
            if position in player.position_preference.get_all_positions():
                current_assignment[position] = player
            else:
                is_valid_assignment = False
                break
        
        # If assignment is valid, add it to list
        if is_valid_assignment:
            valid_assignments.append(current_assignment)
    
    # If no valid assignments found, return empty list
    return valid_assignments if valid_assignments else []

#####

class PlayerCreationFrame(ttk.Frame):
    def __init__(self, parent, add_player_callback):
        super().__init__(parent)
        self.add_player_callback = add_player_callback
        self.position_vars = {
            'main': [],
            'secondary': [],
            'tertiary': []
        }
        self.setup_ui()

    def setup_ui(self):
        # Player Name
        ttk.Label(self, text="Player Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Rank Selection
        ttk.Label(self, text="Rank:").grid(row=1, column=0, padx=5, pady=5)
        self.rank_var = tk.StringVar()
        rank_combo = ttk.Combobox(self, textvariable=self.rank_var, values=RANKS)
        rank_combo.grid(row=1, column=1, padx=5, pady=5)
        rank_combo.set(RANKS[0])

        # Server Selection
        ttk.Label(self, text="Server:").grid(row=2, column=0, padx=5, pady=5)
        self.server_var = tk.StringVar()
        server_combo = ttk.Combobox(self, textvariable=self.server_var, values=SERVERS)
        server_combo.grid(row=2, column=1, padx=5, pady=5)
        server_combo.set(SERVERS[0])

        # Order Capability
        ttk.Label(self, text="Order Capable:").grid(row=3, column=0, padx=5, pady=5)
        self.order_var = tk.BooleanVar()
        ttk.Checkbutton(self, variable=self.order_var).grid(row=3, column=1, padx=5, pady=5)

        # Position Preferences
        self.create_position_section("Main Roles", 4, 'main')
        self.create_position_section("Secondary Roles", 5, 'secondary')
        self.create_position_section("Tertiary Roles", 6, 'tertiary')

        # Add Player Button
        ttk.Button(self, text="Add Player", command=self.add_player).grid(row=7, column=0, columnspan=2, pady=20)

    def create_position_section(self, title: str, row: int, role_type: str):
        ttk.Label(self, text=f"{title}:").grid(row=row, column=0, padx=5, pady=5)
        position_frame = ttk.Frame(self)
        position_frame.grid(row=row, column=1, padx=5, pady=5)

        for i, pos in enumerate(POSITIONS):
            var = tk.BooleanVar()
            self.position_vars[role_type].append((pos, var))
            ttk.Checkbutton(position_frame, text=pos, variable=var).grid(row=0, column=i, padx=2)

    def get_selected_positions(self, role_type: str) -> List[str]:
        return [pos for pos, var in self.position_vars[role_type] if var.get()]

    def add_player(self):
        try:
            # Get position preferences
            positions = {
                'main': self.get_selected_positions('main'),
                'secondary': self.get_selected_positions('secondary'),
                'tertiary': self.get_selected_positions('tertiary')
            }

            # Validate that a position is not selected in multiple tiers
            all_positions = positions['main'] + positions['secondary'] + positions['tertiary']
            if len(all_positions) != len(set(all_positions)):
                raise ValueError("A position cannot be selected in multiple tiers")

            # Validate that at least one main role is selected
            if not positions['main']:
                raise ValueError("At least one main role must be selected")

            # Create player
            player = Player(
                name=self.name_entry.get().strip(),
                rank=self.rank_var.get(),
                position_preference=create_position_preference(positions),
                server=self.server_var.get(),
                order_capable=self.order_var.get()
            )

            self.add_player_callback(player)
            self.clear_form()
            messagebox.showinfo("Success", "Player added successfully!")

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.rank_var.set(RANKS[0])
        self.server_var.set(SERVERS[0])
        self.order_var.set(False)
        for role_type in self.position_vars:
            for _, var in self.position_vars[role_type]:
                var.set(False)

class PlayerListFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.players: List[Player] = []
        self.setup_ui()

    def setup_ui(self):
        # Player List with Checkboxes
        self.tree = ttk.Treeview(self, columns=('Select', 'Name', 'Rank', 'Server', 'Positions', 'Order'), show='headings')

        # Rearrange columns to put Select first
        self.tree.heading('Select', text='Select')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Rank', text='Rank')
        self.tree.heading('Server', text='Server')
        self.tree.heading('Positions', text='Positions')
        self.tree.heading('Order', text='Order')

        # Configure column widths (adjusted to be narrower)
        self.tree.column('Select', width=50, anchor='center')
        self.tree.column('Name', width=100)
        self.tree.column('Rank', width=70)
        self.tree.column('Server', width=70)
        self.tree.column('Positions', width=200)
        self.tree.column('Order', width=70)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, columnspan=6, sticky='nsew')
        scrollbar.grid(row=0, column=7, sticky='ns')

        # Restore existing buttons and add Delete Player
        ttk.Button(self, text="Save Players", command=self.save_players).grid(row=1, column=0, pady=10)
        ttk.Button(self, text="Load Players", command=self.load_players).grid(row=1, column=1, pady=10)
        ttk.Button(self, text="Select All", command=self.select_all).grid(row=1, column=2, pady=10)
        ttk.Button(self, text="Deselect All", command=self.deselect_all).grid(row=1, column=3, pady=10)
        ttk.Button(self, text="Delete Player", command=self.delete_players).grid(row=1, column=4, pady=10)
        ttk.Button(self, text="Generate Teams", command=self.generate_teams).grid(row=1, column=5, pady=10)
        ttk.Button(self, text="Generate Teams (Advanced)", command=self.generate_teams_advanced).grid(row=1, column=6, pady=10)

        # Configure grid
        for i in range(6):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Bind double-click to toggle selection
        self.tree.bind('<Double-1>', self.toggle_selection)
        
    def delete_players(self):
        """Delete selected players from the list"""
        # Get selected items
        items_to_delete = []
        players_to_delete = []
        
        for idx, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item, 'values')
            if values[0] == '☑':
                items_to_delete.append(item)
                players_to_delete.append(self.players[idx])
        
        # Confirm deletion
        if not items_to_delete:
            messagebox.showinfo("Delete Players", "No players selected for deletion.")
            return
        
        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Deletion", 
                                      f"Are you sure you want to delete {len(items_to_delete)} player(s)?")
        
        if confirm:
            # Remove from treeview
            for item in items_to_delete:
                self.tree.delete(item)
            
            # Remove from players list
            for player in players_to_delete:
                self.players.remove(player)
            
            messagebox.showinfo("Delete Players", f"Deleted {len(items_to_delete)} player(s).")

    def add_player(self, player: Player):
        # Add the player to the players list
        self.players.append(player)

        # Insert player into the treeview
        positions = str(player.position_preference)
        item = self.tree.insert('', 'end', values=(
            '☐',  # Select column now first
            player.name,
            player.rank,
            player.server,
            positions,
            'Yes' if player.order_capable else 'No'
        ))

        # Bind double-click to toggle selection
        self.tree.bind('<Double-1>', self.toggle_selection)

    def toggle_selection(self, event):
        # Get the item that was clicked
        item = self.tree.identify_row(event.y)
        if item:
            current_value = self.tree.item(item, 'values')

            # Toggle the selection (first column)
            if current_value[0] == '☐':
                new_values = ('☑',) + current_value[1:]
            else:
                new_values = ('☐',) + current_value[1:]

            # Update the treeview item
            self.tree.item(item, values=new_values)

    def select_all(self):
        for item in self.tree.get_children():
            current_values = self.tree.item(item, 'values')
            new_values = ('☑',) + current_values[1:]
            self.tree.item(item, values=new_values)

    def deselect_all(self):
        for item in self.tree.get_children():
            current_values = self.tree.item(item, 'values')
            new_values = ('☐',) + current_values[1:]
            self.tree.item(item, values=new_values)

    def get_selected_players(self) -> List[Player]:
        """Return only the selected players"""
        selected = []
        for item, player in zip(self.tree.get_children(), self.players):
            values = self.tree.item(item, 'values')
            if values[0] == '☑':
                selected.append(player)
        return selected  # Always return a list, even if empty

    def save_players(self):
        """Save players to an Excel file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx", 
                filetypes=[("Excel files", "*.xlsx")]
            )
            if not filename:
                return

            # Convert players to a list of dictionaries for DataFrame
            player_data = []
            for player in self.players:
                player_dict = {
                    'Name': player.name,
                    'Rank': player.rank,
                    'Server': player.server,
                    'Order Capable': player.order_capable,
                    'Main Roles': ', '.join(player.position_preference.main_roles),
                    'Secondary Roles': ', '.join(player.position_preference.secondary_roles),
                    'Tertiary Roles': ', '.join(player.position_preference.tertiary_roles)
                }
                player_data.append(player_dict)

            df = pd.DataFrame(player_data)
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Players saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save players: {str(e)}")

    def load_players(self):
        """Load players from an Excel file"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx")]
            )
            if not filename:
                return

            df = pd.read_excel(filename)
            
            # Clear existing players
            self.players.clear()
            for i in self.tree.get_children():
                self.tree.delete(i)

            for _, row in df.iterrows():
                # Parse roles
                positions = {
                    'main': row['Main Roles'].split(', ') if pd.notna(row['Main Roles']) else [],
                    'secondary': row['Secondary Roles'].split(', ') if pd.notna(row['Secondary Roles']) else [],
                    'tertiary': row['Tertiary Roles'].split(', ') if pd.notna(row['Tertiary Roles']) else []
                }

                # Create PositionPreference
                position_preference = create_position_preference(positions)

                # Create Player
                player = Player(
                    name=row['Name'],
                    rank=row['Rank'],
                    position_preference=position_preference,
                    server=row['Server'],
                    order_capable=row['Order Capable']
                )

                # Add player
                self.add_player(player)

            messagebox.showinfo("Success", f"Loaded {len(self.players)} players from {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load players: {str(e)}")

    def generate_teams(self):
        selected_players = self.get_selected_players()
        
        if len(selected_players) < 10:
            messagebox.showwarning("Warning", f"Not enough players! Selected {len(selected_players)}/10 players.")
            return

        # Create results window similar to before, but with pagination
        results_window = tk.Toplevel()
        results_window.title("Team Compositions")
        results_window.geometry("1000x800")

        # Pagination frame
        pagination_frame = ttk.Frame(results_window)
        pagination_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Text widget for results
        text_widget = tk.Text(results_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(results_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Generate all possible team compositions
        all_compositions = generate_team_combinations(selected_players, num_combinations=100)

        # Pagination variables
        current_page = [0]  # Mutable to allow modification in nested functions
        compositions_per_page = 5

        def display_page(page_num):
            # Clear previous content
            text_widget.delete('1.0', tk.END)
            
            # Calculate start and end indices for current page
            start_idx = page_num * compositions_per_page
            end_idx = min(start_idx + compositions_per_page, len(all_compositions))

            # Display compositions for current page
            for i, comp in enumerate(all_compositions[start_idx:end_idx], 1):
                text_widget.insert(tk.END, f"\nTeam Composition #{start_idx + i}\n")
                text_widget.insert(tk.END, "=" * 80 + "\n")
                text_widget.insert(tk.END, str(comp) + "\n")
                text_widget.insert(tk.END, "=" * 80 + "\n\n")

            # Update page label
            page_label.config(text=f"Page {page_num + 1} of {math.ceil(len(all_compositions) / compositions_per_page)}")

        def prev_page():
            if current_page[0] > 0:
                current_page[0] -= 1
                display_page(current_page[0])

        def next_page():
            if current_page[0] < math.ceil(len(all_compositions) / compositions_per_page) - 1:
                current_page[0] += 1
                display_page(current_page[0])

        # Previous and Next buttons
        prev_button = ttk.Button(pagination_frame, text="Previous", command=prev_page)
        prev_button.pack(side=tk.LEFT, padx=10)

        page_label = ttk.Label(pagination_frame, text="")
        page_label.pack(side=tk.LEFT, padx=10)

        next_button = ttk.Button(pagination_frame, text="Next", command=next_page)
        next_button.pack(side=tk.LEFT, padx=10)

        # Initial display
        display_page(0)

     
    def generate_teams_advanced(self):
        selected_players = self.get_selected_players()
        
        if len(selected_players) < 10:
            messagebox.showwarning("Warning", f"Not enough players! Selected {len(selected_players)}/10 players.")
            return

        # Create results window similar to before, but with pagination
        results_window = tk.Toplevel()
        results_window.title("Team Compositions")
        results_window.geometry("1000x800")

        # Pagination frame
        pagination_frame = ttk.Frame(results_window)
        pagination_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Text widget for results
        text_widget = tk.Text(results_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(results_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Generate all possible team compositions
        all_compositions = generate_team_combinations_advanced(selected_players, num_combinations=100)

        # Pagination variables
        current_page = [0]  # Mutable to allow modification in nested functions
        compositions_per_page = 5

        def display_page(page_num):
            # Clear previous content
            text_widget.delete('1.0', tk.END)
            
            # Calculate start and end indices for current page
            start_idx = page_num * compositions_per_page
            end_idx = min(start_idx + compositions_per_page, len(all_compositions))

            # Display compositions for current page
            for i, comp in enumerate(all_compositions[start_idx:end_idx], 1):
                text_widget.insert(tk.END, f"\nTeam Composition #{start_idx + i}\n")
                text_widget.insert(tk.END, "=" * 80 + "\n")
                text_widget.insert(tk.END, str(comp) + "\n")
                text_widget.insert(tk.END, "=" * 80 + "\n\n")

            # Update page label
            page_label.config(text=f"Page {page_num + 1} of {math.ceil(len(all_compositions) / compositions_per_page)}")

        def prev_page():
            if current_page[0] > 0:
                current_page[0] -= 1
                display_page(current_page[0])

        def next_page():
            if current_page[0] < math.ceil(len(all_compositions) / compositions_per_page) - 1:
                current_page[0] += 1
                display_page(current_page[0])

        # Previous and Next buttons
        prev_button = ttk.Button(pagination_frame, text="Previous", command=prev_page)
        prev_button.pack(side=tk.LEFT, padx=10)

        page_label = ttk.Label(pagination_frame, text="")
        page_label.pack(side=tk.LEFT, padx=10)

        next_button = ttk.Button(pagination_frame, text="Next", command=next_page)
        next_button.pack(side=tk.LEFT, padx=10)

        # Initial display
        display_page(0)
                           
#####

@dataclass
class TeamComposition:
    red_team: Dict[str, Player]
    blue_team: Dict[str, Player]
    red_score: float
    blue_score: float
    t_value: float  # Total score difference
    l_value: float  # Lane difference RMS

    def __str__(self):
        result = []
        # Red Team
        result.append("RED TEAM")
        result.append(f"Team Score: {self.red_score:.2f}")
        result.append("-" * 50)
        for position in POSITIONS:
            player = self.red_team[position]
            result.append(f"{position.upper()}: {player.name} ({player.rank}, {player.server})")
            result.append(f"  Position Preference: {player.position_preference}")
            result.append(f"  Order Capable: {player.order_capable}")
        
        # Blue Team
        result.append("\nBLUE TEAM")
        result.append(f"Team Score: {self.blue_score:.2f}")
        result.append("-" * 50)
        for position in POSITIONS:
            player = self.blue_team[position]
            result.append(f"{position.upper()}: {player.name} ({player.rank}, {player.server})")
            result.append(f"  Position Preference: {player.position_preference}")
            result.append(f"  Order Capable: {player.order_capable}")
        
        # Metrics
        result.append("\nMETRICS")
        result.append(f"T-Value (Team Score Difference): {self.t_value:.2f}")
        result.append(f"L-Value (Lane Difference RMS): {self.l_value:.2f}")
        
        return "\n".join(result)

def calculate_t_value(red_score: float, blue_score: float) -> float:
    """Calculate the absolute difference between team scores"""
    return abs(red_score - blue_score)

def calculate_l_value(red_team: Dict[str, Player], blue_team: Dict[str, Player]) -> float:
    """Calculate the root mean square of lane differences without order capable bonus"""
    squared_diffs = []
    
    for position in POSITIONS:
        red_player = red_team[position]
        blue_player = blue_team[position]
        
        # Calculate individual position score difference without order points
        red_pos_score = (red_player.rank_points() + 
                        red_player.position_penalty(position))
        blue_pos_score = (blue_player.rank_points() + 
                         blue_player.position_penalty(position))
        
        diff = red_pos_score - blue_pos_score
        squared_diffs.append(diff ** 2)
    
    # Calculate RMS
    mean_squared_diff = sum(squared_diffs) / len(POSITIONS)
    return math.sqrt(mean_squared_diff)


def calculate_l_value_advanced(red_team: Dict[str, Player], blue_team: Dict[str, Player]) -> float:
    """Calculate the root mean square of lane differences without order capable bonus"""
    squared_diffs = []
    
    for position in POSITIONS:
        red_player = red_team[position]
        blue_player = blue_team[position]
        
        # Calculate individual position score difference without order points
        red_pos_score = (red_player.rank_points(position) + 
                        red_player.position_penalty_advanced(position))
        blue_pos_score = (blue_player.rank_points(position) + 
                         blue_player.position_penalty_advanced(position))
        
        diff = red_pos_score - blue_pos_score
        squared_diffs.append(diff ** 2)
    
    # Calculate RMS
    mean_squared_diff = sum(squared_diffs) / len(POSITIONS)
    return math.sqrt(mean_squared_diff)

def evaluate_team_composition(players: List[Player], position_assignments: Dict[str, Player]) -> float:
    """Evaluate a team composition based on various metrics"""
    total_score = 0
    
    for position, player in position_assignments.items():
        # Add rank points
        total_score += player.rank_points()
        
        # Add/subtract points based on position preference
        total_score += player.position_penalty(position)
        
        # Add points for order capability
        total_score += player.order_points
    
    # Add team synergy bonus based on average rank
    synergy_exponent = 0.5  # Choose your exponent for diminishing returns
    synergy_weight = 1  # Choose your synergy weight
    avg_rank = sum(p.rank_points() for p in players) / len(players)
    total_score += avg_rank ** synergy_exponent * synergy_weight
    
    return total_score

def evaluate_team_composition_advanced(players: List[Player], position_assignments: Dict[str, Player]) -> float:
    """Evaluate a team composition based on various metrics"""
    total_score = 0
    
    for position, player in position_assignments.items():
        # Add rank points
        total_score += player.rank_points(position)
        
        # Add/subtract points based on position preference
        total_score += player.position_penalty_advanced(position)
        
        # Add points for order capability
        total_score += player.order_points
    
    # Add team synergy bonus based on average rank
    synergy_exponent = 0.5  # Choose your exponent for diminishing returns
    synergy_weight = 1  # Choose your synergy weight
    avg_rank = sum(p.rank_points(position) for p in players) / len(players)
    total_score += avg_rank ** synergy_exponent * synergy_weight
    
    return total_score


def generate_team_combinations(players: List[Player], num_combinations: int = 5) -> List[TeamComposition]:
    """Generate and evaluate possible team compositions, returning the top combinations"""
    valid_combinations = []
    
    ## 
    ## Code here if red vs blue preset
    ##

    # Generate all possible 10-player combinations divided into two teams
    for team_players in combinations(players, 10):
        # Try different ways to split players into two teams
        for red_team_players in combinations(team_players, 5):
            blue_team_players = tuple(p for p in team_players if p not in red_team_players)
            
            # Generate valid position assignments for both teams
            red_assignments = generate_valid_position_assignments(list(red_team_players))
            blue_assignments = generate_valid_position_assignments(list(blue_team_players))
            
            # Try all valid position combinations
            for red_pos in red_assignments:
                for blue_pos in blue_assignments:
                    # Evaluate both teams
                    red_score = evaluate_team_composition(list(red_team_players), red_pos)
                    blue_score = evaluate_team_composition(list(blue_team_players), blue_pos)
                    
                    # Calculate metrics
                    t_value = calculate_t_value(red_score, blue_score)
                    l_value = calculate_l_value(red_pos, blue_pos)
                    
                    comp = TeamComposition(
                        red_team=red_pos,
                        blue_team=blue_pos,
                        red_score=red_score,
                        blue_score=blue_score,
                        t_value=t_value,
                        l_value=l_value
                    )
                    valid_combinations.append(comp)
    
    # Sort by balance (lower T and L values are better)
    return sorted(valid_combinations, 
                 key=lambda x: (x.t_value + x.l_value))[:num_combinations]


def generate_team_combinations_advanced(players: List[Player], num_combinations: int = 5) -> List[TeamComposition]:
    """Generate and evaluate possible team compositions, returning the top combinations"""
    valid_combinations = []
    
    ## 
    ## Code here if red vs blue preset
    ##

    # Generate all possible 10-player combinations divided into two teams
    for team_players in combinations(players, 10):
        # Try different ways to split players into two teams
        for red_team_players in combinations(team_players, 5):
            blue_team_players = tuple(p for p in team_players if p not in red_team_players)
            
            # Generate valid position assignments for both teams
            red_assignments = generate_valid_position_assignments(list(red_team_players))
            blue_assignments = generate_valid_position_assignments(list(blue_team_players))
            
            # Try all valid position combinations
            for red_pos in red_assignments:
                for blue_pos in blue_assignments:
                    # Evaluate both teams
                    red_score = evaluate_team_composition_advanced(list(red_team_players), red_pos)
                    blue_score = evaluate_team_composition_advanced(list(blue_team_players), blue_pos)
                    
                    # Calculate metrics
                    t_value = calculate_t_value(red_score, blue_score)
                    l_value = calculate_l_value_advanced(red_pos, blue_pos)
                    
                    comp = TeamComposition(
                        red_team=red_pos,
                        blue_team=blue_pos,
                        red_score=red_score,
                        blue_score=blue_score,
                        t_value=t_value,
                        l_value=l_value
                    )
                    valid_combinations.append(comp)
    
    # Sort by balance (lower T and L values are better)
    return sorted(valid_combinations, 
                 key=lambda x: (x.t_value + x.l_value))[:num_combinations]

#####

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Team Composition Generator")
        self.geometry("1200x800")

        # Create main container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create and arrange the two main frames
        self.player_list = PlayerListFrame(container)
        self.player_creation = PlayerCreationFrame(container, self.player_list.add_player)

        self.player_creation.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.player_list.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        # Configure grid weights
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

def run_gui():
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
