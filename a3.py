import tkinter as tk
from tkinter import filedialog # For masters task
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *

class FarmGame:
    """
    Class for the controller class of the game

    """
    def __init__ (self, master: tk.Tk, map_file: str) -> None:
        """
        Instantiates an instace of the FarmGame class

        Args:
            master: root window of the game
            map_file: Location of the map file (path)
        """
        self._master = master
        self._master.title('Farm Game')
        self._model = FarmModel(map_file)

        self._player = self._model.get_player()
        self._inventory = self._player.get_inventory()

        self._banner_frame = tk.Frame(master, height='130')
        self._banner_frame.pack(side=tk.TOP)
        self._banner = get_image('images/header.png', (700, 130))
        self._banner_label = tk.Label(self._banner_frame, image=self._banner)
        self._banner_label.pack()

        self._farm_frame = tk.Frame(self._master)
        self._farm_frame.pack(side=tk.TOP)
        self._farm = FarmView(self._farm_frame, self._model.get_dimensions()
                               ,(FARM_WIDTH, FARM_WIDTH))
        self._farm.pack(side=tk.LEFT)

        self._item_view_frame = tk.Frame(self._farm_frame,relief=tk.RAISED,
                                    width=INVENTORY_WIDTH, height=FARM_WIDTH)
        self._item_view_frame.pack(side=tk.RIGHT)
        self._item_view_frame.pack_propagate(False)

        self._labels = []
        for item in ITEMS: 
            # Determines if the item is a seed to include a buy button
            if item in SEEDS:
                if item in self._inventory:
                    self._item_label = ItemView(self._item_view_frame, 
item, self._inventory[item], self.select_item,self.sell_item, self.buy_item)
                    self._labels.append(self._item_label)
                else:
                    self._item_label = ItemView(self._item_view_frame, 
                item, 0, self.select_item, self.sell_item, self.buy_item)
                    self._labels.append(self._item_label)

            else:
                self._item_label = ItemView(self._item_view_frame, item, 
                            0, self.select_item, self.sell_item,None )
                self._labels.append(self._item_label)

        # Packs all created labels so they are visible 
        for labels in self._labels:
            labels.pack(side=tk.TOP, fill=tk.BOTH)

        self._infobar = InfoBar(self._master)
        self._infobar.pack(side=tk.TOP)

        self._next_day_button = tk.Button(self._master, text='Next day', 
                                          command=self._next_day)
        self._next_day_button.pack(side=tk.BOTTOM )

        master.bind("<KeyPress>", self.handle_keypress)
        
        self.redraw()

    def _next_day(self):
        """
        Method for going into a new day

        """
        self._model.new_day()
        self.redraw()
    
    def handle_keypress(self, event: tk.Event) -> None:
        """
        Method for handling all keypresses made 

        Args:
            event: A key press made by the user
        """
        if event.char == DOWN:
            self._model.move_player(DOWN)
        elif event.char == UP:
            self._model.move_player(UP)
        elif event.char == LEFT:
            self._model.move_player(LEFT)
        elif event.char == RIGHT:
            self._model.move_player(RIGHT)
        elif event.char == 't':
            self._model.till_soil(self._model.get_player_position())
        elif event.char == 'u':
            self._model.untill_soil(self._model.get_player_position())
        elif event.char == 'p':
            selected = self._model.get_player().get_selected_item()
            # Determines if the user is planting a selected item 
            if selected in self._model.get_player().get_inventory():
                # Determines if the user is on tilled soil
                if self.check_ground(self._model.get_player_position()):
                    if selected == 'Potato Seed':
                        new_plant = PotatoPlant()

                    elif selected == 'Kale Seed':
                        new_plant = KalePlant()

                    elif selected == 'Berry Seed':
                        new_plant = BerryPlant()

                    self._model.add_plant(\
                        self._model.get_player_position(), new_plant)
                    self._model.get_player().remove_item((selected, 1))

                    target_label = self.find_label(self._labels, selected)
                    # Updates the selected label's item appropriately 
                    if selected in self._model.get_player().get_inventory():
                        target_label.update(self._inventory[selected], True)
                    else:
                        target_label.update(0, False)

        elif event.char == 'r':
            self._model.remove_plant(self._model.get_player_position())
             
        elif event.char == 'h':
            result = self._model.harvest_plant(self._model.\
                                               get_player_position())
            if result == None: # Determines if there is a plant present 
                pass
            else:
                self._model.get_player().add_item(result) 
                for labels in self._labels: # Updates corresponding label
                    if labels.get_name() in \
                        self._model.get_player().get_inventory():
                        if labels.get_name().split(' ')[0] == result[0]:
                            labels.update(\
        self._model.get_player().get_inventory()[labels.get_name()], False)
                            pass
                    else:
                        pass
        self.redraw()
    
    def check_ground(self, position: tuple[int, int]) -> bool:
        """
        Method for determining if the user's current position contains soil

        Args:
            position: The player's coordinates (x, y)

        Returns:
            bool: Whether the ground is soil or not 
        """
        row, col = position
        return self._model.get_map()[row][col] == SOIL 
    
    def find_label(self, labels: list['ItemView'], name: str):
        """
        Retrieves the specified label

        Args:
            labels: A list of the existing labels
            name: Name of the item 

        Returns:
            selected_label (ItemView): the label being retrieved 
        """
        for label in labels:
            # Loops through the existing labels to find a requested label
            if label.get_name() == name:
                selected_label = label
                return selected_label

    def select_item(self, item_name: str) -> None: 
        """
        Binding command for when the user selects an item. This method 
        determines of the item is eligible for selection

        Args:
            item_name: name of the item being selected

        """
        inventory = self._model.get_player().get_inventory()
        self._previous_selection = self.find_label(self._labels, 
                                self._model.get_player().get_selected_item())
        if self._previous_selection != None:
            # Deselects the previous selection made by the player 
            if self._previous_selection.get_name() not in self._inventory:
                pass
            else:
                self._previous_selection.update(\
            inventory[self._model.get_player().get_selected_item()], False)
        self._model.get_player().select_item(item_name)
        self._new_selection = self._model.get_player().get_selected_item()
        # Selects the new item if it is in the inventory 
        if item_name in inventory:
            self._model.get_player().select_item(item_name)
            self._new_selection = self._model.get_player().get_selected_item()
            # Updates the selected label if the selection was valid 
            if self._model.get_player().get_selected_item() != None:
                selected_label = self.find_label(self._labels, item_name)
                selected_label.update(inventory[item_name], True)
        else:
            return None

    def buy_item(self, item_name: str) -> None:
        """
        Binding command for when the user buys an item. Determines if the 
        user is eligible for purchasing that specific item

        Args:
            item_name: name of the item being bought
        """
        self._model.get_player().buy(item_name, BUY_PRICES[item_name])

        for labels in self._labels:
            if labels.get_name() == item_name:
                labels.update(self._inventory[labels.get_name()], False)
        self.redraw()
    
    def sell_item(self, item_name: str) -> None:
        """
        Binding command for selling an item. Determines if the user is
        eligible for selling the item

        Args:
            item_name: Name of the item being sold
        """
        self._model.get_player().sell(item_name, SELL_PRICES[item_name])
        for labels in self._labels:
            if labels.get_name() == item_name:
                # Updates label after item has been sold
                if labels.get_name() not in self._inventory: 
                    labels.update(0, False)
                else:
                    labels.update(self._inventory[labels.get_name()], False)
        self.redraw()    

    def redraw(self) -> None:
        """
        Method for redrawing the FarmGame view
        """
        self._farm.redraw(self._model.get_map(), self._model.get_plants(), 
    self._model.get_player_position(), self._model.get_player_direction())
        self._infobar.redraw(self._model.get_days_elapsed(), 
    self._model.get_player().get_money(), self._model._player.get_energy())

