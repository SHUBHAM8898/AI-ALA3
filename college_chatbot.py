"""
College Helpdesk Chatbot (Improved Rule-Based Version)
Uses Python if/elif rules, keyword matching, and fuzzy matching for common typos.
No external packages are required.
Run: python college_chatbot.py
"""

import re
from difflib import SequenceMatcher

INTENTS = {
    "greeting": {
        "keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
        "response": "Hello! Welcome to the College Helpdesk. You can ask me about admissions, courses, fees, exams, attendance, library, scholarships, timetable, departments, certificates, hostel, transport, or contacts."
    },
    "admission": {
        "keywords": ["admission", "admissions", "apply", "application", "enroll", "enrollment", "eligibility", "documents required", "admission form"],
        "response": "For admission, check your college's official admission notice. Commonly required documents include previous marksheets, school leaving/transfer certificate, ID proof, photos, and category/income certificates if applicable. Requirements and deadlines vary, so confirm with the admission office."
    },
    "courses": {
        "keywords": ["course", "courses", "program", "programs", "branch", "degree", "diploma", "bachelor", "master", "syllabus", "subject"],
        "response": "Course availability and syllabus depend on the college and semester. Check the official prospectus or department page. If you tell me your course or semester, I can give general study guidance."
    },
    "fees": {
        "keywords": ["fee", "fees", "tuition", "payment", "pay fees", "installment", "refund", "receipt", "accounts"],
        "response": "For exact fees, due dates, instalments, refunds, or receipts, contact the college accounts office or check the official student portal. Never share passwords, OTPs, or full payment-card details in chat."
    },
    "exam": {
        "keywords": ["exam", "exams", "examination", "timetable", "date sheet", "hall ticket", "admit card", "result", "marksheet", "recheck", "revaluation", "backlog", "remedial"],
        "response": "For exam timetables, hall tickets, results, rechecking, and backlogs, use the official student/examination portal or contact the exam section. Confirm dates from official notices because they can change."
    },
    "attendance": {
        "keywords": ["attendance", "present", "absent", "attendance percentage", "shortage", "proxy"],
        "response": "Check your latest attendance in the student portal or with your faculty advisor. Attendance rules vary by institution and subject. If you share classes attended and total classes, I can calculate your percentage."
    },
    "library": {
        "keywords": ["library", "book", "books", "borrow", "issue book", "return book", "reading room"],
        "response": "The college library can help with textbooks, reference material, reading space, and book borrowing. Ask the librarian about opening hours, borrowing limits, renewals, and late fees."
    },
    "scholarship": {
        "keywords": ["scholarship", "financial aid", "stipend", "digital gujarat", "fee assistance", "grant"],
        "response": "Scholarship eligibility depends on scheme, income, category, course, and marks. Check the relevant official government/college scholarship portal and confirm deadlines with the scholarship cell. Keep your documents and bank details secure."
    },
    "hostel": {
        "keywords": ["hostel", "accommodation", "room", "mess", "warden"],
        "response": "For hostel availability, fees, rules, mess facilities, and application dates, contact the hostel office. Availability and charges vary by campus."
    },
    "transport": {
        "keywords": ["bus", "transport", "route", "college bus", "pickup", "drop", "parking"],
        "response": "For bus routes, pickup points, transport fees, parking, and schedules, contact the transport office or check the latest campus notice."
    },
    "timetable": {
        "keywords": ["class timing", "college timing", "timings", "time table", "schedule", "lecture", "period", "when does college start"],
        "response": "Class timings and timetables can differ by semester, division, and day. Please check the latest timetable shared by your department or student portal."
    },
    "faculty": {
        "keywords": ["faculty", "teacher", "professor", "hod", "department", "mentor", "advisor"],
        "response": "For faculty contact details, office hours, department information, or mentor assignments, use the official department page or ask your department office."
    },
    "certificate": {
        "keywords": ["certificate", "bonafide", "bonafide certificate", "leaving certificate", "transfer certificate", "transcript", "character certificate", "migration"],
        "response": "For bonafide, transfer/leaving, character, migration, or transcript requests, contact the student section/administration office. Ask about the application form, processing time, and any fee."
    },
    "placement": {
        "keywords": ["placement", "job", "career", "campus interview", "resume", "internship", "training"],
        "response": "For internships, campus placements, resume reviews, and interview training, contact the placement/career cell. Keep your resume updated and check official notices for eligibility and deadlines."
    },
    "wifi": {
        "keywords": ["wifi", "wi-fi", "internet", "network", "computer lab", "lab"],
        "response": "For campus Wi-Fi or lab access, contact the IT support team or lab assistant. Use only your own account and never share your password or OTP."
    },
    "contact": {
        "keywords": ["contact", "phone", "telephone", "email", "address", "location", "office number", "helpline"],
        "response": "For verified phone numbers, email addresses, and campus location, check the college's official website or student portal. I don't want to invent contact details."
    },
    "holiday": {
        "keywords": ["holiday", "vacation", "closed", "open today", "working day", "public holiday"],
        "response": "Please check the latest official college circular or academic calendar for holidays and campus closures. I don't have live access to your college notices."
    },
    "documents": {
        "keywords": ["documents", "document", "id card", "identity card", "lost id", "student id"],
        "response": "For document submission or a lost student ID, contact the student section. Keep scanned copies of important documents and follow the college's official replacement process."
    },
    "complaint": {
        "keywords": ["complaint", "grievance", "bullying", "harassment", "ragging", "problem", "issue"],
        "response": "For a college complaint, contact your faculty advisor, department head, student grievance cell, or the appropriate campus authority. If anyone is in immediate danger, contact local emergency services or a trusted responsible adult."
    },
    "thanks": {
        "keywords": ["thanks", "thank you", "thx", "thankyou"],
        "response": "You're welcome! I'm glad I could help."
    },
    "goodbye": {
        "keywords": ["bye", "goodbye", "exit", "quit", "see you"],
        "response": "Goodbye! Best wishes for your studies."
    },
    "help": {
        "keywords": ["help", "what can you do", "options", "topics", "menu"],
        "response": "I can help with: admissions, courses/syllabus, fees, exams/results, attendance calculations, library, scholarships, hostel, transport, timetable, faculty, certificates, placements, Wi-Fi/labs, contacts, holidays, documents, and complaints."
    },
}

