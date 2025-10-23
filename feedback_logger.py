import sqlite3

def log_feedback(disease, remedy, feedback):
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (disease TEXT, remedy TEXT, feedback TEXT)''')
    c.execute("INSERT INTO feedback VALUES (?, ?, ?)", (disease, remedy, feedback))
    conn.commit()
    conn.close()