import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import random
from tkinter import ttk  # Make sure this import is present
import threading
import time
from datetime import datetime, time as dt_time, timedelta
import tkinter.font as tkfont
import json
from pathlib import Path
from PIL import Image as PILImage
from PIL import ImageTk
import io
from urllib.request import urlopen
import winsound  # For Windows systems
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import os
from reportlab.pdfgen import canvas
import traceback
from fpdf import FPDF
import calendar
import shutil
import pytz

# Add this near the top of your file, with other global variables
streak_counter = 0
streak_label = None

# Near the top of your file, with other global variables
global pattern_combo
pattern_combo = None

# Add these global variables near the top of your file
grade_counts = {"A": 0, "B": 0, "F": 0}
grade_label = None

# Add these constants near the top of your file
DATA_DIR = Path.home() / ".trading_assistant"
STATE_FILE = DATA_DIR / "app_state.json"

# Add these constants near your other constants
GOAL_HISTORY_FILE = DATA_DIR / "goal_history.json"

SEGMENTS = [
    "Pre-market prep",
    "9:30 - 10:00",
    "10:00 - 11:30",
    "11:30 - 2:00"
]

PREMARKET_CATEGORIES = ["Engagement", "Catalyst Research", "Opening Game Plans"]
REGULAR_CATEGORIES = ["Engagement", "Entries", "Sizing", "Exit strategy"]

# Add this near the top with other global variables and constants
PSYCHOLOGICAL_GUIDANCE = {
    "Calm & Focused": "Ideal trading state. Maintain this mindset by:\n- Taking breaks when needed\n- Sticking to your trading plan\n- Focusing on process over outcome",
    
    "Fear of Loss": "Common but dangerous emotion:\n- Review your position size\n- Confirm your stop loss\n- Remember: losses are part of trading",
    
    "Fear of Missing Profit": "FOMO's cousin:\n- Stick to your targets\n- There will always be other trades\n- Focus on your current position",
    
    "Fear of Being Wrong": "Remember:\n- Being wrong is part of trading\n- Focus on risk management\n- Your worth isn't tied to one trade",
    
    "Anxious about Position Size": "Size management check:\n- Consider reducing position\n- Review your risk parameters\n- Only trade what you're comfortable with",
    
    "FOMO": "⚠️ HIGH RISK STATE ⚠️\n- Step away from the computer\n- No new trades\n- Review why you're feeling this way",
    
    "Revenge Trading": "⚠️ STOP TRADING NOW ⚠️\n- Close platform\n- Take a walk\n- Return tomorrow with fresh perspective",
    
    "Frustrated": "⚠️ DANGER STATE ️\n- Stop trading\n- Clear your head\n- Review what's frustrating you",
    
    "Overconfident": "Caution needed:\n- Review your rules\n- Double-check your setups\n- Maintain proper position sizing",
    
    "Impulsive": "High risk behavior:\n- Slow down\n- Check your trading plan\n- Validate setups thoroughly",
    
    "Hesitant/Frozen": "Analysis paralysis:\n- Review your trading plan\n- Start with smaller size\n- Focus on A+ setups only",
    
    "Excited/Euphoric": "Be careful:\n- Maintain position sizing\n- Stick to your rules\n- Don't overtrade"
}

# First, add this near your other global variables at the top
emotional_log_text = None

# Add this with your other global variables at the top of the file
goal_entries = {}  # Initialize as empty dictionary

# Add these near the top of your file with other global variables
global entry_daily_risk, allocation_label
entry_daily_risk = None
allocation_label = None

# Add this function to handle emotional state submission
def submit_emotional_state():
    # Check if user has selected an emotional state from the dropdown
    selected_emotion = emotion_var.get()
    if not selected_emotion:
        messagebox.showwarning("Selection Required", "Please select an emotional state.")
        return
        
    # Open dialog to collect contextual information about what caused this emotional state
    trigger = simpledialog.askstring(
        "Emotion Trigger",
        "What triggered this emotional state?",
        parent=root
    )
    
    # Only proceed with logging if user provided context about the trigger
    if trigger:
        # Get current timestamp for the emotional state entry
        current_time = datetime.now().strftime("%H:%M")
        
        # Create a formatted log entry with timestamp, emotion and trigger details
        emotional_entry = f"{current_time} - {selected_emotion}\nTrigger: {trigger}\n\n"
        
        # Add the emotional state entry to the Daily Review Checklist (DRC) tab's log
        emotional_log_text.insert(tk.END, emotional_entry)
        
        # If guidance exists for this emotion, display relevant psychological tips
        if selected_emotion in PSYCHOLOGICAL_GUIDANCE:
            messagebox.showinfo("Psychological Guidance", 
                              f"Guidance for {selected_emotion}:\n\n{PSYCHOLOGICAL_GUIDANCE[selected_emotion]}")
            
        # Reset the emotion selection interface to its default state
        emotion_var.set('')
        guidance_text.delete('1.0', tk.END)
        guidance_text.insert('1.0', "Select your emotional state for guidance")
    # Ensure the newest entry is visible in the emotional log
    emotional_log_text.see(tk.END)
    # Alternative: winsound.Beep(1000, 100)  # 1000Hz for 100ms

# before create_goal_tracking_tab is called

def increment_consistency(consistency_var):
    """
    Increment the consistency counter for goal tracking.
    Format: "days_followed/total_days"
    """
    try:
        current = consistency_var.get()
        days_followed, total_days = map(int, current.split('/'))
        days_followed += 1
        total_days += 1
        consistency_var.set(f"{days_followed}/{total_days}")
    except ValueError:
        consistency_var.set("1/1")

def calculate_grade(score, total):
    global streak_counter, streak_label, grade_counts, grade_label
    
    if score == total:
        streak_counter += 1
        update_streak_counter()
        grade = "A"
    elif score >= total / 3:
        streak_counter = 0
        update_streak_counter()
        grade = "B"
    else:
        streak_counter = 0
        update_streak_counter()
        grade = "F"
    
    grade_counts[grade] += 1
    update_grade_tally()
    
    return grade

# Add this new function to update the streak counter
def update_streak_counter():
    global streak_label
    if streak_label:
        streak_label.destroy()
    
    color = "black"
    text = f"Streak: {streak_counter}"
    
    if streak_counter >= 4:
        color = "gold"
        text += " 🏆 Legendary!"
    elif streak_counter >= 3:
        color = "purple"
        text += " 🚀 Incredible!"
    elif streak_counter >= 2:
        color = "blue"
        text += " 🔥 On Fire!"
    elif streak_counter >= 1:
        color = "green"
        text += " 👍 Great job!"
    
    streak_label = tk.Label(gamification_frame, text=text, fg=color, font=("Arial", 12, "bold"))
    streak_label.pack(anchor='w', pady=(5, 0))

# Add this new function to update the grade tally
def update_grade_tally():
    global grade_label
    if grade_label:
        grade_label.config(text=f"Grades: A: {grade_counts['A']}, B: {grade_counts['B']}, F: {grade_counts['F']}")

# Function to calculate EV and R/R
def calculate_ev():
    global entry_daily_risk, allocation_label
    try:
        # Validate that all fields have values
        if not all([entry_risk.get().strip(), 
                   entry_reward.get().strip(), 
                   entry_probability.get().strip(),
                   entry_daily_risk.get().strip()]):
            messagebox.showerror("Input Error", "Please fill in all fields")
            return
            
        # Try to convert inputs to floats with more specific error messages
        try:
            risk = float(entry_risk.get())
        except ValueError:
            messagebox.showerror("Input Error", "Risk must be a valid number")
            return
            
        try:
            reward = float(entry_reward.get())
        except ValueError:
            messagebox.showerror("Input Error", "Reward must be a valid number")
            return
            
        try:
            probability_of_success = float(entry_probability.get())
        except ValueError:
            messagebox.showerror("Input Error", "Probability must be a valid number")
            return
            
        try:
            daily_risk = float(entry_daily_risk.get())
        except ValueError:
            messagebox.showerror("Input Error", "Daily risk must be a valid number")
            return
        
        # Validate probability range
        if probability_of_success < 0 or probability_of_success > 100:
            messagebox.showerror("Input Error", "Probability must be between 0 and 100")
            return
            
        # Validate positive numbers
        if risk <= 0 or reward <= 0 or daily_risk <= 0:
            messagebox.showerror("Input Error", "Risk, reward, and daily risk must be positive numbers")
            return
        
        probability_success = probability_of_success / 100
        probability_loss = 1 - probability_success
        normalized_reward = reward / risk
        ev = (normalized_reward * probability_success) - (1 * probability_loss)
        
        # Calculate risk allocation based on EV
        if ev < 1.00:
            risk_percentage = 0  # Don't take the trade
        elif ev <= 1.19:
            risk_percentage = 5
        elif ev <= 1.39:
            risk_percentage = 8
        elif ev <= 1.59:
            risk_percentage = 10
        elif ev <= 1.79:
            risk_percentage = 15
        elif ev <= 1.99:
            risk_percentage = 20
        elif ev <= 2.40:
            risk_percentage = 25
        else:
            risk_percentage = 30
            
        # Calculate dollar amount for this trade
        trade_risk = (risk_percentage / 100) * daily_risk
        
        result_label.config(text=f"Expected Value (EV): {ev:.2f}")
        rr_label.config(text=f"Risk/Reward (R/R): 1:{normalized_reward:.2f}")
        allocation_label.config(text=f"Risk Allocation: {risk_percentage}% (${trade_risk:.2f})")
        
        if ev < 1.00:
            trade_label.config(text="DO NOT TAKE", fg="red")
        elif ev < 1.40:
            trade_label.config(text="C Trade - Small Size", fg="orange")
        elif ev < 1.80:
            trade_label.config(text="B Trade", fg="#DAA520")  # Using goldenrod color instead of yellow
        else:
            trade_label.config(text="A TRADE", fg="green")
    
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

# Function to clear specific input fields related to the Expected Value calculation
def clear_ev_inputs():
    global entry_daily_risk, allocation_label  # Add this line
    entry_reward.delete(0, tk.END)
    entry_probability.delete(0, tk.END)
    entry_risk.delete(0, tk.END)
    result_label.config(text="Expected Value (EV):")
    rr_label.config(text="Risk/Reward (R/R):")
    allocation_label.config(text="Risk Allocation:")
    trade_label.config(text="")


# Function to submit the trade and update the output
def submit():
    ticker = ticker_entry.get()
    setup = setup_entry.get() # type: ignore
    trade = trade_entry.get() # type: ignore
    reasons2sell = reasons2sell_entry.get("1.0", tk.END).strip()  # type: ignore # Get the reasons2sell text
    trade_rating = trade_rating_var.get() # type: ignore

    rules_followed = {
        "Stock in play": stock_in_play_var.get(),
        "Solid trade entry": solid_trade_entry_var.get(),
        "Followed exit strategy": followed_exit_strategy_var.get()
    }

    score = sum(rules_followed.values())
    grade = calculate_grade(score, len(rules_followed))

    mistakes = []
    if not rules_followed["Stock in play"]:
        mistakes.append("BAD STOCK CHOICE")
    if not rules_followed["Solid trade entry"]:
        mistakes.append("BAD ENTRY")
    if not rules_followed["Followed exit strategy"]:
        mistakes.append("DID NOT FOLLOW EXIT STRATEGY")

    mistake_text = f" | Mistake: {'; '.join(mistakes).upper()}" if mistakes else ""
    grade_text = f"{grade}{mistake_text}"

    grade_label.config(text=f"Grade: {grade}")

    trade_info = {
        "Ticker": ticker,
        "Setup": setup,
        "Trade": trade,
        "Reasons2sell": reasons2sell,  # Add reasons2sell to trade_info
        "Trade Rating": trade_rating,
        "Grade": grade_text,
        "Rules Followed": rules_followed
    }
    trades.append(trade_info)

    trade_summary = f"Ticker: {ticker} | Setup: {setup} | Trade: {trade} | Reasons2sell: {reasons2sell} | Rating: {trade_rating} | Grade: {grade_text}"
    
    # Insert at the beginning of the output text boxes
    output_text.insert("1.0", trade_summary + "\n")
    drc_trades_text.insert("1.0", trade_summary + "\n")
    
    # Ensure the top of both text boxes is visible
    output_text.see("1.0")
    drc_trades_text.see("1.0")

    if mistakes:
        # Temporarily disable the topmost attribute
        root.attributes('-topmost', False)
        
        # Create a custom dialog box for analyzing trading mistakes and planning corrections
        class CustomDialog(simpledialog.Dialog):
            def body(self, master):
                # Set up the dialog window specifically for analyzing trading mistakes
                self.title("Mistake Analysis")
                # Create a label that prompts the user to reflect on their mistakes and develop a correction strategy
                tk.Label(master, text="Why did you make these mistakes, and what can you do in the next trade to correct them?").grid(row=0, pady=5)
                # Create text input area for user's response with word wrapping
                self.e1 = tk.Text(master, wrap=tk.WORD, width=50, height=5)
                self.e1.grid(row=1, pady=5)
                # Return text widget for initial focus when dialog opens
                return self.e1  # initial focus

            def apply(self):
                self.result = self.e1.get("1.0", tk.END).strip()

        # Show the custom dialog
        dialog = CustomDialog(root)
        response = dialog.result

        # Re-enable the topmost attribute
        root.attributes('-topmost', True)
        
        if response:
            output_text.insert(tk.END, f"Correction Plan: {response}\n")
            output_text.see(tk.END)

    clear_all_inputs() # type: ignore
    messagebox.showinfo("Trade Submitted", "Trade details submitted successfully!")

    update_grade_tally()


# Main window setup
root = tk.Tk()
root.title("Trading assistant")

# Set the window size and position
window_width = 649
window_height = 1008
x_position = root.winfo_screenwidth() - window_width - 20  # Dynamic positioning from right edge
y_position = 0

# Set the window's size and position
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Set the window to be always on top
root.attributes('-topmost', True)

# Create a notebook (tab control)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Create the main screen tab
main_screen_tab = ttk.Frame(notebook)
notebook.add(main_screen_tab, text="Main Screen")

# Create the DRC tab
drc_tab = ttk.Frame(notebook)
notebook.add(drc_tab, text="Daily Report Card")

# Create the new Pre-market prep tab
premarket_tab = ttk.Frame(notebook)
notebook.add(premarket_tab, text="Pre-market prep")