class FarmView(AbstractGrid):
    """
    Class for the farm view which inherits from abstract grid 

    Args:
        AbstractGrid: a class which inherits from tk.Canvas 
    """
    def __init__ (self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int], 
    size: tuple[int, int], **kwargs) -> None:
        """
        Instantiates an instance of the FarmView class 

        Args:
            master: The master frame for this Canvas.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)

        """
        super(FarmView, self).__init__(master, dimensions, size)
        self._image_cache = {}
    
    def redraw(self, ground: list[str], plants: dict[tuple[int, int],'Plant'],
    player_position: tuple[int, int], player_direction: str) -> None:
        """
        Redraws the farm view

        Args:
            ground: List of the strings detailing the 
            ground of the farm
            plants: Dictionary containing the coordinates (x, y) and plant
            objects existing 
            player_position: Coordinates of the player (x, y)
            player_direction: String detailing direction player is going
        """
        self.clear()
        # Loops through the list of corresponding squares on the map
        for rows, tiles in enumerate(ground):
            # Loops through each square at each index of the map
            for column, tile in enumerate(tiles):
                # Sets the coordinates and size of the image to be displayed
                coordinates = self.get_midpoint((rows, column))
                img = get_image(f'images/{IMAGES.get(tile)}', 
                            self.get_cell_size(), self._image_cache)
                self.create_image(coordinates[0], coordinates[1], image=img)
        
        #  Determines if any plants are present on the farm and displays them
        # according to their coordinates
        for plant in plants:
            self._img_path = get_plant_image_name(plants[plant])
            self._img_of_plant = get_image(f'images/{self._img_path}', 
                                    self.get_cell_size(), self._image_cache)
            self._plant_position = self.get_midpoint((plant[0], plant[1]))
            self.create_image(self._plant_position[0], self._plant_position[1], 
                        image=self._img_of_plant)

        img_of_player = get_image(f'images/player_{player_direction}.png', 
                                self.get_cell_size(), self._image_cache)
        self._new_position = self.pixel_to_cell(player_position[0], 
                                            player_position[1])
        self._position = self.get_midpoint((player_position[0], 
                                        player_position[1]))
        self.create_image(self._position[0], self._position[1],
                          image=img_of_player)

