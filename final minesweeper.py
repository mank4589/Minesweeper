import random
import time
import datetime
import mysql.connector
from prettytable import PrettyTable

class Minesweeper:
    def __init__(self, rows, cols, num_mines):
        self.rows, self.cols, self.num_mines = rows, cols, num_mines
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.mine_locations = []
        self.revealed_cells = [[False] * cols for _ in range(rows)]
        self.place_mines()
        self.calculate_adjacent_mines()
        self.start_time = None
        
    def create_leaderboard_table(self): 
            cursor = self.conn.cursor()
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    player_name TEXT,
                    elapsed_time REAL,
                    game_won INTEGER,
                    difficulty_mode TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            self.conn.commit()
            
    def place_mines(self):
        self.mine_locations = random.sample(range(self.rows * self.cols), self.num_mines)
        for loc in self.mine_locations:
            row, col = divmod(loc, self.cols)
            self.board[row][col] = 'M'


    def calculate_adjacent_mines(self):
        directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2) if i != 0 or j != 0]

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

    def update_leaderboard(self, player_name, elapsed_time, game_won, difficulty_mode, play_date):
        if game_won:
            try:
                query = '''
                    INSERT INTO leaderboard (player_name, elapsed_time, game_won, difficulty_mode, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                '''
                values = (player_name, round(elapsed_time,2), 1, difficulty_mode, play_date)

                cursor = self.conn.cursor()
                cursor.execute(query, values)
                self.conn.commit()
                cursor.close()
                print("Data successfully inserted into the leaderboard table.")
            except Exception as e:
                print(f"Error updating leaderboard: {e}")
            finally:
                if self.conn.is_connected():
                    self.conn.close()
                    print("Database connection closed.")
          
    def reveal_all_mines(self):
        for loc in self.mine_locations:
            row, col = divmod(loc, self.cols)
            self.revealed_cells[row][col] = True
        self.print_board()

    def __del__(self):
        pass
            
def display_leaderboard():
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='4589',
                database='minesweeper_leaderboard'
            )
            cursor = conn.cursor()
            cursor.execute('''
                SELECT player_name, elapsed_time, difficulty_mode, timestamp FROM leaderboard ORDER BY elapsed_time
            ''')
            rows = cursor.fetchall()

            table = PrettyTable()
            table.field_names = ['PLAYER', 'ELAPSED_TIME', 'DIFFICULTY_MODE', 'TIMESTAMP']
            for row in rows:
                table.add_row(row)

            print(table)

        except Exception as e:
            print(f"Error displaying leaderboard: {e}")

        finally:
            if cursor:
                cursor.close()
            if conn.is_connected():
                conn.close()
def main_menu():
    print("Welcome to Minesweeper!")
    
    while True:
        print("\nMain Menu:")
        print("1. Start Game")
        print("2. Display Leaderboard")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            start_game()
        elif choice == '2':
            display_leaderboard()
        elif choice == '3':
            print("Exiting Minesweeper. Goodbye!")
            
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def start_game():
    player_name = input('Enter your name: ')
    play_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    while True:
        print("\nChoose Difficulty:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Back to Main Menu")
        difficulty_choice = input("Enter your choice: ")

        if difficulty_choice=='1':
            num_mines = 5
            difficulty_mode = 'Easy'

        elif difficulty_choice == '2':
            num_mines = 8
            difficulty_mode = 'Medium'
            
        elif difficulty_choice == '3':
            num_mines = 12
            difficulty_mode = 'Hard'

        elif difficulty_choice == '4':
            break    

        elif difficulty_choice not in ['1', '2', '3']:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
            continue
        game = Minesweeper(10, 10, num_mines)

        while True:
            game.print_board()
            print("Options:")
            print("1. Reveal a cell")
            print("2. Mark a potential mine location")
            print("3. Back to Difficulty Selection")
            choice = input("Enter your choice: ")

            if choice == '3':
                break
            elif choice == '1':
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
                        game.update_leaderboard(player_name, elapsed_time, game_won, difficulty_mode, play_date)
                        break
                    if all(cell or (i * game.cols + j) in game.mine_locations for i, cells in enumerate(game.revealed_cells) for
                           j, cell in enumerate(cells)):
                        game_won = True
                        print("All cells revealed. You win!")
                        elapsed_time = game.get_elapsed_time()
                        print(f"Time taken: {elapsed_time:.2f} seconds")
                        game.update_leaderboard(player_name, elapsed_time, game_won, difficulty_mode, play_date)
                        game.reveal_all_mines()
                        break
            elif choice == '2':
                row = int(input("Enter the row to mark: "))
                col = int(input("Enter the column to mark: "))
                game.mark_mine_location(row, col)
                game.print_board()
            
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main_menu()