# Function to create content for the Pre-market prep tab
def create_premarket_content(parent):
    global eps_estimate_entry, eps_actual_entry, rev_estimate_entry, rev_actual_entry, eps_percentage_var, rev_percentage_var

    # Create a canvas with scrollbar
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Create the content frame inside the scrollable frame
    content_frame = ttk.Frame(scrollable_frame, padding="20")
    content_frame.pack(fill=tk.BOTH, expand=True)

    title_label = ttk.Label(content_frame, text="Pre-market Preparation", font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))

    # Market Overview section
    market_overview_frame = ttk.LabelFrame(content_frame, text="Market Overview", padding="10")
    market_overview_frame.pack(fill=tk.X, pady=(0, 20))

    market_overview = tk.Text(market_overview_frame, height=5, width=70, wrap=tk.WORD, font=('Arial', 9))
    market_overview.pack(fill=tk.BOTH, expand=True)

    # Earnings movers section
    earnings_frame = ttk.LabelFrame(content_frame, text="Earnings movers", padding="10")
    earnings_frame.pack(fill=tk.X, pady=(0, 20))

    # Create a frame for the input fields
    inputs_frame = ttk.Frame(earnings_frame)
    inputs_frame.pack(fill=tk.X)

    # Ticker input
    ttk.Label(inputs_frame, text="Ticker:").grid(row=0, column=0, sticky="e", padx=(0, 5), pady=5)
    ticker_entry = ttk.Entry(inputs_frame, width=10)
    ticker_entry.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)

    # Short interest input
    ttk.Label(inputs_frame, text="Short int:").grid(row=1, column=0, sticky="e", padx=(0, 5), pady=5)
    short_int_entry = ttk.Entry(inputs_frame, width=10)
    short_int_entry.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=5)

    # Institution ownership input
    ttk.Label(inputs_frame, text="Institution owner%:").grid(row=2, column=0, sticky="e", padx=(0, 5), pady=5)
    inst_owner_entry = ttk.Entry(inputs_frame, width=10)
    inst_owner_entry.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=5)

    # EPS inputs
    ttk.Label(inputs_frame, text="EPS Estimate:").grid(row=0, column=2, sticky="e", padx=(0, 5), pady=5)
    eps_estimate_entry = ttk.Entry(inputs_frame, width=10)
    eps_estimate_entry.grid(row=0, column=3, sticky="w", padx=(0, 10), pady=5)

    ttk.Label(inputs_frame, text="EPS Actual:").grid(row=0, column=4, sticky="e", padx=(0, 5), pady=5)
    eps_actual_entry = ttk.Entry(inputs_frame, width=10)
    eps_actual_entry.grid(row=0, column=5, sticky="w", padx=(0, 10), pady=5)

    # Revenue inputs
    ttk.Label(inputs_frame, text="Rev Estimate:").grid(row=1, column=2, sticky="e", padx=(0, 5), pady=5)
    rev_estimate_entry = ttk.Entry(inputs_frame, width=10)
    rev_estimate_entry.grid(row=1, column=3, sticky="w", padx=(0, 10), pady=5)

    ttk.Label(inputs_frame, text="Rev Actual:").grid(row=1, column=4, sticky="e", padx=(0, 5), pady=5)
    rev_actual_entry = ttk.Entry(inputs_frame, width=10)
    rev_actual_entry.grid(row=1, column=5, sticky="w", padx=(0, 10), pady=5)

    # Beat/Miss percentages
    eps_percentage_var = tk.StringVar()
    rev_percentage_var = tk.StringVar()

    ttk.Label(inputs_frame, text="EPS Beat/Miss:").grid(row=2, column=2, sticky="e", padx=(0, 5), pady=5)
    ttk.Label(inputs_frame, textvariable=eps_percentage_var).grid(row=2, column=3, sticky="w", padx=(0, 10), pady=5)

    ttk.Label(inputs_frame, text="Rev Beat/Miss:").grid(row=2, column=4, sticky="e", padx=(0, 5), pady=5)
    ttk.Label(inputs_frame, textvariable=rev_percentage_var).grid(row=2, column=5, sticky="w", padx=(0, 10), pady=5)

    # Calculate button
    calculate_button = ttk.Button(inputs_frame, text="Calculate", command=update_percentages)
    calculate_button.grid(row=3, column=2, columnspan=4, pady=(10, 0))

    # Guidance input
    ttk.Label(inputs_frame, text="Guidance:").grid(row=4, column=0, sticky="e", padx=(0, 5), pady=5)
    guidance_entry = ttk.Entry(inputs_frame, width=10)
    guidance_entry.grid(row=4, column=1, sticky="w", padx=(0, 10), pady=5)

    # Catalyst rating input
    ttk.Label(inputs_frame, text="Catalyst rating:").grid(row=4, column=2, sticky="e", padx=(0, 5), pady=5)
    catalyst_rating = ttk.Spinbox(inputs_frame, from_=-10, to=10, width=5)
    catalyst_rating.grid(row=4, column=3, sticky="w", padx=(0, 10), pady=5)
    ttk.Label(inputs_frame, text="(-10 to +10)").grid(row=4, column=4, sticky="w", padx=(0, 5), pady=5)

    # Gap outside of significant range question
    ttk.Label(inputs_frame, text="Gap outside of significant range?").grid(row=5, column=0, columnspan=2, sticky="e", padx=(0, 5), pady=5)
    gap_range = ttk.Combobox(inputs_frame, values=["Yes", "No"], width=5, state="readonly")
    gap_range.grid(row=5, column=2, sticky="w", padx=(0, 10), pady=5)
    gap_range.set("No")  # Default value

    # Notes input
    ttk.Label(inputs_frame, text="Notes:").grid(row=6, column=0, sticky="e", padx=(0, 5), pady=5)
    notes_entry = ttk.Entry(inputs_frame, width=50)
    notes_entry.grid(row=6, column=1, columnspan=5, sticky="ew", padx=(0, 10), pady=5)

    # Update the add_earnings_mover function to include the new fields
    add_button = ttk.Button(inputs_frame, text="Add", command=lambda: add_earnings_mover(
        ticker_entry, eps_percentage_var, rev_percentage_var, guidance_entry, 
        catalyst_rating, gap_range, notes_entry, short_int_entry, inst_owner_entry, earnings_text))
    add_button.grid(row=7, column=0, columnspan=6, pady=(10, 0))

    # Text widget to display added earnings movers
    earnings_text = tk.Text(earnings_frame, height=8, width=70, wrap=tk.WORD)
    earnings_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    # Day 2 movers section
    day2_frame = ttk.LabelFrame(content_frame, text="Day 2 movers and other catalysts -  go through ALL stocks that had day 1 earnings moves prior trading day", padding="10")
    day2_frame.pack(fill=tk.X, pady=(0, 20))

    day2_text = tk.Text(day2_frame, height=5, width=70, wrap=tk.WORD, font=('Arial', 9))
    day2_text.pack(fill=tk.BOTH, expand=True)

    # Top 2 to watch and Opening game plan section
    top2_gameplan_frame = ttk.LabelFrame(content_frame, text="Top 2 to Watch and Opening Game Plan", padding="10")
    top2_gameplan_frame.pack(fill=tk.X, pady=(0, 20))

    # Top 2 to watch
    top2_frame = ttk.Frame(top2_gameplan_frame)
    top2_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(top2_frame, text="1:").pack(anchor='w', padx=(0, 5))
    top1_entry = ttk.Entry(top2_frame)
    top1_entry.pack(fill=tk.X, padx=(0, 10), pady=(0, 5))

    ttk.Label(top2_frame, text="2:").pack(anchor='w', padx=(0, 5))
    top2_entry = ttk.Entry(top2_frame)
    top2_entry.pack(fill=tk.X, padx=(0, 10))

    # New question and input boxes
    question_label = ttk.Label(top2_gameplan_frame, text="What makes these two catalysts/stocks better than the others?")
    question_label.pack(anchor='w', pady=(10, 5))

    reason_frame = ttk.Frame(top2_gameplan_frame)
    reason_frame.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(reason_frame, text="1:").pack(anchor='w', padx=(0, 5))
    reason1_entry = ttk.Entry(reason_frame)
    reason1_entry.pack(fill=tk.X, padx=(0, 10), pady=(0, 5))

    ttk.Label(reason_frame, text="2:").pack(anchor='w', padx=(0, 5))
    reason2_entry = ttk.Entry(reason_frame)
    reason2_entry.pack(fill=tk.X, padx=(0, 10), pady=(0, 5))

    # Opening play strategies
    strategies = [
        "Pre-market range break",
        "Back-through open",
        "Gap, give, and go",
        "Hitchhiker"
    ]

    strategy_entries = {}
    strategy_frame = ttk.Frame(top2_gameplan_frame)
    strategy_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # Define a smaller font
    small_font = ('TkDefaultFont', 9)

    for strategy in strategies:
        strategy_label = ttk.Label(strategy_frame, text=f"{strategy}:", font=small_font)
        strategy_label.pack(anchor='w', pady=(10, 5))
        
        entry_frame = ttk.Frame(strategy_frame)
        entry_frame.pack(fill=tk.X)
        entry_frame.columnconfigure(0, weight=1)
        entry_frame.columnconfigure(1, weight=1)
        
        entry1 = tk.Text(entry_frame, width=30, height=4, wrap=tk.WORD, font=small_font)
        entry1.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        entry2 = tk.Text(entry_frame, width=30, height=4, wrap=tk.WORD, font=small_font)
        entry2.grid(row=0, column=1, sticky='ew')
        
        strategy_entries[strategy] = (entry1, entry2)

    return content_frame, market_overview, earnings_text, day2_text, top1_entry, top2_entry, reason1_entry, reason2_entry, strategy_entries

def create_goal_setting_frame(parent):
    global goal_entries
    goal_frame = ttk.Frame(parent, padding="10")
    goal_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
    
    # Header
    ttk.Label(goal_frame, text="Today's Trading Process Goal:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(goal_frame, 
             text="Focus on specific, measurable actions that are within your control",
             font=("Arial", 9)).grid(row=1, column=0, sticky="w", pady=(0,5))
    
    # Main Goal
    ttk.Label(goal_frame, text="Specific Process Goal:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w")
    process_text = tk.Text(goal_frame, height=2, width=60, wrap=tk.WORD)
    process_text.grid(row=3, column=0, sticky="ew", pady=(0,5), padx=(0,20))
    
    # Lead & Lag Measures
    ttk.Label(goal_frame, text="Lead Measure (Action I'll take):", font=("Arial", 9)).grid(row=4, column=0, sticky="w")
    lead_measure = ttk.Entry(goal_frame, width=60)
    lead_measure.grid(row=5, column=0, sticky="ew", pady=(0,5), padx=(0,20))
    
    ttk.Label(goal_frame, text="Lag Measure (How I'll know I succeeded):", font=("Arial", 9)).grid(row=6, column=0, sticky="w")
    lag_measure = ttk.Entry(goal_frame, width=60)
    lag_measure.grid(row=7, column=0, sticky="ew", pady=(0,5), padx=(0,20))
    
    # Commitment
    ttk.Label(goal_frame, text="Why this goal matters today:", font=("Arial", 9)).grid(row=8, column=0, sticky="w")
    commitment = ttk.Entry(goal_frame, width=60)
    commitment.grid(row=9, column=0, sticky="ew", pady=(0,5), padx=(0,20))
    
    # Obstacles and Solutions
    ttk.Label(goal_frame, text="Potential obstacle:", font=("Arial", 9)).grid(row=10, column=0, sticky="w")
    obstacle_entry = ttk.Entry(goal_frame, width=60)
    obstacle_entry.grid(row=11, column=0, sticky="ew", pady=(0,5), padx=(0,20))
    
    ttk.Label(goal_frame, text="My solution:", font=("Arial", 9)).grid(row=12, column=0, sticky="w")
    solution_entry = ttk.Entry(goal_frame, width=60)
    solution_entry.grid(row=13, column=0, sticky="ew", pady=(0,5), padx=(0,20))
    
    # End of Day Review
    ttk.Label(goal_frame, text="End of Day Review:", font=("Arial", 9, "bold")).grid(row=14, column=0, sticky="w", pady=(10,0))
    ttk.Label(goal_frame, 
             text="• Did I follow my process?\n�� What worked/didn't work?\n• What will I adjust tomorrow?",
             justify="left", font=("Arial", 9)).grid(row=15, column=0, sticky="w")
    review_text = tk.Text(goal_frame, height=3, width=60, wrap=tk.WORD)
    review_text.grid(row=16, column=0, sticky="ew", pady=(0,5), padx=(0,20))
    
    goal_frame.columnconfigure(0, weight=1)
    
    # Update the global dictionary with the new entries
    goal_entries.update({
        "Process": process_text,
        "Lead": lead_measure,
        "Lag": lag_measure,
        "Commitment": commitment,
        "Obstacle": obstacle_entry,
        "Solution": solution_entry,
        "Review": review_text
    })
    
    return goal_frame  # Only return the frame, not goal_entries

