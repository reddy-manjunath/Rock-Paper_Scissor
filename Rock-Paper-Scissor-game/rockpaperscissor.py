import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import pygame
import random
import json
from datetime import datetime

class ModernRPSGame:
    def __init__(self, round_num=1):
        # Initialize pygame mixer for sounds
        pygame.mixer.init()
        
        # Game constants
        self.TARGET_SCORE = 5
        self.ROUND_TIMES = [60, 45, 30, 20,10]
        self.COLORS = {
            'bg': '#1B1E3D',  # Dark navy background
            'player': '#FFA500',  # Orange for player
            'computer': '#FFEA00',  # Royal blue for computer
            'text': '#FFFFFF',  # White text
            'button': '#FFFFFF',  # White buttons
            'header': '#E74C3C'  # Red header
        }
        
        # Game state
        self.round_num = round_num
        self.user_score = 0
        self.computer_score = 0
        self.time_left = self.ROUND_TIMES[self.round_num - 1]
        self.game_paused = False
        self.high_scores = self.load_high_scores()
        self.current_streak = 0
        self.best_streak = 0
        self.round_history = []
        self.choices = ["rock", "paper", "scissors"]
        
        # Setup main window
        self.root = tk.Tk()
        self.root.title(f"Rock Paper Scissors - Round {self.round_num}")
        self.root.geometry("800x800")
        self.root.configure(bg=self.COLORS['bg'])
        
        # Load sounds
        self.load_sounds()
        
        # Setup UI
        self.setup_ui()
        self.update_timer()
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
    def load_sounds(self):
        try:
            pygame.mixer.music.load("music.mp3")
            self.click_sound = pygame.mixer.Sound("click.mp3")
            self.win_sound = pygame.mixer.Sound("win.mp3")
            self.lose_sound = pygame.mixer.Sound("lose.mp3")
            pygame.mixer.music.play(-1)
        except:
            print("Sound files not found. Continuing without sound.")

    def setup_ui(self):
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Round and timer info
        self.setup_header()
        
        # Score display
        self.setup_score_display()
        
        # Game area
        self.setup_game_area()
        
        # Bottom controls
        self.setup_bottom_controls()
        
        # Statistics text area
        self.setup_statistics_area()

    def setup_header(self):
        header_frame = tk.Frame(self.main_container, bg=self.COLORS['bg'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Round number
        tk.Label(
            header_frame,
            text=f"ROUND {self.round_num}",
            font=("Arial", 24, "bold"),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        ).pack(side=tk.LEFT, padx=10)
        
        # Timer
        self.timer_label = tk.Label(
            header_frame,
            text=f"Time: {self.time_left}s",
            font=("Arial", 20),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        )
        self.timer_label.pack(side=tk.RIGHT, padx=10)

    def setup_score_display(self):
        score_frame = tk.Frame(self.main_container, bg=self.COLORS['bg'])
        score_frame.pack(fill='x', pady=(0, 20))
        
        # Player score box
        player_box = tk.Frame(score_frame, bg='white', padx=30, pady=15)
        player_box.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            player_box,
            text="PLAYER",
            font=("Arial", 14),
            bg='white',
            fg=self.COLORS['bg']
        ).pack()
        
        self.player_score_label = tk.Label(
            player_box,
            text=str(self.user_score),
            font=("Arial", 32, "bold"),
            bg='white',
            fg=self.COLORS['bg']
        )
        self.player_score_label.pack()
        
        # Computer score box
        computer_box = tk.Frame(score_frame, bg='white', padx=30, pady=15)
        computer_box.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(
            computer_box,
            text="COMPUTER",
            font=("Arial", 14),
            bg='white',
            fg=self.COLORS['bg']
        ).pack()
        
        self.computer_score_label = tk.Label(
            computer_box,
            text=str(self.computer_score),
            font=("Arial", 32, "bold"),
            bg='white',
            fg=self.COLORS['bg']
        )
        self.computer_score_label.pack()
        
        # Streak display
        self.streak_label = tk.Label(
            score_frame,
            text=f"Streak: {self.current_streak} | Best: {self.best_streak}",
            font=("Arial", 14),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        )
        self.streak_label.pack(pady=10)

    def setup_game_area(self):
        game_frame = tk.Frame(self.main_container, bg=self.COLORS['bg'])
        game_frame.pack(expand=True, fill='both', pady=20)
        
        # Player choice area
        player_frame = tk.Frame(game_frame, bg=self.COLORS['bg'])
        player_frame.pack(side=tk.LEFT, expand=True)
        
        tk.Label(
            player_frame,
            text="YOU PICKED",
            font=("Arial", 18),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        ).pack(pady=(0, 10))
        
        self.player_choice_display = self.create_choice_display(player_frame, self.COLORS['player'])
        self.player_choice_display.pack()
        
        # Result area
        result_frame = tk.Frame(game_frame, bg=self.COLORS['bg'])
        result_frame.pack(side=tk.LEFT, expand=True)
        
        self.result_label = tk.Label(
            result_frame,
            text="",
            font=("Arial", 36, "bold"),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        )
        self.result_label.pack(pady=20)
        
        self.play_again_btn = tk.Button(
            result_frame,
            text="PLAY AGAIN",
            font=("Arial", 14),
            command=self.reset_round,
            bg='white',
            fg=self.COLORS['bg'],
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        
        # Computer choice area
        computer_frame = tk.Frame(game_frame, bg=self.COLORS['bg'])
        computer_frame.pack(side=tk.RIGHT, expand=True)
        
        tk.Label(
            computer_frame,
            text="THE COMPUTER PICKED",
            font=("Arial", 18),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text']
        ).pack(pady=(0, 10))
        
        self.computer_choice_display = self.create_choice_display(computer_frame, self.COLORS['computer'])
        self.computer_choice_display.pack()

    def create_choice_display(self, parent, color):
        size = 160
        canvas = tk.Canvas(parent, width=size, height=size, bg=self.COLORS['bg'], highlightthickness=0)
        canvas.create_oval(5, 5, size-5, size-5, fill=color, outline='white', width=3)
        return canvas

    def setup_bottom_controls(self):
        control_frame = tk.Frame(self.main_container, bg=self.COLORS['bg'])
        control_frame.pack(side=tk.BOTTOM, pady=20)
        
        buttons = [
            ("RULES", self.show_rules),
            ("HIGH SCORES", self.show_high_scores),
            ("STATISTICS", self.show_statistics),
            ("RESET SCORE", lambda: self.reset_round(True)),
            ("QUIT", self.quit_game)
        ]
    
        for text, command in buttons:
            tk.Button(
                control_frame,
                text=text,
                command=command,
                font=("Arial", 12),
                bg=self.COLORS['bg'],
                fg=self.COLORS['text'],
                relief=tk.FLAT,
                padx=15,
                pady=5
            ).pack(side=tk.LEFT, padx=10)

    def setup_statistics_area(self):
        self.history_text = tk.Text(
            self.main_container,
            height=4,
            width=50,
            bg=self.COLORS['bg'],
            fg=self.COLORS['text'],
            font=("Arial", 10)
        )
        self.history_text.pack(pady=10)
        self.history_text.insert('1.0', "Game History:\n")
        self.history_text.config(state='disabled')

    def setup_keyboard_shortcuts(self):
        self.root.bind('r', lambda e: self.play_round("rock"))
        self.root.bind('p', lambda e: self.play_round("paper"))
        self.root.bind('s', lambda e: self.play_round("scissors"))
        self.root.bind('h', lambda e: self.show_high_scores())
        self.root.bind('q', lambda e: self.quit_game())

    def play_round(self, player_choice):
        if self.game_paused:
            return
            
        try:
            self.click_sound.play()
        except:
            pass
            
        computer_choice = random.choice(self.choices)
        
        # Update displays
        self.update_choice_display(self.player_choice_display, player_choice, self.COLORS['player'])
        self.update_choice_display(self.computer_choice_display, computer_choice, self.COLORS['computer'])
        
        # Determine winner and update scores
        result = self.determine_winner(player_choice, computer_choice)
        self.update_scores(result)
        self.update_history(player_choice, computer_choice, result)
        
        # Show result and play again button
        self.result_label.config(text=f"YOU {result}")
        self.play_again_btn.pack(pady=10)
        
        # Check if round is complete
        if self.user_score == self.TARGET_SCORE or self.computer_score == self.TARGET_SCORE:
            self.end_round("score_reached")

    def update_choice_display(self, canvas, choice, color):
        canvas.delete("all")
        size = 160
        
        # Draw outer circle
        canvas.create_oval(5, 5, size-5, size-5, fill=color, outline='white', width=3)
        
        # Add choice icon
        try:
            img = Image.open(f"{choice}.png")
            img = img.resize((80, 80), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            canvas.image = photo
            canvas.create_image(size//2, size//2, image=photo)
        except:
            canvas.create_text(size//2, size//2, text=choice.upper(), font=("Arial", 20), fill='white')

    def determine_winner(self, player, computer):
        if player == computer:
            return "DRAW"
        elif (
            (player == "rock" and computer == "scissors") or
            (player == "paper" and computer == "rock") or
            (player == "scissors" and computer == "paper")
        ):
            return "WIN"
        else:
            return "LOSE"

    def update_scores(self, result):
        if result == "WIN":
            self.user_score += 1
            self.current_streak += 1
            self.best_streak = max(self.current_streak, self.best_streak)
        elif result == "LOSE":
            self.computer_score += 1
            self.current_streak = 0
            
        self.player_score_label.config(text=str(self.user_score))
        self.computer_score_label.config(text=str(self.computer_score))
        self.streak_label.config(text=f"Streak: {self.current_streak} | Best: {self.best_streak}")

    def update_history(self, player_choice, computer_choice, result):
        self.round_history.append({
            'user_choice': player_choice,
            'computer_choice': computer_choice,
            'result': result,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        self.history_text.config(state='normal')
        self.history_text.insert(
            '1.0',
            f"[{self.round_history[-1]['timestamp']}] You: {player_choice} vs Computer: {computer_choice} - {result}\n"
        )
        self.history_text.config(state='disabled')

    def update_timer(self):
        if not self.game_paused and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.time_left}s")
            
            if self.time_left <= 10:
                self.timer_label.config(fg='red')
            
            self.root.after(1000, self.update_timer)
        elif self.time_left <= 0:
            self.end_round("time_up")

    def end_round(self, end_type):
        winner = "User" if self.user_score > self.computer_score else "Computer"
        
        try:
            if winner == "User":
                self.win_sound.play()
            else:
                self.lose_sound.play()
        except:
            pass
            
        self.save_high_score()
        
        if end_type == "score_reached":
            if self.round_num < 6:
                if messagebox.askyesno(
                    "Round Complete",
                    f"Round {self.round_num} complete!\n"
                    f"{winner} won!\n"
                    f"Score: You {self.user_score} - Computer {self.computer_score}\n"
                    f"Best Streak: {self.best_streak}\n\n"
                    f"Would you like to proceed to round {self.round_num + 1}?"
                ):
                    self.root.destroy()
                    self.start_new_round(self.round_num + 1)
                else:
                    self.quit_game()
            else:
                self.quit_game()
        elif end_type == "time_up":
            if messagebox.showinfo(
                "Time's Up!",
                f"Time's up!\n"
                f"Final Score: You {self.user_score} - Computer {self.computer_score}\n"
                f"Best Streak: {self.best_streak}"
            ):
                self.quit_game()

    def start_new_round(self, round_num):
        new_game = ModernRPSGame(round_num)
        new_game.root.mainloop()

    def reset_round(self, reset_all=False):
        if reset_all:
            self.user_score = 0
            self.computer_score = 0
            self.current_streak = 0
            self.best_streak = 0
            self.round_history = []
            
        self.game_paused = False
        self.time_left = self.ROUND_TIMES[self.round_num - 1]
        self.timer_label.config(fg=self.COLORS['text'])
        
        # Clear displays
        self.update_choice_display(self.player_choice_display, "", self.COLORS['player'])
        self.update_choice_display(self.computer_choice_display, "", self.COLORS['computer'])
        self.result_label.config(text="")
        self.play_again_btn.pack_forget()
        
        # Update score displays
        self.player_score_label.config(text=str(self.user_score))
        self.computer_score_label.config(text=str(self.computer_score))
        self.streak_label.config(text=f"Streak: {self.current_streak} | Best: {self.best_streak}")
        
        # Clear history display
        self.history_text.config(state='normal')
        self.history_text.delete('1.0', tk.END)
        self.history_text.insert('1.0', "Game History:\n")
        self.history_text.config(state='disabled')
        
        # Restart timer
        self.update_timer()

    def show_rules(self):
        rules_text = """
        Game Rules:
        
        1. Choose rock, paper, or scissors using keyboard shortcuts:
           - 'R' for Rock
           - 'P' for Paper
           - 'S' for Scissors
        
        2. Win conditions:
           - Rock crushes Scissors
           - Paper covers Rock
           - Scissors cuts Paper
        
        3. Scoring:
           - First to 5 points wins the round
           - Each round has a time limit
           - Round 1: 60 seconds
           - Round 2: 45 seconds
           - Round 3: 30 seconds
           - Round 4: 20 seconds
        
        4. Features:
           - Track your winning streak
           - View game history
           - Check high scores
           - Reset scores at any time
        """
        
        messagebox.showinfo("Game Rules", rules_text)

    def show_statistics(self):
        if not self.round_history:
            messagebox.showinfo("Statistics", "No games played yet!")
            return
            
        total_games = len(self.round_history)
        wins = sum(1 for game in self.round_history if game['result'] == 'WIN')
        losses = sum(1 for game in self.round_history if game['result'] == 'LOSE')
        draws = sum(1 for game in self.round_history if game['result'] == 'DRAW')
        
        win_rate = (wins / total_games) * 100
        
        stats_text = f"""
        Game Statistics:
        
        Total Games: {total_games}
        Wins: {wins}
        Losses: {losses}
        Draws: {draws}
        Win Rate: {win_rate:.1f}%
        Best Streak: {self.best_streak}
        Current Streak: {self.current_streak}
        
        Most Used Choice: {self.get_most_used_choice()}
        Best Performing Choice: {self.get_best_choice()}
        """
        
        messagebox.showinfo("Statistics", stats_text)

    def get_most_used_choice(self):
        if not self.round_history:
            return "N/A"
            
        choice_counts = {}
        for game in self.round_history:
            choice = game['user_choice']
            choice_counts[choice] = choice_counts.get(choice, 0) + 1
            
        return max(choice_counts.items(), key=lambda x: x[1])[0].capitalize()

    def get_best_choice(self):
        if not self.round_history:
            return "N/A"
            
        choice_stats = {}
        for game in self.round_history:
            choice = game['user_choice']
            if choice not in choice_stats:
                choice_stats[choice] = {'wins': 0, 'total': 0}
            
            choice_stats[choice]['total'] += 1
            if game['result'] == 'WIN':
                choice_stats[choice]['wins'] += 1
        
        best_choice = max(
            choice_stats.items(),
            key=lambda x: (x[1]['wins'] / x[1]['total'] if x[1]['total'] > 0 else 0)
        )
        
        return best_choice[0].capitalize()

    def load_high_scores(self):
        try:
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        except:
            return []

    def save_high_score(self):
        score_entry = {
            'player_score': self.user_score,
            'computer_score': self.computer_score,
            'round': self.round_num,
            'streak': self.best_streak,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.high_scores.append(score_entry)
        self.high_scores.sort(key=lambda x: (-x['player_score'], x['computer_score']))
        self.high_scores = self.high_scores[:10]  # Keep only top 10
        
        try:
            with open('high_scores.json', 'w') as f:
                json.dump(self.high_scores, f)
        except:
            print("Could not save high scores")

    def show_high_scores(self):
        if not self.high_scores:
            messagebox.showinfo("High Scores", "No high scores yet!")
            return
            
        scores_text = "TOP 10 HIGH SCORES:\n\n"
        for i, score in enumerate(self.high_scores, 1):
            scores_text += f"{i}. Player {score['player_score']} - {score['computer_score']} Computer\n"
            scores_text += f"   Round: {score['round']} | Best Streak: {score['streak']}\n"
            scores_text += f"   Date: {score['timestamp']}\n\n"
            
        messagebox.showinfo("High Scores", scores_text)

    def quit_game(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    game = ModernRPSGame()
    game.root.mainloop()