class ItemView(tk.Frame):
    """
    Class for the ItemView object. It inherits from tk.Frame

    """
    def __init__(self, master: tk.Frame, item_name: str, amount: int, 
    select_command:Optional[Callable[[str], None]] = None, 
    sell_command: Optional[Callable[[str],None]] = None,
      buy_command: Optional[Callable[[str], None]] = None) -> None:
        """
        Initialises an instance of the class

        Args:
            master: frame for which the object will be packed to 
            item_name: string of the item's name
            amount: Integer of the amount of a specific item
            select_command: Defaults to None. The binding command for selection
            sell_command: Defaults to None. The binding command for selling
            buy_command: Defaults to None. The binding command for buying

        """
        super().__init__(master)
        self._item_name = item_name
        self._amount = amount
        self['borderwidth'] = 2
        self['relief'] = tk.RAISED
        self['height'] = FARM_WIDTH/6
        self.pack_propagate(0)
        self._buttons_available = []

        # Determines if the user has the item 
        if amount == 0: 
            colour = INVENTORY_EMPTY_COLOUR
            self._label_detail = 'Buy price: $N/A'
        else:
            colour = INVENTORY_COLOUR
        
        # Determines if the item is buyable
        if buy_command != None:
            self._buy_button = tk.Button(self, text='Buy', 
                                         command=lambda:buy_command(item_name))
            self._buttons_available.append(self._buy_button)
        
        if item_name in SEEDS:
            self._label_detail = f'Buy price: ${BUY_PRICES[item_name]}'
        else:
            self._label_detail = 'Buy price: $N/A'

        self._sell_button = tk.Button(self, text='Sell', 
                                      command=lambda:sell_command(item_name))
        self._buttons_available.append(self._sell_button)
           
        self['bg'] = colour
        self._information = tk.Label(self, bg=colour, text=f'{item_name}:\
         {amount}\nSell price: ${SELL_PRICES[item_name]}\n{self._label_detail}')
        self._information.pack(side=tk.LEFT)
        for buttons in self._buttons_available:
            buttons.pack(side=tk.LEFT)
        
        self.update(amount, False)
            
        self.bind("<Button-1>", lambda _: select_command(item_name))
        self._information.bind("<Button-1>",lambda _: select_command(item_name))
    
    def get_name(self) -> str:
        """
        Method for getting the name of the item

        Returns:
            self._item_name: string for the name of the item 
        """
        return self._item_name

    def get_amount(self) -> int:
        """
        Method for getting the amount of the item

        Returns:
            self._amount: string for the name of the item 
        """
        return self._amount

    def update(self, amount: int, selected: bool = False) -> None:
        """
        Method for updating the ItemView

        Args:
            amount: Integer value of new amount of an item
            selected: Defaults to False. If the item is selected 
        """
        if amount == 0:
            new_colour = INVENTORY_EMPTY_COLOUR
        elif selected == True:
            new_colour = INVENTORY_SELECTED_COLOUR
        elif selected == False:
            new_colour = INVENTORY_COLOUR

        text = f'{self.get_name()}: {amount}\nSell price: $'
        self._information.configure(bg=new_colour, 
        text=f'{text}{SELL_PRICES[self.get_name()]}\n{self._label_detail}')
        # Applies the new colour to all buttons
        for button in self._buttons_available:
            button.configure(highlightbackground=new_colour)
        self['bg'] = new_colour
        
class InfoBar(AbstractGrid):
    """
    Class for the InfoBar object to be displayed. This class inherits 
    from the AbstractGrid class which inherits from the tk.Canvas object

    """
    def __init__ (self, master: tk.Tk | tk.Frame) -> None:
        """
        Initialises an instance of the of the InfoBar class

        Args:
            master: Either a window or frame for it to be displayed 
        """
        super(InfoBar, self).__init__(master, (2,3), (700, INFO_BAR_HEIGHT))
        self._master = master
    
    def redraw(self, day: int, money: int, energy: int) -> None:
        """
        Redraws the InfoBar object to update its values

        Args:
            day: Integer of the current day
            money: Integer of the player's current money
            energy: Integer of the player's current energy 
        """
        self.clear()
        self.annotate_position((0,0), 'Day:', font=HEADING_FONT)
        self.annotate_position((0,1), 'Money:', font=HEADING_FONT)
        self.annotate_position((0,2), 'Energy:', font=HEADING_FONT)
        self.annotate_position((1, 0), day)
        self.annotate_position((1,1), f'${money}')
        self.annotate_position((1,2), energy)

def play_game(root: tk.Tk, map_file: str) -> None:
    """
    Function for playing the game. It creates an instance of the FarmGame
    class and then runs the tkinter event loop

    Args:
        root: The window for the game 
        map_file: The path to the map file
    """
    controller = FarmGame(root, map_file)
    root.mainloop()

def main() -> None:
    """
    Main function for playing the game. Assigns a root window and
    calls the play_game function
    """
    ROOT = tk.Tk()
    play_game(ROOT, 'maps/map2.txt')

if __name__ == '__main__':
    main()