def export_drc_data():
    try:
        # Create file path
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"DRC_Report_{current_date}.pdf"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if not file_path:
            return
            
        # Debug print function
        def print_debug(msg):
            print(f"DEBUG: {msg}")
        
        # Create the PDF in landscape orientation
        width, height = letter[::-1]  # Landscape
        c = canvas.Canvas(file_path, pagesize=(width, height))
        current_y = height - 72
        line_height = 15

        # Add header with date and title
        def add_header():
            c.setFont("Helvetica", 12)
            c.drawString(72, height - 70, f"Date: {datetime.now().strftime('%B %d, %Y')}")
            c.line(72, height - 80, width - 72, height - 80)  # Horizontal line under header
            return height - 100  # Return new Y position after header

        def add_section(title, content, font_size=12, indent=0, section_color=(0.9, 0.9, 0.9), is_main_header=False):
            nonlocal current_y
            
            # Check if we need a new page
            if current_y < 150:
                c.showPage()
                c.setPageSize((width, height))
                current_y = add_header()
            
            # Draw title section
            if is_main_header:
                c.setFillColorRGB(0.1, 0.2, 0.4)
                c.rect(72, current_y - 5, width - 144, 30, fill=True)
                c.setFillColorRGB(1, 1, 1)
                c.setFont("Helvetica-Bold", font_size + 4)
                c.drawString(82 + indent, current_y, title)
                current_y -= line_height * 2.5
            else:
                c.setFillColorRGB(*section_color)
                c.rect(72, current_y - 5, width - 144, 25, fill=True)
                c.setFillColorRGB(0, 0, 0)
                c.setFont("Helvetica-Bold", font_size)
                c.drawString(82 + indent, current_y, title)
                current_y -= line_height * 2
            
            if content:
                c.setFont("Helvetica", 12)
                
                # Calculate available width for text
                available_width = width - 144 - (2 * indent)
                
                # Split content into lines and wrap text
                wrapped_lines = []
                for line in content.split('\n'):
                    if not line.strip():
                        wrapped_lines.append('')
                        continue
                        
                    words = line.split()
                    current_line = []
                    current_width = 0
                    
                    for word in words:
                        word_width = c.stringWidth(word, "Helvetica", 12)
                        space_width = c.stringWidth(" ", "Helvetica", 12)
                        
                        if current_width + word_width + space_width <= available_width:
                            current_line.append(word)
                            current_width += word_width + space_width
                        else:
                            if current_line:
                                wrapped_lines.append(' '.join(current_line))
                            current_line = [word]
                            current_width = word_width + space_width
                    
                    if current_line:
                        wrapped_lines.append(' '.join(current_line))
                
                # Calculate total height needed
                total_height = len(wrapped_lines) * line_height
                
                # Check if content needs a new page
                if current_y - total_height < 72:
                    c.showPage()
                    c.setPageSize((width, height))
                    current_y = add_header()
                    c.setFont("Helvetica", 12)
                
                # Draw background for content
                c.setFillColorRGB(0.95, 0.97, 1.0)
                c.rect(72 + indent, current_y - total_height + 5, 
                       width - 144 - indent, total_height + 10, fill=True)
                
                # Draw text
                c.setFillColorRGB(0, 0, 0)
                for line in wrapped_lines:
                    if line:  # Only draw non-empty lines
                        c.drawString(82 + indent, current_y, line)
                    current_y -= line_height
                
            current_y -= line_height * 1.5

        def add_image(image_path, max_width=800):
            nonlocal current_y
            try:
                # Load the image
                img = ImageReader(image_path)
                img_width, img_height = img.getSize()
                
                # Calculate scaled dimensions
                aspect = img_height / float(img_width)
                usable_width = width - 144
                
                if img_width / img_height > 2:  # Ultrawide image
                    max_width = usable_width
                
                if img_width > max_width:
                    img_width = max_width
                    img_height = max_width * aspect
                
                # Check if we need a new page
                if current_y - img_height < 100:
                    c.showPage()
                    c.setPageSize((width, height))
                    current_y = add_header()  # Add header to new page
                
                # Add a border and shadow effect
                x_pos = (width - img_width) / 2
                # Draw shadow
                c.setFillColorRGB(0.8, 0.8, 0.8)
                c.rect(x_pos + 3, current_y - img_height - 3, img_width, img_height, fill=True)
                # Draw white background
                c.setFillColorRGB(1, 1, 1)
                c.rect(x_pos, current_y - img_height, img_width, img_height, fill=True)
                # Draw image
                c.drawImage(image_path, x_pos, current_y - img_height, 
                           width=img_width, height=img_height,
                           preserveAspectRatio=True)
                # Draw border
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.rect(x_pos, current_y - img_height, img_width, img_height, fill=False)
                
                current_y -= (img_height + 40)  # More padding between images
                
            except Exception as e:
                print_debug(f"Error adding image {image_path}: {str(e)}")

        # Start with header
        current_y = add_header()

        # Add Daily Goal Section
        add_section("DAILY PROCESS GOAL", "", 16, section_color=(0.2, 0.6, 0.8), is_main_header=True)
        
        try:
            # Get goal entries directly from the goal_entries dictionary
            goal_details = ""
            
            # Process Text widgets
            if goal_entries["Process"].get("1.0", tk.END).strip():
                goal_details += f"Specific Process Goal:\n{goal_entries['Process'].get('1.0', tk.END).strip()}\n\n"
            
            # Process Entry widgets
            for key in ["Lead", "Lag", "Commitment", "Obstacle", "Solution"]:
                if goal_entries[key].get().strip():
                    goal_details += f"{key}:\n{goal_entries[key].get().strip()}\n\n"
            
            # Process Review Text widget
            if goal_entries["Review"].get("1.0", tk.END).strip():
                goal_details += f"End of Day Review:\n{goal_entries['Review'].get('1.0', tk.END).strip()}"
            
            if goal_details:
                add_section("Daily Goals and Review", goal_details, 14, section_color=(0.85, 0.9, 0.95))
            
        except Exception as e:
            print_debug(f"Error adding goal details: {str(e)}")
            traceback.print_exc()  # Add this for more detailed error information

        # Add Time Segments section
        add_section("TIME SEGMENTS REVIEW", "", 16, section_color=(0.2, 0.6, 0.8), is_main_header=True)
        
        print_debug("Processing time segments...")
        
        for segment_name, widget_data in segment_widgets.items():
            try:
                print_debug(f"Processing segment: {segment_name}")
                
                # Initialize content for this segment
                segment_content = []
                
                # Get grades
                grades_content = []
                for category, combo in zip(widget_data["categories"], widget_data["grade_combos"]):
                    grade = combo.get()
                    if grade:
                        grades_content.append(f"{category}: {grade}")
                        print_debug(f"Found grade for {category}: {grade}")
                
                if grades_content:
                    segment_content.append("Grades:")
                    segment_content.extend(grades_content)
                
                # Get comments
                comment = widget_data["comment_box"].get("1.0", tk.END).strip()
                if comment:
                    segment_content.append("\nComments:")
                    segment_content.append(comment)
                    print_debug(f"Found comment: {comment[:50]}...")
                
                # Combine all content
                final_content = "\n".join(segment_content)
                
                if final_content.strip():
                    print_debug(f"Adding section for {segment_name}")
                    add_section(segment_name, final_content, 14, section_color=(0.85, 0.9, 0.95))
                else:
                    print_debug(f"No content found for {segment_name}")
                    
            except Exception as e:
                print_debug(f"Error processing segment {segment_name}: {str(e)}")
                traceback.print_exc()

        # Pre-market Prep Section
        add_section("PRE-MARKET PREPARATION", "", 16, section_color=(0.2, 0.6, 0.8), is_main_header=True)
        
        try:
            # Market Overview with light blue background
            market_text = market_overview.get("1.0", tk.END).strip()
            add_section("Market Overview", market_text, 14, section_color=(0.8, 0.9, 1.0))
            
            # Earnings Movers with different blue shade
            earnings_content = earnings_text.get("1.0", tk.END).strip()
            add_section("Earnings Movers", earnings_content, 14, section_color=(0.7, 0.85, 1.0))
            
            # Day 2 Movers
            day2_content = day2_text.get("1.0", tk.END).strip()
            add_section("Day 2 Movers", day2_content, 14)
            
            # Top 2 to Watch
            top_content = f"""
            1. {top1_entry.get().strip()}
            Reason: {reason1_entry.get().strip()}
            
            2. {top2_entry.get().strip()}
            Reason: {reason2_entry.get().strip()}
            """
            add_section("Top 2 to Watch", top_content, 14)
            
        except Exception as e:
            print_debug(f"Error in Pre-market section: {str(e)}")
            traceback.print_exc()

        # Daily Overview Section
        try:
            daily_text = daily_overview_text.get("1.0", tk.END).strip()
            if daily_text:
                add_section("Daily Overview", daily_text, 14, section_color=(0.85, 0.9, 0.95))
        except Exception as e:
            print_debug(f"Error in Daily Overview section: {str(e)}")
            traceback.print_exc()

        try:
            easy_trades_content = easy_trades_text.get("1.0", tk.END).strip()
            if easy_trades_content:
                add_section("Easy $$ Trades", easy_trades_content, 14, section_color=(0.85, 0.9, 0.95))
        except Exception as e:
            print_debug(f"Error in Easy $$ Trades section: {str(e)}")
            traceback.print_exc()

        try:
            # Trades
            trades_text = drc_trades_text.get("1.0", tk.END).strip()
            if trades_text:
                add_section("Trades Taken", trades_text, 14)
            
            # Emotional Log
            emotional_text = emotional_log_text.get("1.0", tk.END).strip()
            if emotional_text:
                add_section("Mistake Tally", emotional_text, 14)
            
        except Exception as e:
            print_debug(f"Error in DRC section: {str(e)}")
            traceback.print_exc()

        # Add Trading Charts section
        print_debug("Adding Trading Charts")
        add_section("Trading Charts", "", 14)
        
        try:
            # Get all images from the chart_images list
            if hasattr(drc_trades_text, 'chart_images'):
                for image_path in drc_trades_text.chart_images:
                    add_image(image_path)
        except Exception as e:
            print_debug(f"Error processing chart images: {str(e)}")

        # Save and open
        c.save()
        
        messagebox.showinfo("Export Successful", f"DRC data exported to {file_path}")
        
        if messagebox.askyesno("Open Report", "Would you like to open the exported report?"):
            import os
            os.startfile(file_path)
            
    except Exception as e:
        print(f"Export error: {str(e)}")
        traceback.print_exc()
        
def add_earnings_mover(ticker, eps_percentage, rev_percentage, guidance, catalyst, 
                       gap_range, notes, short_int, inst_owner, text_widget):
    mover = f"{ticker.get()} | EPS: {eps_percentage.get()} | Rev: {rev_percentage.get()} | " \
            f"Guidance: {guidance.get()} | Catalyst: {catalyst.get()} | " \
            f"Gap outside range: {gap_range.get()} | Short int: {short_int.get()}% | " \
            f"Inst owner: {inst_owner.get()}% | Notes: {notes.get()}\n"
    
    text_widget.insert(tk.END, mover)
    
    # Clear all input fields after adding
    for entry in [ticker, guidance, notes, eps_estimate_entry, eps_actual_entry, 
                  rev_estimate_entry, rev_actual_entry, short_int, inst_owner]:
        entry.delete(0, tk.END)
    catalyst.set(0)
    gap_range.set("No")
    eps_percentage_var.set("")
    rev_percentage_var.set("")

def calculate_percentage(actual, estimate):
    if estimate == 0:
        return "N/A"  # Avoid division by zero
    return f"{((actual - estimate) / abs(estimate)) * 100:.2f}%"

def update_percentages():
    global eps_estimate_entry, eps_actual_entry, rev_estimate_entry, rev_actual_entry, eps_percentage_var, rev_percentage_var
    try:
        eps_estimate = float(eps_estimate_entry.get())
        eps_actual = float(eps_actual_entry.get())
        rev_estimate = float(rev_estimate_entry.get())
        rev_actual = float(rev_actual_entry.get())

        eps_beat_miss = calculate_percentage(eps_actual, eps_estimate)
        rev_beat_miss = calculate_percentage(rev_actual, rev_estimate)

        eps_percentage_var.set(eps_beat_miss)
        rev_percentage_var.set(rev_beat_miss)
    except ValueError:
        eps_percentage_var.set("N/A")
        rev_percentage_var.set("N/A")

# Call the function to create the pre-market prep content
content_frame, market_overview, earnings_text, day2_text, top1_entry, top2_entry, reason1_entry, reason2_entry, strategy_entries = create_premarket_content(premarket_tab)

# First, define the variables at the top level (after your imports)
emotion_var = None
guidance_text = None

# Then define the function that will use these variables
def show_psych_guidance(event=None):
    global emotion_var, guidance_text
    selected_emotion = emotion_var.get()
    if selected_emotion in PSYCHOLOGICAL_GUIDANCE:
        guidance_text.delete('1.0', tk.END)
        guidance_text.insert('1.0', PSYCHOLOGICAL_GUIDANCE[selected_emotion])
        
        # Add color coding based on emotion category
        if selected_emotion in ["FOMO", "Revenge Trading", "Frustrated"]:
            guidance_text.configure(fg="red")
        elif selected_emotion in ["Overconfident", "Impulsive", "Excited/Euphoric"]:
            guidance_text.configure(fg="orange")
        elif selected_emotion == "Calm & Focused":
            guidance_text.configure(fg="green")
        else:
            guidance_text.configure(fg="black")

# First, define the reset process function (place this before create_emotion_check_frame)
def emotional_reset_process():
    reset_steps = [
        "1. Physical Reset (30 seconds):\n"
        "- Take 3 deep breaths (4 counts in, 6 counts out)\n"
        "- Roll shoulders back\n"
        "- Unclench your jaw and relax your hands\n",
        
        "2. Mental Reset (45 seconds):\n"
        "- Look away from your charts\n"
        "- Remind yourself: 'My stop is my risk manager'\n"
        "- Say: 'Let winners run, that's how I make money'\n",
        
        "3. Trade Review (45 seconds):\n"
        "- Check your original trade thesis\n"
        "- Confirm your technical stop level\n"
        "- Review your profit target(s)\n",
        
        "4. Return Protocol (60 seconds):\n"
        "- Is price action invalid? Y/N\n"
        "- Are you at your stop? Y/N\n"
        "- If both NO, your fear is not based on price action\n"
        "- HOLD YOUR POSITION - Let your stop do its job!"
    ]
    
    # Create a new window for the reset process
    reset_window = tk.Toplevel()
    reset_window.title("In-Trade Reset Process")
    reset_window.geometry("400x500")
    reset_window.transient(root)  # Make it float on top of main window
    
    # Center the window on the screen
    window_width = 400
    window_height = 500
    screen_width = reset_window.winfo_screenwidth()
    screen_height = reset_window.winfo_screenheight()
    
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    reset_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    # Add a header
    header = ttk.Label(reset_window, 
                      text="Quick Reset Process (3 minutes total)", 
                      font=('Arial', 12, 'bold'))
    header.pack(pady=10)
    
    # Add a warning/reminder
    warning = ttk.Label(reset_window,
                       text="Remember: Fear of loss often leads to cutting winners short.\nYour stop loss is your risk manager - trust it!",
                       foreground="red",
                       justify="center",
                       wraplength=350)
    warning.pack(pady=(0,10))
    
    # Create a frame for the steps
    steps_frame = ttk.Frame(reset_window)
    steps_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Add each step with a checkbox
    checkboxes = []
    for step in reset_steps:
        frame = ttk.Frame(steps_frame)
        frame.pack(fill=tk.X, pady=5)
        
        var = tk.BooleanVar()
        cb = ttk.Checkbutton(frame, variable=var)
        cb.pack(side=tk.LEFT, padx=(0,5))
        
        label = ttk.Label(frame, text=step, wraplength=350)
        label.pack(side=tk.LEFT, fill=tk.X)
        
        checkboxes.append(var)
    
    # Add a completion button
    def check_completion():
        if all(cb.get() for cb in checkboxes):
            emotion_var.set("Calm & Focused")
            reset_window.destroy()
            messagebox.showinfo("Reset Complete", 
                              "Reset complete. Trust your stop loss.\nLet your winners run - that's how you make money.")
        else:
            messagebox.showwarning("Incomplete Reset", 
                                 "Please complete all steps of the reset process.")
    
    ttk.Button(reset_window, 
               text="Complete Reset", 
               command=check_completion).pack(pady=20)

