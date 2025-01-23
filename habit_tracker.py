import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Function to create the database and table
def create_db():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS habits (
                  id INTEGER PRIMARY KEY,
                  habit TEXT NOT NULL,
                  completion TEXT DEFAULT '',
                  start_date DATE NOT NULL
              )
              ''')
    conn.commit()
    conn.close()

# Function to add a new habit
def add_habit():
    habit_name = habit_entry.get().strip()
    if habit_name:
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("INSERT INTO habits (habit, start_date) VALUES (?, ?)", (habit_name, datetime.now().date()))
        conn.commit()
        conn.close()
        habit_entry.delete(0, tk.END)
        load_habits()
    else:
        messagebox.showwarning("Warning", "Please enter a habit name.")

# Function to load habits from the database
def load_habits():
    for widget in habit_frame.winfo_children():
        widget.destroy()
        
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT * FROM habits")
    habits = c.fetchall()
    conn.close()
    
    # Create a header for the habits section
    header_label = tk.Label(habit_frame, text="Your Habits", font=("Helvetica", 16, "bold"), bg="white")
    header_label.pack(pady=5)

    # Create a list of day names
    day_names = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

    for habit in habits:
        # Frame for each habit
        habit_container = tk.Frame(habit_frame, bg="white", padx=10, pady=5, borderwidth=1, relief="sunken")
        habit_container.pack(fill='x', pady=5)

        habit_label = tk.Label(habit_container, text=habit[1], font=("Helvetica", 14), bg="lightgray", anchor='w')
        habit_label.pack(side=tk.LEFT, fill='x', expand=True)

        # Calculate completion percentage
        completion = habit[2]
        completed_days = completion.count('1')
        
        # Calculate the percentage based on the number of completed days (each day = 14.29%)
        completion_rate = (completed_days / 7) * 100
        completion_label = tk.Label(habit_container, text=f"{completion_rate:.2f}%", bg="lightblue", padx=10)
        completion_label.pack(side=tk.LEFT)

        # Create a frame for checkboxes
        checkbox_frame = tk.Frame(habit_container, bg="white")
        checkbox_frame.pack(side=tk.LEFT)

        # Create a header for the checkboxes
        checkbox_header_frame = tk.Frame(checkbox_frame, bg="white")
        checkbox_header_frame.pack(fill='x')

        for day in day_names:
            day_label = tk.Label(checkbox_header_frame, text=day, font=("Helvetica", 8), bg="lightgray", width=3)
            day_label.pack(side=tk.LEFT)

        for day in range(7):
            button_text = "✓" if day < len(completion) and completion[day] == '1' else "X"
            button = tk.Button(checkbox_frame, text=button_text, command=lambda h=habit, d=day: toggle_completion(h[0], d), width=2)
            button.pack(side=tk.LEFT)

        # Button for deleting habit
        delete_button = tk.Button(habit_container, text="Delete", command=lambda h=habit[0]: delete_habit(h), bg="red", fg="white")
        delete_button.pack(side=tk.RIGHT)

# Function to toggle the completion of a habit
def toggle_completion(habit_id, day):
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT completion FROM habits WHERE id = ?", (habit_id,))
    completion = c.fetchone()[0]

    # Toggle completion status
    if day < len(completion):
        if completion[day] == '1':
            completion = completion[:day] + '0' + completion[day + 1:]  # Mark as not completed
        else:
            completion = completion[:day] + '1' + completion[day + 1:]  # Mark as completed
    else:
        completion += '1'  # Add new completion if not already there

    c.execute("UPDATE habits SET completion = ? WHERE id = ?", (completion, habit_id))
    conn.commit()
    conn.close()
    load_habits()

# Function to delete a habit with confirmation
def delete_habit(habit_id):
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this habit?"):
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        conn.commit()
        conn.close()
        load_habits()

# Create GUI
app = tk.Tk()
app.title("Habit Tracker")
app.geometry("400x600")
app.configure(bg='white')

# Display current date and day
current_date = datetime.now().strftime("%A, %B %d, %Y")
date_label = tk.Label(app, text=current_date, font=("Helvetica", 14), bg="white")
date_label.pack(pady=10)

create_db()

# Frame for habit entry
input_frame = tk.Frame(app, bg='white')
input_frame.pack(pady=10)

habit_entry = tk.Entry(input_frame, width=30)
habit_entry.pack(side=tk.LEFT, padx=5)

add_button = tk.Button(input_frame, text="Add Habit", command=add_habit, bg="lightgreen")
add_button.pack(side=tk.LEFT, padx=5)

# Frame for displaying habits
habit_frame = tk.Frame(app, bg='white')
habit_frame.pack(pady=10, fill='both', expand=True)

load_habits()

app.mainloop()