import mysql.connector
from datetime import datetime

# ---------------- DATABASE CONNECTION ---------------- #

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="testdatabase"
)

cursor = db.cursor()

# ---------------- DATABASE SETUP ---------------- #

def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INT AUTO_INCREMENT PRIMARY KEY,
        keywords VARCHAR(255),
        answer TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        eligibility VARCHAR(255),
        duration VARCHAR(50),
        fees VARCHAR(50)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question TEXT,
        asked_on DATETIME
    )
    """)

    db.commit()


def insert_default_data():
    cursor.execute("SELECT COUNT(*) FROM faq")
    if cursor.fetchone()[0] == 0:
        faq_data = [
            ("courses,programs,degree",
             "We offer BSc IT, BCA, and BSc Computer Science."),
            ("eligibility,criteria,qualify",
             "Eligibility depends on the course. Ask for a specific course."),
            ("fees,fee,cost",
             "Fees vary by course. Ask about a specific course."),
            ("documents,certificate,proof",
             "Required documents: 10th & 12th mark sheets, TC, ID proof."),
            ("deadline,last date,closing",
             "Admissions close on 30th June."),
            ("hostel,accommodation",
             "Yes, hostel facilities are available.")
        ]
        cursor.executemany(
            "INSERT INTO faq (keywords, answer) VALUES (%s, %s)",
            faq_data
        )

    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        courses_data = [
            ("BSc IT", "12th standard with Mathematics", "3 Years", "₹60,000 per year"),
            ("BCA", "12th standard (any stream)", "3 Years", "₹55,000 per year"),
            ("BSc Computer Science", "12th standard with Mathematics", "3 Years", "₹65,000 per year")
        ]
        cursor.executemany(
            "INSERT INTO courses (name, eligibility, duration, fees) VALUES (%s, %s, %s, %s)",
            courses_data
        )

    db.commit()

# ---------------- CHATBOT LOGIC ---------------- #

def log_question(question):
    cursor.execute(
        "INSERT INTO logs (question, asked_on) VALUES (%s, %s)",
        (question, datetime.now())
    )
    db.commit()


def get_course_response(user_input):
    cursor.execute("SELECT name, eligibility, duration, fees FROM courses")
    courses = cursor.fetchall()

    for name, eligibility, duration, fees in courses:
        if any(word in user_input for word in name.lower().split()):
            return (
                f"Course: {name}\n"
                f"Eligibility: {eligibility}\n"
                f"Duration: {duration}\n"
                f"Fees: {fees}"
            )
    return None


def get_faq_response(user_input):
    cursor.execute("SELECT keywords, answer FROM faq")
    rows = cursor.fetchall()

    user_words = set(user_input.split())
    best_match = None
    max_matches = 0

    for keywords, answer in rows:
        key_words = set(keywords.split(","))
        matches = len(user_words & key_words)

        if matches > max_matches:
            max_matches = matches
            best_match = answer

    return best_match if max_matches > 0 else None


def get_response(user_input):
    log_question(user_input)

    if user_input in ["hi", "hello", "hey"]:
        return "Hello! How can I help you with admissions?"

    if user_input == "help":
        return (
            "You can ask about:\n"
            "- Courses offered\n"
            "- Eligibility\n"
            "- Fees\n"
            "- Hostel facilities\n"
            "- Admission deadline\n"
            "- Specific courses like BSc IT or BCA"
        )

    course_response = get_course_response(user_input)
    if course_response:
        return course_response

    faq_response = get_faq_response(user_input)
    if faq_response:
        return faq_response

    return (
        "Sorry, I couldn't understand your question.\n"
        "Please ask about courses, eligibility, fees, hostel, or deadline."
    )

# ---------------- MAIN CHAT LOOP ---------------- #

def start_chatbot():
    print("\n🎓 University Admission AI Chatbot (MySQL)")
    print("Type 'help' to see options")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ").lower().strip()

        if not user_input:
            print("Bot: Please enter a question.\n")
            continue

        if user_input == "exit":
            print("Bot: Thank you for contacting admissions.")
            break

        response = get_response(user_input)
        print("\nBot:", response, "\n")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    create_tables()
    insert_default_data()
    start_chatbot()