# Then define the create_emotion_check_frame function
def create_emotion_check_frame(parent):
    mistake_frame = tk.LabelFrame(parent, text="Mistake Logger", pady=10, padx=10, relief=tk.RIDGE, borderwidth=2)
    mistake_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    # Create large, attention-grabbing button
    mistake_button = ttk.Button(
        mistake_frame,
        text="I Made a Mistake!",
        command=log_mistake,
        style="Mistake.TButton"
    )
    mistake_button.pack(fill=tk.X, pady=10, padx=20)

    # Create custom style for the button
    style = ttk.Style()
    style.configure(
        "Mistake.TButton",
        font=('Arial', 12, 'bold'),
        padding=10
    )

    return mistake_frame

def log_mistake():
    # Create a new window for the mistake logging process
    log_window = tk.Toplevel()
    log_window.title("Mistake Logger")
    log_window.geometry("500x600")
    log_window.transient(root)  # Make it float on top of main window
    
    # Center the window
    window_width = 500
    window_height = 600
    screen_width = log_window.winfo_screenwidth()
    screen_height = log_window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    log_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Create a frame with padding
    main_frame = ttk.Frame(log_window, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Step 1: Emotional State
    ttk.Label(main_frame, text="1. What emotion led to this mistake?", font=('Arial', 10, 'bold')).pack(anchor='w')
    emotions = [
        "Fear of Loss",
        "Fear of Missing Profit",
        "Fear of Being Wrong",
        "Anxious about Position Size",
        "FOMO",
        "Revenge Trading",
        "Frustrated",
        "Overconfident",
        "Impulsive",
        "Hesitant/Frozen",
        "Excited/Euphoric"
    ]
    emotion_var = tk.StringVar()
    emotion_combo = ttk.Combobox(main_frame, values=emotions, textvariable=emotion_var, state="readonly")
    emotion_combo.pack(fill=tk.X, pady=(0, 15))

    # Step 2: Mistake Type
    ttk.Label(main_frame, text="2. What type of mistake was it?", font=('Arial', 10, 'bold')).pack(anchor='w')
    mistake_types = [
        "Entered too early",
        "Entered too late",
        "Position size too large",
        "Position size too small",
        "Moved stop loss",
        "Exited too early",
        "Exited too late",
        "Broke trading rules",
        "Other"
    ]
    mistake_var = tk.StringVar()
    mistake_combo = ttk.Combobox(main_frame, values=mistake_types, textvariable=mistake_var, state="readonly")
    mistake_combo.pack(fill=tk.X, pady=(0, 15))

    # Step 3: Description
    ttk.Label(main_frame, text="3. Briefly describe what happened:", font=('Arial', 10, 'bold')).pack(anchor='w')
    description_text = tk.Text(main_frame, height=4, wrap=tk.WORD)
    description_text.pack(fill=tk.X, pady=(0, 15))

    # Step 4: Prevention
    ttk.Label(main_frame, text="4. How will you prevent this in the future?", font=('Arial', 10, 'bold')).pack(anchor='w')
    prevention_text = tk.Text(main_frame, height=4, wrap=tk.WORD)
    prevention_text.pack(fill=tk.X, pady=(0, 15))

    def save_mistake():
        if not all([emotion_var.get(), mistake_var.get(), 
                   description_text.get("1.0", tk.END).strip(),
                   prevention_text.get("1.0", tk.END).strip()]):
            messagebox.showwarning("Incomplete", "Please fill out all fields")
            return

        # Format the mistake log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        mistake_entry = (
            f"Time: {timestamp}\n"
            f"Emotion: {emotion_var.get()}\n"
            f"Mistake Type: {mistake_var.get()}\n"
            f"Description: {description_text.get('1.0', tk.END).strip()}\n"
            f"Prevention Plan: {prevention_text.get('1.0', tk.END).strip()}\n"
            f"{'='*50}\n"
        )

        # Add to both the output and emotional log
        output_text.insert("1.0", mistake_entry + "\n")
        emotional_log_text.insert("1.0", mistake_entry + "\n")
        
        # Show confirmation and close window
        messagebox.showinfo("Logged", "Mistake logged successfully!\nRemember: Every mistake is a learning opportunity.")
        log_window.destroy()

    # Add Save button
    ttk.Button(main_frame, text="Save Mistake Log", command=save_mistake).pack(pady=20)

# Then in your main UI setup code (where you're creating the setup_frame), replace the emotion check frame creation with:
setup_frame = tk.Frame(main_screen_tab, width=250)
setup_frame.pack(side=tk.LEFT, fill=tk.Y)
setup_frame.pack_propagate(False)

# Create but don't display the listbox (keep it for dependency purposes)
global setup_list
listbox_frame = tk.Frame(setup_frame)
scrollbar = tk.Scrollbar(listbox_frame)
setup_list = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, width=40)
scrollbar.config(command=setup_list.yview)

# Create the emotion check frame
create_emotion_check_frame(setup_frame)

# Add General Notes after Emotion Check
notes_label = tk.Label(setup_frame, text="General notes and reminders")
notes_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5,0))

# Create a frame to hold the Text widget and scrollbar
notes_frame = tk.Frame(setup_frame)
notes_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

general_notes = tk.Text(notes_frame, wrap=tk.WORD, height=10)
general_notes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add scrollbar for the general notes
notes_scrollbar = tk.Scrollbar(notes_frame)
notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
notes_scrollbar.config(command=general_notes.yview)
general_notes.config(yscrollcommand=notes_scrollbar.set)

# EV Calculator frame below listbox
calculator_frame = tk.LabelFrame(setup_frame, text="EV Calculator", pady=10, padx=10, relief=tk.RIDGE, borderwidth=2)
calculator_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Configure the columns to allow expansion
calculator_frame.columnconfigure(1, weight=1)

tk.Label(calculator_frame, text="Daily Risk ($):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
entry_daily_risk = tk.Entry(calculator_frame)
entry_daily_risk.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10), pady=5)

tk.Label(calculator_frame, text="Reward:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
entry_reward = tk.Entry(calculator_frame)
entry_reward.grid(row=1, column=1, sticky=tk.EW, padx=(0, 10), pady=5)

tk.Label(calculator_frame, text="Risk (in $):").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
entry_risk = tk.Entry(calculator_frame)
entry_risk.grid(row=2, column=1, sticky=tk.EW, padx=(0, 10), pady=5)

tk.Label(calculator_frame, text="Probability (%):").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
entry_probability = tk.Entry(calculator_frame)
entry_probability.grid(row=3, column=1, sticky=tk.EW, padx=(0, 10), pady=5)

# Buttons frame
button_frame = tk.Frame(calculator_frame)
button_frame.grid(row=4, column=0, columnspan=2, pady=10)

calc_button = tk.Button(button_frame, text="Calculate EV & R/R", command=calculate_ev)
calc_button.pack(side=tk.LEFT, padx=5)
clear_button = tk.Button(button_frame, text="Clear", command=clear_ev_inputs)
clear_button.pack(side=tk.LEFT, padx=5)

# Results frame
results_frame = tk.Frame(calculator_frame)
results_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

result_label = tk.Label(results_frame, text="Expected Value (EV):", anchor="w")
result_label.pack(fill=tk.X, padx=10, pady=2)

rr_label = tk.Label(results_frame, text="Risk/Reward (R/R):", anchor="w")
rr_label.pack(fill=tk.X, padx=10, pady=2)

allocation_label = tk.Label(results_frame, text="Risk Allocation:", anchor="w")
allocation_label.pack(fill=tk.X, padx=10, pady=2)

trade_label = tk.Label(results_frame, text="", anchor="w")
trade_label.pack(fill=tk.X, padx=10, pady=2)

# Gamification frame below the trade details
gamification_frame = tk.LabelFrame(setup_frame, text="Daily Performance Tracker", pady=10, padx=10, relief=tk.RIDGE, borderwidth=2)
gamification_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)


# Grade label
grade_label = tk.Label(gamification_frame, text="Grades: A: 0, B: 0, F: 0")
grade_label.pack(anchor='w')

# Output for reviewing trades
trades_label = tk.Label(main_screen_tab, text="Trades taken")
trades_label.pack_forget()

# Approach 2: Create a custom font
custom_font = tkfont.Font(size=9)
output_text = tk.Text(main_screen_tab, wrap=tk.WORD, width=70, height=10, font=custom_font)
output_text.pack_forget()

# Frame for notes and rules
notes_rules_frame = tk.Frame(main_screen_tab)
notes_rules_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(0, 10))

# First, define the create_note_section function
def create_note_section(parent, title, height=4):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    label = tk.Label(frame, text=title)
    label.pack(anchor=tk.W)
    
    # Create Text widget with its own scrollbar
    text_frame = tk.Frame(frame)
    text_frame.pack(fill=tk.X)
    
    text_widget = tk.Text(text_frame, height=height, wrap=tk.WORD, font=custom_font)
    scrollbar = tk.Scrollbar(text_frame)
    
    text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_widget.yview)
    
    return text_widget

# Keep note_box but hide it
note_box = tk.Text(notes_rules_frame)
note_box.pack_forget() 
 # Create but don't display
rules_frame = tk.Frame(notes_rules_frame)
rules_frame.pack(fill=tk.BOTH, expand=True)

# Add these functions before create_drc_content
def add_chart_to_drc():
    global drc_trades_text, chart_preview_frame
    
    # Allow user to select multiple image files
    file_paths = filedialog.askopenfilenames(
        title="Select Chart Images",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
    )
    
    if file_paths:
        # Initialize chart_images list if it doesn't exist
        if not hasattr(drc_trades_text, 'chart_images'):
            drc_trades_text.chart_images = []
        
        for file_path in file_paths:
            try:
                # Store the image path
                drc_trades_text.chart_images.append(file_path)
                # Update the preview (removed the text insertion)
                update_chart_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add chart {file_path}: {str(e)}")

def remove_chart(index):
    if hasattr(drc_trades_text, 'chart_images'):
        if 0 <= index < len(drc_trades_text.chart_images):
            drc_trades_text.chart_images.pop(index)
            update_chart_preview()

def update_chart_preview():
    # Find the preview container inside the canvas
    preview_container = None
    for widget in chart_preview_frame.winfo_children():
        if isinstance(widget, tk.Canvas):
            preview_container = widget.winfo_children()[0]
            break
    
    if not preview_container:
        return
        
    # Clear existing previews
    for widget in preview_container.winfo_children():
        widget.destroy()
    
    # Add new previews
    if hasattr(drc_trades_text, 'chart_images'):
        for idx, img_path in enumerate(drc_trades_text.chart_images):
            frame = ttk.Frame(preview_container)
            frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Show filename
            name = os.path.basename(img_path)
            ttk.Label(frame, text=f"{name[:20]}...").pack()
            
            # Add remove button
            ttk.Button(
                frame,
                text="Remove",
                command=lambda x=idx: remove_chart(x)
            ).pack()
update_streak_counter()

def clear_drc():
    # Clear all time segments
    for segment_name, segment_data in segment_widgets.items():
        # Clear grade combos
        for combo in segment_data["grade_combos"]:
            combo.set("")
        # Clear comment box
        segment_data["comment_box"].delete('1.0', tk.END)
    
    # Clear Daily Overview
    daily_overview_text.delete('1.0', tk.END)
    
    # Clear Easy $$ trades
    easy_trades_text.delete('1.0', tk.END)
    
    # Clear goal entries
    for key in ['Process', 'Review']:
        if key in goal_entries and goal_entries[key]:
            goal_entries[key].delete('1.0', tk.END)
    
    for key in ['Lead', 'Lag', 'Commitment', 'Obstacle', 'Solution']:
        if key in goal_entries and goal_entries[key]:
            goal_entries[key].delete(0, tk.END)
    
    # Clear trades taken
    drc_trades_text.delete('1.0', tk.END)
    
    # Clear emotional log
    emotional_log_text.delete('1.0', tk.END)
    
    # Clear chart images if they exist
    if hasattr(drc_trades_text, 'chart_images'):
        drc_trades_text.chart_images = []
        update_chart_preview()
    
    messagebox.showinfo("Clear", "DRC tab cleared successfully!")

def create_time_segment(parent_frame, segment_name, categories, row):
    """Helper function to create a single time segment frame"""
    frame = ttk.Frame(parent_frame, padding="10")
    frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
    
    # Segment label
    ttk.Label(frame, text=segment_name, width=20).grid(row=0, column=0, sticky="w")
    
    # Grade selection frame
    grade_frame = ttk.Frame(frame)
    grade_frame.grid(row=1, column=0, sticky="ew", pady=(5,10))
    
    # Store comboboxes in a list for easier access
    grade_combos = []
    
    # Create grade selection combos
    for i, category in enumerate(categories):
        ttk.Label(grade_frame, text=category).grid(row=0, column=i, padx=5)
        combo = ttk.Combobox(grade_frame, values=["A", "B", "F"], width=5, state="readonly")
        combo.set("")
        combo.grid(row=1, column=i, padx=5)
        grade_combos.append(combo)
    
    # Comment section
    ttk.Label(frame, 
             text="What did I do well, what did I not do well, and where does my focus on improvement need to be?",
             wraplength=500).grid(row=2, column=0, sticky="w", pady=(5,0))
    
    comment_box = tk.Text(frame, height=5, width=70, wrap=tk.WORD)
    comment_box.grid(row=3, column=0, sticky="ew", pady=(5,10))
    
    return {
        "frame": frame,
        "grade_combos": grade_combos,
        "comment_box": comment_box,
        "categories": categories
    }