def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s%-]", " ", text)
    return re.sub(r"\s+", " ", text)

def score_intent(message, keywords):
    """Return a score based on exact phrase and fuzzy similarity."""
    best = 0.0
    padded = f" {message} "
    for keyword in keywords:
        k = normalize(keyword)
        if k and f" {k} " in padded:
            best = max(best, 1.0 + len(k) / 1000)
        elif k and (k in message or message in k):
            best = max(best, 0.82)
        else:
            # Fuzzy matching helps with small spelling errors in short keywords.
            ratio = SequenceMatcher(None, message, k).ratio()
            if len(message) >= 4 and len(k) >= 4 and ratio >= 0.78:
                best = max(best, ratio * 0.8)
    return best

def get_response(user_input):
    message = normalize(user_input)
    if not message:
        return "Please type a question. Type 'help' to see the topics I support."

    # Direct rule-based checks first.
    for intent in ("greeting", "thanks", "goodbye", "help"):
        if score_intent(message, INTENTS[intent]["keywords"]) >= 0.8:
            return INTENTS[intent]["response"]

    best_intent, best_score = None, 0
    for intent, data in INTENTS.items():
        if intent in {"greeting", "thanks", "goodbye", "help"}:
            continue
        score = score_intent(message, data["keywords"])
        if score > best_score:
            best_intent, best_score = intent, score

    if best_intent and best_score >= 0.62:
        return INTENTS[best_intent]["response"]

    return ("I couldn't confidently match that question to my rules. Try rephrasing it or type 'help'. "
            "I can answer common college-helpdesk questions, but I don't have live college records or real-time notices.")

def main():
    print("=" * 64)
    print("             COLLEGE HELPDESK CHATBOT")
    print(" Rule-based Python chatbot | type 'help' for topics")
    print(" Type 'bye' to end.")
    print("=" * 64)
    while True:
        try:
            user_input = input("\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break
        response = get_response(user_input)
        print("Bot:", response)
        if normalize(user_input) in {"bye", "goodbye", "exit", "quit", "see you"}:
            break

if __name__ == "__main__":
    main()
