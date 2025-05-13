import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

# Connect to MySQL (XAMPP)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="tictactoe_game"
)
cursor = conn.cursor()

# Ensure tables exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        wins INT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe Login")
        self.root.geometry("300x200")
        self.root.configure(bg="#f5f5f5")

        frame = tk.Frame(root, bg="#f5f5f5")
        frame.pack(expand=True)

        tk.Label(frame, text="Enter your name:", font=("Arial", 12), bg="#f5f5f5").pack(pady=10)
        self.name_entry = tk.Entry(frame, font=("Arial", 12))
        self.name_entry.pack()

        tk.Button(frame, text="Login / Register", font=("Arial", 11), command=self.login).pack(pady=10)
        tk.Button(frame, text="Leaderboard", command=self.show_leaderboard).pack()

        self.user_id = None

    def login(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return

        cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
        result = cursor.fetchone()
        if result:
            self.user_id = result[0]
        else:
            cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
            conn.commit()
            self.user_id = cursor.lastrowid
            cursor.execute("INSERT INTO scores (user_id, wins) VALUES (%s, 0)", (self.user_id,))
            conn.commit()

        self.root.destroy()
        main = tk.Tk()
        TicTacToe(main, self.user_id, name)
        main.mainloop()

    def show_leaderboard(self):
        leaderboard_win = tk.Toplevel(self.root)
        leaderboard_win.title("Leaderboard")
        leaderboard_win.geometry("300x300")

        tree = ttk.Treeview(leaderboard_win, columns=("Name", "Wins"), show="headings")
        tree.heading("Name", text="Player Name")
        tree.heading("Wins", text="Wins")
        tree.column("Name", width=150)
        tree.column("Wins", width=100)
        tree.pack(padx=10, pady=10)

        cursor.execute("""
            SELECT users.name, scores.wins
            FROM scores
            INNER JOIN users ON scores.user_id = users.id
            ORDER BY scores.wins DESC
            LIMIT 10
        """)
        for name, wins in cursor.fetchall():
            tree.insert("", tk.END, values=(name, wins))


class TicTacToe:
    def __init__(self, root, user_id, username):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.root.title(f"Tic-Tac-Toe - {self.username}")
        self.root.geometry("350x400")
        self.turn = "X"
        self.board = [None] * 9
        self.buttons = []

        tk.Label(self.root, text=f"Player: {self.username}", font=("Arial", 12)).pack(pady=5)

        self.status = tk.Label(self.root, text="Turn: X", font=("Arial", 12, "bold"))
        self.status.pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack()

        for i in range(9):
            btn = tk.Button(frame, text="", width=10, height=4,
                            font=("Arial", 14), command=lambda i=i: self.click(i))
            btn.grid(row=i//3, column=i%3)
            self.buttons.append(btn)

        tk.Button(self.root, text="Reset", command=self.reset).pack(pady=10)

    def click(self, i):
        if not self.board[i]:
            self.board[i] = self.turn
            self.buttons[i].config(text=self.turn, state="disabled")

            if self.check_winner():
                self.status.config(text=f"{self.turn} wins!")
                if self.turn == "X":
                    self.save_win()
                self.disable_all()
                messagebox.showinfo("Game Over", f"{self.turn} wins!")
            elif None not in self.board:
                self.status.config(text="It's a Draw!")
                messagebox.showinfo("Game Over", "It's a Draw!")
            else:
                self.turn = "O" if self.turn == "X" else "X"
                self.status.config(text=f"Turn: {self.turn}")

    def check_winner(self):
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a]:
                return True
        return False

    def disable_all(self):
        for btn in self.buttons:
            btn.config(state="disabled")

    def save_win(self):
        cursor.execute("UPDATE scores SET wins = wins + 1 WHERE user_id = %s", (self.user_id,))
        conn.commit()

    def reset(self):
        self.board = [None] * 9
        for btn in self.buttons:
            btn.config(text="", state="normal")
        self.turn = "X"
        self.status.config(text="Turn: X")

# Main Execution
if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
    cursor.close()
    conn.close()