def create_drc_content(parent):
    global segment_widgets, daily_overview_text, easy_trades_text, drc_trades_text, emotional_log_text, chart_preview_frame
    
    # Create a canvas with a scrollbar
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    current_row = 0

    # Add goal setting frame at the top
    goal_frame = create_goal_setting_frame(scrollable_frame)
    goal_frame.grid(row=current_row, column=0, sticky="ew", padx=10, pady=5)
    current_row += 1

    # Create time segments
    segment_widgets = {}  # Dictionary to store all segment widgets
    
    for segment in SEGMENTS:
        categories = PREMARKET_CATEGORIES if segment == "Pre-market prep" else REGULAR_CATEGORIES
        segment_widgets[segment] = create_time_segment(scrollable_frame, segment, categories, current_row)
        current_row += 1

    # Add Daily Overview and Easy $$ trades comment boxes
    overview_frame = ttk.Frame(scrollable_frame, padding="10")
    overview_frame.grid(row=current_row, column=0, sticky="ew", padx=10, pady=5)
    current_row += 1

    ttk.Label(overview_frame, text="Daily Overview:").grid(row=0, column=0, sticky="w", pady=(5,0))
    daily_overview_text = tk.Text(overview_frame, height=5, width=70, wrap=tk.WORD)
    daily_overview_text.grid(row=1, column=0, sticky="ew", pady=(0,5))

    ttk.Label(overview_frame, text="Easy $$ trades:").grid(row=2, column=0, sticky="w", pady=(5,0))
    easy_trades_text = tk.Text(overview_frame, height=5, width=70, wrap=tk.WORD)
    easy_trades_text.grid(row=3, column=0, sticky="ew", pady=(0,5))

    # Add Trades Taken text box
    trades_frame = ttk.Frame(scrollable_frame)
    trades_frame.grid(row=current_row, column=0, sticky="ew", padx=10, pady=5)
    current_row += 1
    
    ttk.Label(trades_frame, text="Trades Taken:").grid(row=0, column=0, sticky="w")
    drc_trades_text = tk.Text(trades_frame, height=5, width=70, wrap=tk.WORD, font=custom_font)
    drc_trades_text.grid(row=1, column=0, sticky="ew")
    trades_scrollbar = ttk.Scrollbar(trades_frame, orient="vertical", command=drc_trades_text.yview)
    trades_scrollbar.grid(row=1, column=1, sticky="ns")
    drc_trades_text.configure(yscrollcommand=trades_scrollbar.set)

    # Add Emotional Log text box
    emotional_log_frame = ttk.Frame(scrollable_frame)
    emotional_log_frame.grid(row=current_row, column=0, sticky="ew", padx=10, pady=5)
    current_row += 1
    
    ttk.Label(emotional_log_frame, text="Mistake Tracker:").grid(row=0, column=0, sticky="w")
    emotional_log_text = tk.Text(emotional_log_frame, height=5, width=70, wrap=tk.WORD)
    emotional_log_text.grid(row=1, column=0, sticky="ew")
    emotional_log_scrollbar = ttk.Scrollbar(emotional_log_frame, orient="vertical", command=emotional_log_text.yview)
    emotional_log_scrollbar.grid(row=1, column=1, sticky="ns")
    emotional_log_text.configure(yscrollcommand=emotional_log_scrollbar.set)

    # Add Chart Preview section
    chart_frame = ttk.Frame(scrollable_frame)
    chart_frame.grid(row=current_row, column=0, sticky="ew", padx=10, pady=5)
    current_row += 1
    
    ttk.Label(chart_frame, text="Charts:").grid(row=0, column=0, sticky="w")
    chart_preview_frame = ttk.Frame(chart_frame)
    chart_preview_frame.grid(row=1, column=0, sticky="ew")
    
    ttk.Button(chart_preview_frame, text="Add Chart", command=add_chart_to_drc).grid(row=0, column=0, padx=5)
    
    preview_canvas = tk.Canvas(chart_preview_frame, height=100)
    preview_canvas.grid(row=0, column=1, sticky="ew", padx=5)
    
    preview_container = ttk.Frame(preview_canvas)
    preview_canvas.create_window((0,0), window=preview_container, anchor="nw")

    # Add Export and Clear buttons
    button_frame = ttk.Frame(scrollable_frame)
    button_frame.grid(row=current_row, column=0, pady=10)

    export_button = ttk.Button(button_frame, text="Export DRC", command=export_drc_data)
    export_button.grid(row=0, column=0, padx=5)

    clear_button = ttk.Button(button_frame, text="Clear DRC", command=clear_drc)
    clear_button.grid(row=0, column=1, padx=5)

    # Configure grid weights
    scrollable_frame.columnconfigure(0, weight=1)

    # Grid the canvas and scrollbar
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    # Configure parent grid weights
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)

    return scrollable_frame

# Create the DRC content
drc_content_frame = create_drc_content(drc_tab)

def show_reminder(segment):
    messagebox.showinfo("DRC Reminder", f"Time to fill out the {segment} section!")

def check_time():
    eastern = pytz.timezone('US/Eastern')
    
    while True:
        # Get current time in user's local timezone
        local_time = datetime.now()
        
        # Convert to Eastern time
        eastern_time = datetime.now(pytz.timezone('US/Eastern')).time()
        
        # Define check times in Eastern
        check_times = [
            (dt_time(9, 25), dt_time(9, 26), "Pre-market prep"),
            (dt_time(10, 0), dt_time(10, 1), "9:30 - 10:00"),
            (dt_time(11, 30), dt_time(11, 31), "10:00 - 11:30"),
            (dt_time(14, 0), dt_time(14, 1), "11:30 - 2:00"),
            (dt_time(16, 0), dt_time(16, 1), "Afterhours")
        ]
        
        # Check each time window
        for start_time, end_time, segment in check_times:
            if start_time <= eastern_time < end_time:
                root.after(0, show_reminder, segment)
                break
        
        time.sleep(60)  # Check every 60 seconds

# Start the time checking in a separate thread
time_thread = threading.Thread(target=check_time)
time_thread.daemon = True
time_thread.start()

def reduce_font_size(widget):
    current_font = widget.cget("font")
    if not current_font:
        current_font = tkfont.nametofont(widget.cget("font"))
    
    if isinstance(current_font, str):
        font = tkfont.nametofont(current_font)
    else:
        font = current_font
    
    family = font.cget("family")
    size = font.cget("size")
    weight = font.cget("weight")
    slant = font.cget("slant")
    
    new_size = size - 1 if size > 1 else 1
    new_font = tkfont.Font(family=family, size=new_size, weight=weight, slant=slant)
    
    widget.configure(font=new_font)

# After creating all widgets
reduce_font_size(output_text)
reduce_font_size(note_box)

# Force update
output_text.update()
note_box.update()

def load_setups():
    """Load setups from JSON file"""
    try:
        setup_file = DATA_DIR / "playbook_setups.json"
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading setups: {e}")
        return {}



def update_pattern_combo():
    """Update the pattern combo with current playbook setups"""
    global pattern_combo
    try:
        setups = load_setups()
        setup_names = list(setups.keys()) if setups else []
        if pattern_combo and hasattr(pattern_combo, 'configure'):
            pattern_combo['values'] = setup_names
            print(f"Updated pattern combo with {len(setup_names)} setups: {setup_names}")  # Debug print
    except Exception as e:
        print(f"Error updating pattern combo: {e}")
        traceback.print_exc()

