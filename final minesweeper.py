import random
import time
import datetime
from prettytable import PrettyTable

class Minesweeper:
    def __init__(self, rows, cols, num_mines):
        if num_mines > rows * cols:
            raise ValueError("Number of mines cannot be greater than the total number of cells.")
        
        self.rows, self.cols, self.num_mines = rows, cols, num_mines
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.mine_locations = []
        self.revealed_cells = [[False] * cols for _ in range(rows)]
        self.place_mines()
        self.calculate_adjacent_mines()
        self.start_time = None

    def place_mines(self):
        self.mine_locations = random.sample(range(self.rows * self.cols), self.num_mines)
        for loc in self.mine_locations:
            row, col = divmod(loc, self.cols)
            self.board[row][col] = 'M'


    def calculate_adjacent_mines(self):
        directions = [(i, j) for i in range(4) for j in range(4) if i != 0 or j != 0]

        for loc in self.mine_locations:
            row, col = divmod(loc, self.cols)
            for i, j in directions:
                new_row, new_col = row + i, col + j
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols and self.board[new_row][new_col] != 'M':
                    if self.board[new_row][new_col] == ' ':
                        self.board[new_row][new_col] = '1'
                    else:
                        self.board[new_row][new_col] = str(int(self.board[new_row][new_col]) + 1)

    def reveal_cell(self, row, col):
        if not self.revealed_cells[row][col]:
            self.revealed_cells[row][col] = True
            if self.start_time is None:
                self.start_time = time.time()

            if (row * self.cols + col) in self.mine_locations:
                return False
            elif self.board[row][col] == ' ':
                self.board[row][col] = '0'
                self.reveal_empty_cells(row, col)
            return True
        else:
            print("Cell already revealed. Choose another cell.")
            return None

    def reveal_empty_cells(self, row, col):
        directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2) if i != 0 or j != 0]
        for i, j in directions:
            new_row, new_col = row + i, col + j
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols and not self.revealed_cells[new_row][new_col]:
                self.revealed_cells[new_row][new_col] = True
                if (new_row * self.cols + new_col) not in self.mine_locations and self.board[new_row][new_col] == ' ':
                    self.board[new_row][new_col] = '0'
                    self.reveal_empty_cells(new_row, new_col)

    def mark_mine_location(self, row, col):
        if not self.revealed_cells[row][col]:
            self.board[row][col] = 'F'
            self.print_board()
        else:
            print("Cannot mark a revealed cell. Choose another cell.")
            


    def print_board(self):
        table = PrettyTable()
        table.field_names = [''] + [str(i) for i in range(self.cols)]
        for i in range(self.rows):
            row = [str(i)] + [self.get_display_value(i, j) for j in range(self.cols)]
            table.add_row(row)
    
        print(table)

    def get_display_value(self, row, col):
        if self.revealed_cells[row][col]:
            return self.board[row][col]
        elif self.board[row][col] == 'F':
            return 'F'
        else:
            return '-'

    def get_elapsed_time(self):
        if self.start_time is not None:
            return time.time() - self.start_time
        else:
            return 0

    def update_leaderboard(self, player_name, elapsed_time,game_won):
        if game_won:
            leaderboard_filename = "leaderboard.txt"
            try:
                current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
                with open(leaderboard_filename, "a") as file:
                    file.write(f"{player_name}: {elapsed_time:.2f} seconds ({current_date})\n")
            except Exception as e:
                print(f"Error updating leaderboard: {e}")

    def display_leaderboard(self):
        leaderboard_filename = "leaderboard.txt"
        try:
            with open(leaderboard_filename, "r") as file:
                leaderboard = file.read()
                print("Leaderboard:")
                print(leaderboard)
        except Exception as e:
            print(f"Error displaying leaderboard: {e}")
            
    def reveal_all_mines(self):
        for loc in self.mine_locations:
            row, col = divmod(loc, self.cols)
            self.revealed_cells[row][col] = True
        game.print_board()

        
game = Minesweeper(10, 10, 7)
player_name=input('Enter your name: ')
while True:
    game.print_board()
    print("Options:")
    print("1. Reveal a cell")
    print("2. Mark a potential mine location")
    print("3. Display leaderboard")
    choice = input("Enter your choice : ")

    if choice == '1':
        row = int(input("Enter the row to reveal: "))
        col = int(input("Enter the column to reveal: "))
        result = game.reveal_cell(row, col)
        if result is not None:
            if result:
                print("The cell is not a mine.")
            else:
                game_won = False
                print("Game over! The cell is a mine.")
                game.reveal_all_mines() 
                elapsed_time = game.get_elapsed_time()
                print(f"Time taken: {elapsed_time:.2f} seconds")
                game.update_leaderboard(player_name, elapsed_time,game_won)
                break
            if all(cell or (i * game.cols + j) in game.mine_locations for i, cells in enumerate(game.revealed_cells) for j, cell in enumerate(cells)):
                game_won = True
                print("All cells revealed. You win!")
                elapsed_time = game.get_elapsed_time()
                print(f"Time taken: {elapsed_time:.2f} seconds")
                game.update_leaderboard(player_name, elapsed_time,game_won)
                game.reveal_all_mines() 
                break
    elif choice == '2':
        row = int(input("Enter the row to mark: "))
        col = int(input("Enter the column to mark: "))
        game.mark_mine_location(row, col)
        game.print_board()
    elif choice == '3':
        game.display_leaderboard()
    else:
        print("Invalid choice. Please enter 1 or 2.")

