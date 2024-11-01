from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import mysql.connector

app = FastAPI()

# Database configuration
db_config = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'habitflow_db'
}

# Database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Pydantic models
class User(BaseModel):
    username: str
    email: str

class Habit(BaseModel):
    user_id: int
    name: str
    description: str

class Routine(BaseModel):
    user_id: int
    name: str
    habits: List[int]  # List of habit IDs

class HabitLog(BaseModel):
    habit_id: int
    date: str
    status: str

# User Management
@app.post("/users", response_model=int)
def create_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (user.username, user.email))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return User(**user)
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (user.username, user.email, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User updated"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User deleted"}

# Habit Management
@app.post("/habits", response_model=int)
def create_habit(habit: Habit):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (user_id, name, description) VALUES (%s, %s, %s)", 
                   (habit.user_id, habit.name, habit.description))
    conn.commit()
    habit_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return habit_id

@app.get("/habits/{habit_id}", response_model=Habit)
def get_habit(habit_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM habits WHERE id = %s", (habit_id,))
    habit = cursor.fetchone()
    cursor.close()
    conn.close()
    if habit:
        return Habit(**habit)
    raise HTTPException(status_code=404, detail="Habit not found")

@app.get("/users/{user_id}/habits", response_model=List[Habit])
def get_user_habits(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM habits WHERE user_id = %s", (user_id,))
    habits = cursor.fetchall()
    cursor.close()
    conn.close()
    return [Habit(**habit) for habit in habits]

@app.put("/habits/{habit_id}")
def update_habit(habit_id: int, habit: Habit):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE habits SET name = %s, description = %s WHERE id = %s", 
                   (habit.name, habit.description, habit_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Habit updated"}

@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE id = %s", (habit_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Habit deleted"}

# Routine Management
@app.post("/routines", response_model=int)
def create_routine(routine: Routine):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO routines (user_id, name) VALUES (%s, %s)", 
                   (routine.user_id, routine.name))
    conn.commit()
    routine_id = cursor.lastrowid
    for habit_id in routine.habits:
        cursor.execute("INSERT INTO routine_habits (routine_id, habit_id) VALUES (%s, %s)", 
                       (routine_id, habit_id))
    conn.commit()
    cursor.close()
    conn.close()
    return routine_id

@app.get("/routines/{routine_id}")
def get_routine(routine_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM routines WHERE id = %s", (routine_id,))
    routine = cursor.fetchone()
    cursor.close()
    conn.close()
    if routine:
        return routine
    raise HTTPException(status_code=404, detail="Routine not found")

@app.get("/users/{user_id}/routines")
def get_user_routines(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM routines WHERE user_id = %s", (user_id,))
    routines = cursor.fetchall()
    cursor.close()
    conn.close()
    return routines

@app.put("/routines/{routine_id}")
def update_routine(routine_id: int, routine: Routine):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE routines SET name = %s WHERE id = %s", 
                   (routine.name, routine_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Routine updated"}

@app.delete("/routines/{routine_id}")
def delete_routine(routine_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routines WHERE id = %s", (routine_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Routine deleted"}

# Additional Progress Tracking
@app.post("/habits/{habit_id}/log", response_model=int)
def log_habit_progress(habit_id: int, log: HabitLog):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habit_logs (habit_id, date, status) VALUES (%s, %s, %s)", 
                   (log.habit_id, log.date, log.status))
    conn.commit()
    log_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return log_id

@app.get("/habits/{habit_id}/logs")
def get_habit_logs(habit_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM habit_logs WHERE habit_id = %s", (habit_id,))
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return logs

@app.get("/users/{user_id}/progress")
def get_user_progress(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT habit_id, COUNT(*) as count FROM habit_logs WHERE habit_id IN (SELECT id FROM habits WHERE user_id = %s) GROUP BY habit_id", (user_id,))
    progress = cursor.fetchall()
    cursor.close()
    conn.close()
    return progress

# User Habit Streaks
@app.get("/users/{user_id}/streaks")
def get_user_habit_streaks(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT habit_id, MAX(DATEDIFF(CURDATE(), date)) as streak FROM habit_logs WHERE habit_id IN (SELECT id FROM habits WHERE user_id = %s) GROUP BY habit_id", (user_id,))
    streaks = cursor.fetchall()
    cursor.close()
    conn.close()
    return streaks

# Reminder Management
@app.post("/users/{user_id}/reminders")
def set_reminder(user_id: int, reminder: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (user_id, message, date_time) VALUES (%s, %s, %s)", 
                   (user_id, reminder['message'], reminder['date_time']))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Reminder set"}

@app.delete("/users/{user_id}/reminders/{reminder_id}")
def delete_reminder(user_id: int, reminder_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = %s AND user_id = %s", (reminder_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Reminder deleted"}

# Run the server with: uvicorn filename:app --reload