# Add this function to save the application state
def save_app_state():
    """Save application state to file"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        
        # Helper function to safely get text from widgets
        def safe_get_text(widget, default=""):
            try:
                if widget and widget.winfo_exists():
                    return widget.get("1.0", tk.END)
                return default
            except Exception:
                return default

        # Helper function to safely get entry value
        def safe_get_entry(widget, default=""):
            try:
                if widget and widget.winfo_exists():
                    return widget.get()
                return default
            except Exception:
                return default
        
        state = {
            "trades": trades,
            "notes": safe_get_text(note_box),
            "output": safe_get_text(output_text),
            "pattern": safe_get_entry(pattern_combo),
            
            # Pre-market prep tab data
            "premarket": {
                "market_overview": safe_get_text(market_overview),
                "earnings_text": safe_get_text(earnings_text),
                "day2_text": safe_get_text(day2_text),
                "top1": safe_get_entry(top1_entry),
                "top2": safe_get_entry(top2_entry),
                "reason1": safe_get_entry(reason1_entry),
                "reason2": safe_get_entry(reason2_entry),
                "strategies": {
                    strategy: {
                        "entry1": safe_get_text(entries[0]),
                        "entry2": safe_get_text(entries[1])
                    }
                    for strategy, entries in strategy_entries.items()
                }
            },
            
            # DRC tab data
            "drc": {
                "daily_overview": safe_get_text(daily_overview_text),
                "easy_trades": safe_get_text(easy_trades_text),
                "drc_trades": safe_get_text(drc_trades_text),
                "emotional_log": safe_get_text(emotional_log_text),
                "chart_images": getattr(drc_trades_text, 'chart_images', []),
                
                # Time segments data
                "segments": {
                    segment_name: {
                        "grades": [safe_get_entry(combo) for combo in segment_data["grade_combos"]],
                        "comment": safe_get_text(segment_data["comment_box"])
                    }
                    for segment_name, segment_data in segment_widgets.items()
                },
                
                # Goal entries
                "goal_entries": {
                    key: (safe_get_text(widget) if isinstance(widget, tk.Text) else safe_get_entry(widget))
                    for key, widget in goal_entries.items()
                    if widget is not None
                }
            }
        }
        
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=4)
            
    except Exception as e:
        print(f"Failed to save application state: {str(e)}")
        traceback.print_exc()

# Add this function to load the application state
def load_app_state():
    global trades
    
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                
                # Load main screen data
                trades = state.get("trades", [])
                
                # Load text widgets
                if "notes" in state:
                    note_box.delete("1.0", tk.END)
                    note_box.insert("1.0", state["notes"])
                
                if "output" in state:
                    output_text.delete("1.0", tk.END)
                    output_text.insert("1.0", state["output"])
                
                # Load pre-market prep data
                premarket_data = state.get("premarket", {})
                if premarket_data:
                    market_overview.delete("1.0", tk.END)
                    market_overview.insert("1.0", premarket_data.get("market_overview", ""))
                    
                    earnings_text.delete("1.0", tk.END)
                    earnings_text.insert("1.0", premarket_data.get("earnings_text", ""))
                    
                    day2_text.delete("1.0", tk.END)
                    day2_text.insert("1.0", premarket_data.get("day2_text", ""))
                    
                    top1_entry.delete(0, tk.END)
                    top1_entry.insert(0, premarket_data.get("top1", ""))
                    
                    top2_entry.delete(0, tk.END)
                    top2_entry.insert(0, premarket_data.get("top2", ""))
                    
                    reason1_entry.delete(0, tk.END)
                    reason1_entry.insert(0, premarket_data.get("reason1", ""))
                    
                    reason2_entry.delete(0, tk.END)
                    reason2_entry.insert(0, premarket_data.get("reason2", ""))
                    
                    # Load strategies
                    for strategy, data in premarket_data.get("strategies", {}).items():
                        if strategy in strategy_entries:
                            strategy_entries[strategy][0].delete("1.0", tk.END)
                            strategy_entries[strategy][0].insert("1.0", data.get("entry1", ""))
                            strategy_entries[strategy][1].delete("1.0", tk.END)
                            strategy_entries[strategy][1].insert("1.0", data.get("entry2", ""))
                
                # Load DRC data
                drc_data = state.get("drc", {})
                if drc_data:
                    # Load text widgets
                    daily_overview_text.delete("1.0", tk.END)
                    daily_overview_text.insert("1.0", drc_data.get("daily_overview", ""))
                    
                    easy_trades_text.delete("1.0", tk.END)
                    easy_trades_text.insert("1.0", drc_data.get("easy_trades", ""))
                    
                    drc_trades_text.delete("1.0", tk.END)
                    drc_trades_text.insert("1.0", drc_data.get("drc_trades", ""))
                    
                    emotional_log_text.delete("1.0", tk.END)
                    emotional_log_text.insert("1.0", drc_data.get("emotional_log", ""))
                    
                    # Load chart images
                    if "chart_images" in drc_data:
                        drc_trades_text.chart_images = drc_data["chart_images"]
                        update_chart_preview()
                    
                    # Load time segments
                    segments_data = drc_data.get("segments", {})
                    for segment_name, segment_data in segments_data.items():
                        if segment_name in segment_widgets:
                            # Load grades
                            for combo, grade in zip(segment_widgets[segment_name]["grade_combos"], 
                                                  segment_data.get("grades", [])):
                                combo.set(grade)
                            
                            # Load comment
                            comment_box = segment_widgets[segment_name]["comment_box"]
                            comment_box.delete("1.0", tk.END)
                            comment_box.insert("1.0", segment_data.get("comment", ""))
                    
                    # Load goal entries
                    goal_data = drc_data.get("goal_entries", {})
                    for key in ["Process", "Review"]:
                        if key in goal_data and goal_entries.get(key):
                            goal_entries[key].delete("1.0", tk.END)
                            goal_entries[key].insert("1.0", goal_data.get(key, ""))
                    
                    for key in ["Lead", "Lag", "Commitment", "Obstacle", "Solution"]:
                        if key in goal_data and goal_entries.get(key):
                            goal_entries[key].delete(0, tk.END)
                            goal_entries[key].insert(0, goal_data.get(key, ""))
                
                # Update pattern combo after loading state
                update_pattern_combo()
                
    except Exception as e:
        print(f"Failed to load application state: {str(e)}")
        traceback.print_exc()

# Add this near the end of the file, just before root.mainloop()
root.protocol("WM_DELETE_WINDOW", lambda: [save_app_state(), root.destroy()])

# Add this after creating all the UI elements, before root.mainloop()
load_app_state()

# Add this new function near the other clear functions
def clear_main_screen():
    # Clear calculator inputs
    clear_ev_inputs()
    
    # Clear trade details
    clear_all_inputs() # type: ignore
        
    # Clear output
    output_text.delete('1.0', tk.END)
    
    # Reset grade counts and streak
    global grade_counts, streak_counter
    grade_counts = {"A": 0, "B": 0, "F": 0}
    streak_counter = 0
    
    # Update UI elements
    update_grade_tally()
    update_streak_counter()
    
    messagebox.showinfo("Clear", "Main screen cleared successfully!")

# First, add this function before create_premarket_content function
def clear_premarket():
    # Clear market overview
    market_overview.delete('1.0', tk.END)
    
    # Clear earnings text
    earnings_text.delete('1.0', tk.END)
    
    # Clear day2 text
    day2_text.delete('1.0', tk.END)
    
    # Clear top 2 entries and reasons
    top1_entry.delete(0, tk.END)
    top2_entry.delete(0, tk.END)
    reason1_entry.delete(0, tk.END)
    reason2_entry.delete(0, tk.END)
    
    # Clear all strategy entries
    for _, (entry1, entry2) in strategy_entries.items():
        entry1.delete('1.0', tk.END)
        entry2.delete('1.0', tk.END)
    
    messagebox.showinfo("Clear", "Pre-market prep tab cleared successfully!")

# Then in create_premarket_content function, replace the save button section with:
button_frame = ttk.Frame(content_frame)
button_frame.pack(pady=20)

clear_premarket_button = ttk.Button(button_frame, text="Clear Pre-market", command=clear_premarket)
clear_premarket_button.pack(side="left", padx=5)

# First, define all the functions needed for the checkpoint
def submit_from_checkpoint():
    # Check if goal has been reviewed
    if not goal_rewrite.get("1.0", tk.END).strip():
        messagebox.showwarning("Goal Review Required", 
            "Please write your process goal before submitting a trade.")
        return
    
    # Check rules
    rules_followed = {
        "Stock in play": stock_in_play_var.get(),
        "Solid trade entry": solid_trade_entry_var.get(),
        "Followed exit strategy": followed_exit_strategy_var.get(),
        "Proper position size": proper_position_size_var.get()
    }
    
    score = sum(rules_followed.values())
    if score < len(rules_followed):
        if not messagebox.askyesno("Rules Warning",
            "Not all rules are being followed.\nThis trade will result in an F grade.\nDo you want to proceed?"):
            return
    
    # Get values from checkpoint
    ticker = ticker_entry.get()
    setup = pattern_combo.get()
    goal_review = goal_rewrite.get("1.0", tk.END).strip()
    ev = ev_expectations.get("1.0", tk.END).strip()  # Updated to use Text widget method
    thesis = thesis_text.get("1.0", tk.END).strip()
    reasons2sell = reasons_text.get("1.0", tk.END).strip()
    hard_stop = hard_stop_entry.get("1.0", tk.END).strip()
    soft_stop = soft_stop_entry.get("1.0", tk.END).strip()
    
    # Calculate grade
    grade = calculate_grade(score, len(rules_followed))
    
    # Format mistakes text
    mistakes = []
    if not rules_followed["Stock in play"]:
        mistakes.append("BAD STOCK CHOICE")
    if not rules_followed["Solid trade entry"]:
        mistakes.append("BAD ENTRY")
    if not rules_followed["Followed exit strategy"]:
        mistakes.append("DID NOT FOLLOW EXIT STRATEGY")
    
    mistake_text = f" | Mistake: {'; '.join(mistakes).upper()}" if mistakes else ""
    grade_text = f"{grade}{mistake_text}"
    
    # Create trade info with expanded details
    trade_info = {
        "Ticker": ticker,
        "Setup": setup,
        "Goal": goal_review,
        "EV": ev,
        "Thesis": thesis,
        "Reasons to Sell": reasons2sell,
        "Hard Stop": hard_stop,
        "Soft Stop": soft_stop,
        "Grade": grade_text,
        "Rules Followed": rules_followed
    }
    trades.append(trade_info)
    
    # Update output displays with expanded format
    trade_summary = (f"Ticker: {ticker} | Setup: {setup} | "
                    f"Goal: {goal_review} | "
                    f"EV: {ev} | "
                    f"Thesis: {thesis} | "
                    f"Reasons to Sell: {reasons2sell} | "
                    f"Hard Stop: {hard_stop} | "
                    f"Soft Stop: {soft_stop} | "
                    f"Grade: {grade_text}")
    
    output_text.insert("1.0", trade_summary + "\n\n")  # Added extra newline for readability
    drc_trades_text.insert("1.0", trade_summary + "\n\n")
    
    # Ensure the top of both text boxes is visible
    output_text.see("1.0")
    drc_trades_text.see("1.0")
    
    if mistakes:
        # Temporarily disable the topmost attribute
        root.attributes('-topmost', False)
        
        # Create a custom dialog for mistake analysis
        class CustomDialog(simpledialog.Dialog):
            def body(self, master):
                self.title("Mistake Analysis")
                tk.Label(master, text="Why did you make these mistakes, and what can you do in the next trade to correct them?").grid(row=0, pady=5)
                self.e1 = tk.Text(master, wrap=tk.WORD, width=50, height=5)
                self.e1.grid(row=1, pady=5)
                return self.e1

            def apply(self):
                self.result = self.e1.get("1.0", tk.END).strip()

        # Show the custom dialog
        dialog = CustomDialog(root)
        response = dialog.result
        
        # Re-enable the topmost attribute
        root.attributes('-topmost', True)
        
        if response:
            output_text.insert(tk.END, f"Correction Plan: {response}\n")
            output_text.see(tk.END)
    
    # Clear the checkpoint
    clear_checkpoint()
    messagebox.showinfo("Trade Submitted", "Trade details submitted successfully!")
    update_grade_tally()

def clear_checkpoint():
    # Clear all entries in the checkpoint
    ticker_entry.delete(0, tk.END)
    pattern_combo.set('')
    goal_rewrite.delete("1.0", tk.END)
    ev_expectations.delete("1.0", tk.END)  # Updated to use Text widget method
    thesis_text.delete("1.0", tk.END)
    reasons_text.delete("1.0", tk.END)
    hard_stop_entry.delete("1.0", tk.END)
    soft_stop_entry.delete("1.0", tk.END)


# Then update the create_impulse_control_frame function
def create_impulse_control_frame(notes_rules_frame):
    global ticker_entry, pattern_combo, confirmation_text, emotion_var
    global stock_in_play_var, solid_trade_entry_var, followed_exit_strategy_var, proper_position_size_var
    global goal_rewrite, thesis_text, reasons_text, hard_stop_entry, soft_stop_entry
    global ev_expectations

    # Clear any existing widgets in notes_rules_frame
    for widget in notes_rules_frame.winfo_children():
        widget.destroy()

    # Create outer frame without extra padding
    outer_frame = ttk.LabelFrame(notes_rules_frame, text="One Good Trade")
    outer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Create canvas and scrollbar
    canvas = tk.Canvas(outer_frame)
    scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    
    # Create the main content frame
    control_frame = ttk.Frame(canvas, padding="5")
    
    # Configure scrolling
    control_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    # Create the window in the canvas
    canvas_window = canvas.create_window(
        (0, 0),
        window=control_frame,
        anchor="nw",
        width=canvas.winfo_width()
    )

    # Update the window size when canvas size changes
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width - 5)
    
    canvas.bind('<Configure>', on_canvas_configure)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar first
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Add Ticker input
    ttk.Label(control_frame, text="Enter Ticker:").pack(anchor='w')
    ticker_entry = ttk.Entry(control_frame)
    ticker_entry.pack(fill=tk.X, pady=(0,10))
    
    # Pattern selection
    ttk.Label(control_frame, text="Select your trade pattern:").pack(anchor='w')
    pattern_combo = ttk.Combobox(control_frame, state="readonly")
    pattern_combo.pack(fill=tk.X, pady=(0,10))
    update_pattern_combo()  # Initial population of the combo

    # Goal review
    ttk.Label(control_frame, text="Write your process goal to reinforce your focus:").pack(anchor='w')
    goal_rewrite = tk.Text(control_frame, height=3, wrap=tk.WORD)
    goal_rewrite.pack(fill=tk.X, pady=(0,10))

    # EV expectations
    ttk.Label(control_frame, text="What is your initial EV expectations for this trade?:").pack(anchor='w')
    ev_expectations = tk.Text(control_frame, height=1, wrap=tk.WORD)
    ev_expectations.pack(fill=tk.X, pady=(0,10))
    
    # Stop loss fields
    ttk.Label(control_frame, text="Hard Stop (price level where you must exit):").pack(anchor='w')
    hard_stop_entry = tk.Text(control_frame, height=1, wrap=tk.WORD)
    hard_stop_entry.pack(fill=tk.X, pady=(0,10))
    
    ttk.Label(control_frame, text="Soft Stop (Decide after 10 minutes):").pack(anchor='w')
    soft_stop_entry = tk.Text(control_frame, height=1, wrap=tk.WORD)
    soft_stop_entry.pack(fill=tk.X, pady=(0,10))

    # Trade Thesis
    ttk.Label(control_frame, text="What's your complete trade thesis?").pack(anchor='w')
    thesis_text = tk.Text(control_frame, height=6, wrap=tk.WORD)
    thesis_text.pack(fill=tk.X, pady=(5,10))
    
    # Reasons to sell
    ttk.Label(control_frame, text="What are your reasons to sell? (profit targets, technical invalidation, etc.)").pack(anchor='w')
    reasons_text = tk.Text(control_frame, height=7, wrap=tk.WORD)
    reasons_text.pack(fill=tk.X, pady=(0,10))

    # Rules Checklist
    stock_in_play_var = tk.BooleanVar(value=0)
    solid_trade_entry_var = tk.BooleanVar(value=0)
    followed_exit_strategy_var = tk.BooleanVar(value=0)
    proper_position_size_var = tk.BooleanVar(value=0)
    
    ttk.Checkbutton(control_frame, text="Stock in play (Confirming volume, catalyst, and chart clarity)", 
                    variable=stock_in_play_var).pack(anchor='w', pady=5)
    ttk.Checkbutton(control_frame, text="Solid trade entry (Pattern is playing out as expected)", 
                    variable=solid_trade_entry_var).pack(anchor='w', pady=5)
    ttk.Checkbutton(control_frame, text="Following exit strategy (Sticking to planned stops/targets)", 
                    variable=followed_exit_strategy_var).pack(anchor='w', pady=5)
    ttk.Checkbutton(control_frame, text="Proper position size for trade quality", 
                    variable=proper_position_size_var).pack(anchor='w', pady=5)
    
    # Add explanatory text
    explanation = ttk.Label(control_frame, text="Verify these rules are being followed during your trade.", 
                          wraplength=300, font=('Arial', 9, 'italic'))
    explanation.pack(pady=10)
    
    # Add consequence reminder
    consequence = ttk.Label(control_frame, text="Breaking these rules mid-trade leads to F grades and potential losses!", 
                          wraplength=300, foreground='red', font=('Arial', 9, 'bold'))
    consequence.pack(pady=5)

    # Final Actions
    actions_frame = ttk.Frame(control_frame)
    actions_frame.pack(fill=tk.X, pady=10)
    
    submit_button = ttk.Button(actions_frame, text="Submit", command=submit_from_checkpoint)
    submit_button.pack(side=tk.LEFT, padx=5)
    
    clear_button = ttk.Button(actions_frame, text="Clear", command=clear_checkpoint)
    clear_button.pack(side=tk.LEFT, padx=5)

    # Add mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(-1 * int(event.delta/120), "units")
    
    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    # Bind mousewheel only when mouse is over the canvas
    canvas.bind('<Enter>', _bind_mousewheel)
    canvas.bind('<Leave>', _unbind_mousewheel)

    # Clean up scrolling when tab changes
    def _on_tab_change(event):
        canvas.unbind_all("<MouseWheel>")
    notebook.bind("<<NotebookTabChanged>>", _on_tab_change)

    return outer_frame

# Update the main UI setup to remove the rules frame and create the impulse control frame
impulse_control = create_impulse_control_frame(notes_rules_frame)

# Constants (at the top of your file)
PREMARKET_CATEGORIES = ["Engagement", "Catalyst Research", "Opening Game Plans"]
REGULAR_CATEGORIES = ["Engagement", "Entries", "Sizing", "Exit strategy"]

# Add to your save_state function (or create it if it doesn't exist)
def save_state():
    global goal_entries
    state = {
        'goal_entries': {
            'Process': goal_entries['Process'].get('1.0', tk.END).strip(),
            'Lead': goal_entries['Lead'].get(),
            'Lag': goal_entries['Lag'].get(),
            'Commitment': goal_entries['Commitment'].get(),
            'Obstacle': goal_entries['Obstacle'].get(),
            'Solution': goal_entries['Solution'].get(),
            'Review': goal_entries['Review'].get('1.0', tk.END).strip()
        }
    }
    
    # Ensure directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save state to file
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

# Add to your load_state function (or create it if it doesn't exist)
def load_state():
    global goal_entries
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                
                # Load goal entries
                if 'goal_entries' in state:
                    goal_data = state['goal_entries']
                    # Handle Text widgets
                    for key in ['Process', 'Review']:
                        if key in goal_data and goal_entries.get(key):
                            goal_entries[key].delete('1.0', tk.END)
                            if goal_data[key]:
                                goal_entries[key].insert('1.0', goal_data[key])
                    
                    # Handle Entry widgets
                    for key in ['Lead', 'Lag', 'Commitment', 'Obstacle', 'Solution']:
                        if key in goal_data and goal_entries.get(key):
                            goal_entries[key].delete(0, tk.END)
                            if goal_data[key]:
                                goal_entries[key].insert(0, goal_data[key])
                
                # ... load other state data ...
    except Exception as e:
        print(f"Error loading state: {e}")
        traceback.print_exc()

# Add this to your root window setup
def on_closing():
    try:
        print("Application closing...")
        save_app_state()
        print("State saved successfully")
        root.destroy()
    except Exception as e:
        print(f"Error during closing: {str(e)}")
        traceback.print_exc()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Call load_state after creating all widgets
load_state()

def save_goal_tracking():
    try:
        # Create a dictionary to store all goal tracking data
        goal_data = {
            "month": datetime.now().strftime("%B %Y"),
            "goals": {},
            "weekly_checkins": {},
            "monthly_review": {}
        }
        
        # Save to JSON file
        goal_file = DATA_DIR / "goal_tracking.json"
        with open(goal_file, 'w') as f:
            json.dump(goal_data, f, indent=4)
            
        messagebox.showinfo("Success", "Goal tracking data saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save goal tracking data: {str(e)}")

def load_goal_history():
    """Load the goal history from JSON file"""
    try:
        if GOAL_HISTORY_FILE.exists():
            with open(GOAL_HISTORY_FILE, 'r') as f:
                content = f.read()
                if content.strip():
                    return json.loads(content)
        return {}
    except Exception as e:
        print(f"Error loading goal history: {e}")
        return {}

def save_goal_history(goals):
    """Save the goal history to JSON file"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(GOAL_HISTORY_FILE, 'w') as f:
            json.dump(goals, f, indent=2)
    except Exception as e:
        print(f"Error saving goal history: {e}")

def create_goal_tracking_tab(notebook):
    goal_tab = ttk.Frame(notebook)
    notebook.add(goal_tab, text="Goal Tracker")
    
    # Load existing goals
    goals = load_goal_history()
    
    # Create main frame
    main_frame = ttk.Frame(goal_tab)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Current Goal Section at top
    current_goal_frame = ttk.LabelFrame(main_frame, text="Current Trading Goal (If app is still open from prior day, have to close/reopen for it to move to next day.)")
    current_goal_frame.pack(fill=tk.X, pady=(0, 10))
    
    goal_text = tk.Text(current_goal_frame, height=4, wrap=tk.WORD)
    goal_text.pack(fill=tk.X, padx=5, pady=5)
    
    # Load today's goal if it exists
    today = datetime.now().strftime("%Y-%m-%d")
    if today in goals:
        goal_text.insert('1.0', goals[today]['goal'])
    
    def save_current_goal():
        goal_content = goal_text.get('1.0', 'end-1c').strip()
        if goal_content:
            goals[today] = {'goal': goal_content, 'completed': False}
            save_goal_history(goals)
            update_goals_list()
            calculate_stats()
            messagebox.showinfo("Success", "Goal saved successfully!")
    
    save_btn = ttk.Button(current_goal_frame, text="Save Goal", command=save_current_goal)
    save_btn.pack(pady=(0, 5))
    
    # Month and Year selection
    controls_frame = ttk.Frame(main_frame)
    controls_frame.pack(fill=tk.X, pady=5)
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    month_var = tk.StringVar(value=calendar.month_name[current_month])
    year_var = tk.StringVar(value=str(current_year))
    
    ttk.Label(controls_frame, text="Month:").pack(side=tk.LEFT, padx=5)
    month_combo = ttk.Combobox(controls_frame, textvariable=month_var,
                              values=list(calendar.month_name)[1:],
                              state="readonly")
    month_combo.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(controls_frame, text="Year:").pack(side=tk.LEFT, padx=5)
    year_combo = ttk.Combobox(controls_frame, textvariable=year_var,
                             values=[str(y) for y in range(current_year-1, current_year+3)],
                             state="readonly")
    year_combo.pack(side=tk.LEFT, padx=5)
    
    # Create scrollable frame for goals list
    goals_frame = ttk.LabelFrame(main_frame, text="Goals History")
    goals_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
    
    canvas = tk.Canvas(goals_frame)
    scrollbar = ttk.Scrollbar(goals_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
    scrollbar.pack(side="right", fill="y")
    
    # Bottom frame for stats and achievements
    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Stats Frame
    stats_frame = ttk.LabelFrame(bottom_frame, text="Goal Statistics")
    stats_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    # Stats labels
    total_label = ttk.Label(stats_frame, text="Total Goals Set: 0")
    total_label.pack(anchor='w', padx=5, pady=2)
    
    completed_label = ttk.Label(stats_frame, text="Goals Completed: 0")
    completed_label.pack(anchor='w', padx=5, pady=2)
    
    rate_label = ttk.Label(stats_frame, text="Completion Rate: 0%")
    rate_label.pack(anchor='w', padx=5, pady=2)
    
    streak_label = ttk.Label(stats_frame, text="Current Streak: 0 days")
    streak_label.pack(anchor='w', padx=5, pady=2)
    
    longest_label = ttk.Label(stats_frame, text="Longest Streak: 0 days")
    longest_label.pack(anchor='w', padx=5, pady=2)
    
    # Progress bar
    progress_var = tk.DoubleVar()
    ttk.Progressbar(stats_frame, variable=progress_var, maximum=100, length=200).pack(pady=10)
    
    # Achievements Frame
    achievements_frame = ttk.LabelFrame(bottom_frame, text="Achievements")
    achievements_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    
    achievements = {
        "beginner": {"name": "Goal Setter", "desc": "Set your first goal", "unlocked": False},
        "consistent": {"name": "Consistency King", "desc": "Complete 5 goals in a row", "unlocked": False},
        "streak10": {"name": "Perfect 10", "desc": "Maintain a 10-day streak", "unlocked": False},
        "monthly": {"name": "Monthly Champion", "desc": "Complete all goals in a month", "unlocked": False}
    }
    
    achievement_labels = {}
    for key, achievement in achievements.items():
        frame = ttk.Frame(achievements_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)
        
        icon_label = ttk.Label(frame, text="🔒")
        icon_label.pack(side=tk.LEFT, padx=(0, 5))
        
        text_label = ttk.Label(frame, text=f"{achievement['name']}: {achievement['desc']}")
        text_label.pack(side=tk.LEFT, fill=tk.X)
        
        achievement_labels[key] = (icon_label, text_label)
    
    def check_achievements(completion_rate, current_streak, longest_streak, total_goals):
        # Check each achievement condition and update display
        if total_goals > 0:
            achievements["beginner"]["unlocked"] = True
        if current_streak >= 5:
            achievements["consistent"]["unlocked"] = True
        if longest_streak >= 10:
            achievements["streak10"]["unlocked"] = True
        # Require at least 20 goals in a month with 100% completion
        if completion_rate == 100 and total_goals >= 20:
            achievements["monthly"]["unlocked"] = True
        
        # Update achievement display
        for key, achievement in achievements.items():
            icon_label, text_label = achievement_labels[key]
            if achievement["unlocked"]:
                icon_label.config(text="🏆")
                text_label.config(foreground="green")
            else:
                icon_label.config(text="🔒")
                text_label.config(foreground="black")

    def calculate_stats():
        month = list(calendar.month_name).index(month_var.get())
        year = int(year_var.get())
        
        total_goals = 0
        completed_goals = 0
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        # Get all weekdays in the month
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            for day in week[:5]:  # Monday-Friday only
                if day != 0:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    if date_str in goals:
                        total_goals += 1
                        if goals[date_str].get('completed', False):
                            completed_goals += 1
                            temp_streak += 1
                            longest_streak = max(longest_streak, temp_streak)
                            if datetime.strptime(date_str, "%Y-%m-%d").date() <= datetime.now().date():
                                current_streak = temp_streak
                        else:
                            temp_streak = 0
                            if datetime.strptime(date_str, "%Y-%m-%d").date() <= datetime.now().date():
                                current_streak = 0
        
        completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
        
        # Update stats labels
        total_label.config(text=f"Total Goals Set: {total_goals}")
        completed_label.config(text=f"Goals Completed: {completed_goals}")
        rate_label.config(text=f"Completion Rate: {completion_rate:.1f}%")
        streak_label.config(text=f"Current Streak: {current_streak} days")
        longest_label.config(text=f"Longest Streak: {longest_streak} days")
        
        # Update progress bar
        progress_var.set(completion_rate)
        
        # Update achievement status
        check_achievements(completion_rate, current_streak, longest_streak, total_goals)

    def update_completion(date_str, completed):
        if date_str in goals:
            goals[date_str]['completed'] = completed
            save_goal_history(goals)
            calculate_stats()

    def update_goals_list(*args):
        # Clear existing goals
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        month = list(calendar.month_name).index(month_var.get())
        year = int(year_var.get())
        
        # Get all weekdays in the month
        cal = calendar.monthcalendar(year, month)
        for week in cal:
            for day in week[:5]:  # Monday-Friday only
                if day != 0:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    
                    # Create frame for each day
                    day_frame = ttk.Frame(scrollable_frame)
                    day_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    # Configure column weights
                    day_frame.columnconfigure(1, weight=1)  # Make goal text column expandable
                    
                    # Date label (fixed width, column 0)
                    date_label = ttk.Label(day_frame, 
                                         text=f"{calendar.day_name[calendar.weekday(year, month, day)]} {month:02d}/{day:02d}",
                                         width=20)
                    date_label.grid(row=0, column=0, padx=(0, 10), sticky='w')
                    
                    if date_str in goals:
                        # Goal text (expandable, column 1)
                        goal_display = ttk.Label(day_frame, 
                                               text=goals[date_str]['goal'],
                                               wraplength=350)  # Fixed wraplength to ensure space for checkbox
                        goal_display.grid(row=0, column=1, sticky='ew', padx=(0, 10))
                        
                        # Completion checkbox (fixed width, column 2)
                        completed_var = tk.BooleanVar(value=goals[date_str].get('completed', False))
                        ttk.Checkbutton(day_frame, 
                                      text="Complete", 
                                      variable=completed_var,
                                      command=lambda d=date_str, v=completed_var: update_completion(d, v.get())
                                      ).grid(row=0, column=2, sticky='e')
                    else:
                        ttk.Label(day_frame, text="No goal set").grid(row=0, column=1, sticky='w')
        
        calculate_stats()

    # Bind updates and initial update
    month_combo.bind('<<ComboboxSelected>>', update_goals_list)
    year_combo.bind('<<ComboboxSelected>>', update_goals_list)
    update_goals_list()
    
    return goal_tab


goal_tracking_tab = create_goal_tracking_tab(notebook)

# ... existing code ...

def create_playbook_tab(notebook):
    playbook_tab = ttk.Frame(notebook)
    notebook.add(playbook_tab, text="Playbook")
    
    # Create top control panel
    control_frame = ttk.Frame(playbook_tab)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Setup selection area
    ttk.Label(control_frame, text="Select Setup:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0,10))
    setup_var = tk.StringVar()
    setup_combo = ttk.Combobox(control_frame, textvariable=setup_var, state="readonly", width=30)
    setup_combo.pack(side=tk.LEFT, padx=5)
    
    # Create text widgets dictionary at the top level of the function
    text_widgets = {}
    
    # Define a smaller font for text boxes
    small_font = tkfont.Font(size=9)  # Adjust the size as needed
    
    def save_current_setup():
        current = setup_var.get()
        if not current:
            return
            
        setups = load_setups()
        if current not in setups:
            setups[current] = {}
        
        # Save text fields
        for key, widget in text_widgets.items():
            setups[current][key.lower().replace(' ', '_')] = widget.get('1.0', tk.END.strip())
        
        save_setups(setups)
        messagebox.showinfo("Success", "Setup saved successfully!")
    
    def add_new_setup():
        setup_name = simpledialog.askstring("New Setup", "Enter name for new setup:")
        if not setup_name:
            return
        
        setups = load_setups()
        if setup_name in setups:
            messagebox.showerror("Error", "A setup with this name already exists!")
            return
        
        setups[setup_name] = {
            "description": "",
            "identification": "",
            "entry_rules": "",
            "exit_rules": "",
            "risk_management": "",
            "notes": "",
            "images": []
        }
        
        save_setups(setups)
        update_setup_list()
        setup_combo.set(setup_name)
        show_setup_details()
    
    def delete_setup():
        current = setup_var.get()
        if not current:
            messagebox.showwarning("Warning", "Please select a setup to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", 
                                  f"Are you sure you want to delete the setup '{current}'?"):
            return
        
        setups = load_setups()
        if current in setups and "images" in setups[current]:
            for img_path in setups[current]["images"]:
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"Error removing image file: {e}")
        
        if current in setups:
            del setups[current]
        
        save_setups(setups)
        clear_details()
        update_setup_list()
        setup_combo.set('')
        
        messagebox.showinfo("Success", "Setup deleted successfully!")
    
    # Control buttons in the same row
    ttk.Button(control_frame, text="Add New Setup", command=add_new_setup).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Delete Setup", command=delete_setup).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Save Setup", command=save_current_setup).pack(side=tk.LEFT, padx=5)
    
    # Details area (full width)
    details_frame = ttk.Frame(playbook_tab)
    details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
    
    details_canvas = tk.Canvas(details_frame)
    scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=details_canvas.yview)
    scrollable_frame = ttk.Frame(details_canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all"))
    )
    
    details_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    details_canvas.configure(yscrollcommand=scrollbar.set)
    
    # Create text fields for setup details
    fields = {
        "Description": ("Setup Description:", 6),
        "Identification": ("Identification Metrics:", 6),
        "Entry Rules": ("Entry Rules:", 6),
        "Exit Rules": ("Exit Rules:", 6),
        "Risk Management": ("Risk Management Rules:", 6),
        "Notes": ("Additional Notes:", 6)
    }
    
    for key, (label_text, height) in fields.items():
        frame = ttk.LabelFrame(scrollable_frame, text=label_text)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        text_widget = tk.Text(frame, height=height, wrap=tk.WORD, font=small_font)
        text_widget.pack(fill=tk.X, padx=5, pady=5)
        text_widgets[key] = text_widget
    
    image_frame = ttk.LabelFrame(scrollable_frame, text="Example Images")
    image_frame.pack(fill=tk.X, padx=5, pady=5)

    # Create list view for images
    image_list = ttk.Frame(image_frame)
    image_list.pack(fill=tk.X, padx=5, pady=5)
        
    def add_image():
        current = setup_var.get()
        if not current:
            messagebox.showwarning("Warning", "Please select a setup first")
            return
            
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_paths:
            setups = load_setups()
            if current not in setups:
                setups[current] = {"images": []}
            
            # Copy images to application data directory
            for path in file_paths:
                filename = f"{current}_{len(setups[current]['images'])}_{os.path.basename(path)}"
                dest_path = DATA_DIR / "playbook_images" / filename
                dest_path.parent.mkdir(exist_ok=True)
                shutil.copy2(path, dest_path)
                setups[current]["images"].append(str(dest_path))
            
            save_setups(setups)
            update_image_preview()
    
    def update_image_preview():
        # Clear existing list items
        for widget in image_list.winfo_children():
            widget.destroy()

        current = setup_var.get()
        if not current:
            return

        setups = load_setups()
        if current in setups and "images" in setups[current]:
            for idx, img_path in enumerate(setups[current]["images"]):
                try:
                    # Create frame for each image entry
                    entry_frame = ttk.Frame(image_list)
                    entry_frame.pack(fill=tk.X, pady=2)

                    # File name label
                    name_label = ttk.Label(entry_frame, text=os.path.basename(img_path))
                    name_label.pack(side=tk.LEFT, padx=(5, 10))
                    
                    # Make the label clickable
                    name_label.bind("<Button-1>", lambda e, path=img_path: show_full_image(path))
                    name_label.bind("<Enter>", lambda e: e.widget.configure(cursor="hand2"))
                    name_label.bind("<Leave>", lambda e: e.widget.configure(cursor=""))

                    # Remove button
                    ttk.Button(
                        entry_frame,
                        text="Remove",
                        command=lambda i=idx: remove_image(i)
                    ).pack(side=tk.RIGHT, padx=5)

                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
    
    def remove_image(index):
        current = setup_var.get()
        if current:
            setups = load_setups()
            if current in setups and "images" in setups[current]:
                # Remove image file
                img_path = setups[current]["images"][index]
                try:
                    os.remove(img_path)
                except Exception as e:
                    print(f"Error removing image file: {e}")
                
                # Remove from setup data
                setups[current]["images"].pop(index)
                save_setups(setups)
                update_image_preview()
    
    def show_full_image(path):
        """Create a popup window with 4 most recent images"""
        try:
            # Temporarily disable the topmost attribute of the main window
            root.attributes('-topmost', False)
            
            # Create new window
            img_window = tk.Toplevel()
            img_window.title("Image View")
            img_window.state('zoomed')  # Start maximized
            
            # Get current setup and all its images
            current_setup = setup_var.get()
            setups = load_setups()
            current_images = setups[current_setup]["images"]
            current_index = current_images.index(path)
            
            # Calculate starting indices for the 4 displays
            # Start with clicked image, then show 3 most recent images
            total_images = len(current_images)
            display_indices = []
            
            # Add clicked image first
            display_indices.append(current_index)
            
            # Add up to 3 most recent images after the clicked image
            for i in range(1, 4):
                next_index = (current_index + i) % total_images
                if next_index not in display_indices:
                    display_indices.append(next_index)
            
            # If we still need more images, add earlier images
            while len(display_indices) < 4:
                prev_index = (display_indices[0] - 1) % total_images
                if prev_index not in display_indices:
                    display_indices.insert(0, prev_index)
            
            # Create frames for each image display
            image_frames = []
            current_indices = display_indices
            image_labels = []
            photos = []
            
            frame_container = ttk.Frame(img_window)
            frame_container.pack(expand=True, fill='both', padx=20, pady=20)
            
            # Configure grid with more weight
            frame_container.columnconfigure(0, weight=1)
            frame_container.columnconfigure(1, weight=1)
            frame_container.rowconfigure(0, weight=1)
            frame_container.rowconfigure(1, weight=1)
            
            def update_image(display_index, new_index, frame_width=None, frame_height=None):
                if 0 <= new_index < len(current_images):
                    current_indices[display_index] = new_index
                    
                    # Load image
                    img = PILImage.open(current_images[new_index])
                    
                    # If no specific dimensions provided, use default sizes
                    if frame_width is None or frame_width <= 0:
                        frame_width = max(400, frame_container.winfo_width() // 2 - 60)
                    if frame_height is None or frame_height <= 0:
                        frame_height = max(300, frame_container.winfo_height() // 2 - 100)
                    
                    # Calculate scaling to fit in frame while maximizing size
                    scale = min(frame_width/img.width, frame_height/img.height)
                    new_width = int(img.width * scale)
                    new_height = int(img.height * scale)
                    
                    img = img.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    photos[display_index] = photo
                    image_labels[display_index].configure(image=photo)
                    counter_labels[display_index].configure(
                        text=f"Image {new_index + 1} of {len(current_images)}")
            
            def on_resize(event=None):
                if event.widget == frame_container:
                    # Calculate available space for each frame
                    frame_width = max(400, (frame_container.winfo_width() // 2) - 30)
                    frame_height = max(300, (frame_container.winfo_height() // 2) - 50)
                    
                    # Update all images with new size
                    for i in range(4):
                        update_image(i, current_indices[i], frame_width, frame_height)
            
            # Create 4 image frames in a 2x2 grid
            counter_labels = []
            button_font = ('Arial', 12)
            label_font = ('Arial', 11)
            
            for i in range(4):
                frame = ttk.LabelFrame(frame_container, text=f"Example {i+1}")
                row = i // 2
                col = i % 2
                frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                
                # Configure frame grid weights
                frame.columnconfigure(0, weight=1)
                frame.rowconfigure(0, weight=1)
                
                # Create image label with expanded size
                label = ttk.Label(frame)
                label.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
                image_labels.append(label)
                photos.append(None)
                
                # Navigation frame
                nav_frame = ttk.Frame(frame)
                nav_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
                nav_frame.columnconfigure(1, weight=1)
                
                # Previous button
                prev_btn = ttk.Button(nav_frame, text="← Previous", 
                                    command=lambda idx=i: update_image(idx, current_indices[idx] - 1))
                prev_btn.grid(row=0, column=0, padx=5)
                
                # Counter label
                counter_label = ttk.Label(nav_frame, text=f"Image 1 of {len(current_images)}", 
                                        font=label_font)
                counter_label.grid(row=0, column=1, padx=5)
                counter_labels.append(counter_label)
                
                # Next button
                next_btn = ttk.Button(nav_frame, text="Next →",
                                    command=lambda idx=i: update_image(idx, current_indices[idx] + 1))
                next_btn.grid(row=0, column=2, padx=5)
            
            # Load initial images with full size
            frame_width = max(400, (frame_container.winfo_width() // 2) - 30)
            frame_height = max(300, (frame_container.winfo_height() // 2) - 50)
            for i in range(4):
                update_image(i, current_indices[i], frame_width, frame_height)
            
            # Close button
            close_btn = ttk.Button(img_window, text="Close", 
                                 command=lambda: [img_window.destroy(), root.attributes('-topmost', True)])
            close_btn.pack(pady=10)
            
            # Bind resize event
            frame_container.bind('<Configure>', on_resize)
            img_window.bind('<Escape>', lambda e: [img_window.destroy(), root.attributes('-topmost', True)])
            
        except Exception as e:
            # Restore topmost in case of error
            root.attributes('-topmost', True)
            messagebox.showerror("Error", f"Failed to open images: {str(e)}")
    
    ttk.Button(image_frame, text="Add Images", command=add_image).pack(pady=5)
    
    # Pack canvas and scrollbar
    details_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def clear_details():
        for widget in text_widgets.values():
            widget.delete('1.0', tk.END)
        setup_var.set('')
        update_image_preview()
    
    def show_setup_details(*args):
        current = setup_var.get()
        if not current:
            clear_details()
            return
            
        setups = load_setups()
        if current in setups:
            # Load text fields
            for key, widget in text_widgets.items():
                widget.delete('1.0', tk.END)
                content = setups[current].get(key.lower().replace(' ', '_'), '')
                if content:
                    widget.insert('1.0', content)
            
            update_image_preview()
    
    def update_setup_list():
        setups = load_setups()
        setup_combo['values'] = list(setups.keys())
    
    # Bind setup selection to update details
    setup_combo.bind('<<ComboboxSelected>>', show_setup_details)
    
    # Initial update of setup list
    update_setup_list()
    
    return playbook_tab

def save_setups(setups):
    """Save setups to JSON file"""
    setup_file = DATA_DIR / "playbook_setups.json"
    with open(setup_file, 'w') as f:
        json.dump(setups, f, indent=2)

# Add this line after creating other tabs
playbook_tab = create_playbook_tab(notebook)

# ... existing code ...

# Add this after your other notebook tabs
weekly_review_tab = ttk.Frame(notebook)
notebook.add(weekly_review_tab, text="Weekly Review")

def create_weekly_review_content(parent):
    # Define small font
    small_font = tkfont.Font(size=9)

    # Create main container frame with padding
    container = ttk.Frame(parent, padding="10")
    container.pack(fill=tk.BOTH, expand=True)

    # Create canvas and scrollbar
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    
    # Create the main content frame
    content_frame = ttk.Frame(canvas)
    
    # Configure canvas scrolling
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    content_frame.bind('<Configure>', configure_scroll_region)
    
    # Create the window in the canvas
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Configure canvas and scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Configure canvas resize
    def configure_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind('<Configure>', configure_canvas)
    
    # Pack scrollbar first, then canvas
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Create sections dictionary to store widgets
    sections = {}

    def create_section(title, questions, height=4):
        frame = ttk.LabelFrame(content_frame, text=title)
        frame.pack(fill=tk.X, padx=(0, 15), pady=5)  # Add right padding to avoid scrollbar
        
        inner_frame = ttk.Frame(frame, padding="10")
        inner_frame.pack(fill=tk.X, expand=True)
        
        section_widgets = {}
        for q in questions:
            label = ttk.Label(inner_frame, text=q, wraplength=600)
            label.pack(anchor="w", pady=(5,0))
            
            # Create a frame to contain the text widget
            text_frame = ttk.Frame(inner_frame)
            text_frame.pack(fill=tk.X, pady=(5,10))
            text_frame.grid_columnconfigure(0, weight=1)
            
            # Create text widget with small font
            text = tk.Text(text_frame, height=1, wrap=tk.WORD, font=small_font)
            text.grid(row=0, column=0, sticky="ew")
            
            # Add auto-resize functionality
            def auto_resize(event=None, txt=text):
                # Get the width in pixels
                width = txt.winfo_width()
                
                # Create a temporary window to calculate wrapped height
                txt.update_idletasks()
                
                # Calculate content width using font metrics
                content = txt.get("1.0", "end-1c")
                font = tkfont.Font(font=txt['font'])
                
                # Split content into words and calculate wrapped lines
                words = content.split()
                current_line = []
                num_lines = 1
                current_width = 0
                
                for word in words:
                    word_width = font.measure(word + " ")
                    if current_width + word_width <= width:
                        current_width += word_width
                    else:
                        num_lines += 1
                        current_width = word_width
                
                # Add extra lines for explicit line breaks
                num_lines += content.count('\n')
                
                # Set the height of the text widget
                txt.configure(height=max(1, num_lines))
            
            # Bind to both keyup and window resize events
            text.bind('<KeyRelease>', auto_resize)
            text_frame.bind('<Configure>', lambda e, txt=text: auto_resize(None, txt))
            
            section_widgets[q] = text
        
        return section_widgets

    # Goal Review Section
    goal_questions = [
        "How well did I follow my process goals this week?",
        "Which goals were most challenging to maintain and why?",
        "What adjustments should I make to my goals for next week?"
    ]
    sections["goals"] = create_section("Goal Review", goal_questions)

    # Trade Setup Analysis
    setup_questions = [
        "Which setups performed best this week? Why?",
        "Which setups underperformed or failed? What were the common factors?",
        "What new patterns or opportunities did I notice this week?"
    ]
    sections["setups"] = create_section("Trade Setup Analysis", setup_questions)

    # Emotional Management
    emotion_questions = [
        "How well did I manage my emotions this week?",
        "What were my most common emotional triggers?",
        "How effective was my emotional reset process when needed?"
    ]
    sections["emotions"] = create_section("Emotional Management", emotion_questions)

    # Risk Management
    risk_questions = [
        "How well did I maintain my position sizing rules?",
        "Did I properly honor my stop losses?",
        "Were my risk/reward ratios appropriate for each trade?"
    ]
    sections["risk"] = create_section("Risk Management", risk_questions)

    # Market Analysis
    market_questions = [
        "What were the dominant market conditions this week?",
        "How well did I adapt to changing market conditions?",
        "What market factors most influenced my trading decisions?"
    ]
    sections["market"] = create_section("Market Analysis", market_questions)

    # Performance Metrics
    metrics_questions = [
        "What was my grade distribution (A/B/F) this week?",
        "How does my grade distribution compare to previous weeks?",
        "How does my p/l compare to what it could have been had I followed my exit strategy?",
        
    ]
    sections["metrics"] = create_section("Performance Metrics", metrics_questions)

    # Areas for Improvement
    improvement_questions = [
        "What were my three biggest trading mistakes this week?",
        "What specific actions will I take to address these issues?",
        "What skills do I need to develop or strengthen?"
    ]
    sections["improvement"] = create_section("Areas for Improvement", improvement_questions)

    # Positive Reinforcement
    positive_questions = [
        "What were my three best trades this week and why?",
        "Which aspects of my trading process worked particularly well?",
        "What positive habits did I maintain consistently?"
    ]
    sections["positive"] = create_section("Positive Reinforcement", positive_questions)

    # Next Week's Focus
    focus_questions = [
        "What are my top three trading priorities for next week?",
        "What specific metrics will I use to measure improvement?",
        "What market conditions am I preparing for?"
    ]
    sections["focus"] = create_section("Next Week's Focus", focus_questions)

    # Add Export and Clear buttons
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(pady=20, padx=(0, 15))  # Add right padding to avoid scrollbar

    def export_weekly_review():
        try:
            # Create file path
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f"Weekly_Review_{current_date}.pdf"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=filename
            )
            
            if not file_path:
                return

            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Create custom style for section headers
            styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=10,
                spaceBefore=20,
                textColor=colors.HexColor('#1B4F72')
            ))

            # Add title
            elements.append(Paragraph(f"Weekly Trading Review - Week of {current_date}", styles['Title']))
            elements.append(Spacer(1, 20))

            # Add content from each section
            for section_name, section_widgets in sections.items():
                # Add section header
                elements.append(Paragraph(section_name.replace("_", " ").title(), styles['SectionHeader']))
                
                for question, text_widget in section_widgets.items():
                    # Add question
                    elements.append(Paragraph(question, styles['Heading3']))
                    
                    # Add answer
                    answer = text_widget.get("1.0", tk.END).strip()
                    if answer:
                        elements.append(Paragraph(answer, styles['Normal']))
                    else:
                        elements.append(Paragraph("No response provided", styles['Italic']))
                    
                    elements.append(Spacer(1, 10))

            # Build PDF
            doc.build(elements)
            messagebox.showinfo("Export Successful", f"Weekly review exported to {file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export weekly review: {str(e)}")

    def clear_weekly_review():
        if messagebox.askyesno("Clear Review", "Are you sure you want to clear all entries?"):
            for section_widgets in sections.values():
                for text_widget in section_widgets.values():
                    text_widget.delete("1.0", tk.END)
            messagebox.showinfo("Clear", "Weekly review cleared successfully!")

    ttk.Button(button_frame, text="Export Review", command=export_weekly_review).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Clear Review", command=clear_weekly_review).pack(side=tk.LEFT, padx=5)

    # Configure mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Update the mousewheel binding for text widgets
    def _bind_text_scroll(event):
        if event.state == 0:  # No modifier keys
            widget = event.widget
            lines = int(widget.index('end-1c').split('.')[0])
            if lines <= widget.cget('height'):  # If content fits in widget
                return
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    # Bind all text widgets for proper scrolling
    for section in sections.values():
        for text_widget in section.values():
            text_widget.bind("<MouseWheel>", _bind_text_scroll)

    return content_frame, sections

# Create the Weekly Review content
weekly_review_frame, weekly_review_sections = create_weekly_review_content(weekly_review_tab)
        
root.mainloop()