import requests
import json


def is_nonsense(text):
    text = text.lower().strip()

    nonsense_patterns = [
        "asdf", "qwerty", "blah", "random text",
        "???", "!!!", "...."
    ]

    if len(text) < 2:
        return True

    if len(set(text)) == 1:
        return True

    return any(p in text for p in nonsense_patterns)


def is_greeting(text):
    greetings = ["hi", "hello", "hey", "hii", "heyy"]
    return text.lower().strip() in greetings

def is_career_related(text):
    text = text.lower()

    career_keywords = [
        "career", "job", "jobs", "future", "scope", "salary",
        "course", "degree", "study", "college", "bca", "btech",
        "engineering", "medical", "arts", "commerce",
        "profession", "roadmap", "internship", "placement",
        "software", "developer", "coding", "programming",
        "data", "analyst", "cloud", "network", "ai",
        "machine learning", "python", "web development",
        "cybersecurity", "it job", "computer"
    ]

    words = text.split()

    for keyword in career_keywords:
        if keyword in text:
            return True

        for word in words:
            if keyword.startswith(word) or word.startswith(keyword[:4]):
                return True

    return False
def fix_bca_answer(answer, question):
    q = question.lower()

    if "bca" in q:

        wrong_words = [
            "commerce", "finance", "banking",
            "accounting", "bcom",
            "bioinformatics", "pharmaceutical",
            "biotech", "genomics",
            "biology", "medical"
        ]

        if any(word in answer.lower() for word in wrong_words):

            return """
Here are some good career options for BCA students:

• Software Developer
  Build applications, websites, and software systems.

• Web Developer
  Create frontend and backend websites using web technologies.

• Data Analyst
  Analyze data using Python, SQL, Excel, and Power BI.

• Cloud / Network Engineer
  Work with cloud computing, networking, and cybersecurity.

• UI/UX Designer
  Design user-friendly interfaces and app experiences.

• System Administrator
  Manage servers, systems, and technical infrastructure.
"""

    return answer

def ask_ai(user_input):
    try :
        user_input = user_input.strip()

        if is_greeting(user_input):
            return "Hey! How can I help you today?"

        if is_nonsense(user_input):
            return "That doesn’t look like a clear question. Try asking something meaningful 🙂"
        if not is_career_related(user_input):
            return "I only answer career, course, and job-related questions 🙂"

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "phi3:mini",

                "prompt": f"""
        You are a career guidance assistant.

IMPORTANT:
If the question mentions BCA,
ONLY suggest computer science and IT careers.
Never suggest medical, biotech, pharmacy,
commerce, or biology-related careers.
        Rules:
        - Answer ONLY career, courses, jobs, skills, and study-related questions
        - Keep answers short and practical
        - Suggest careers clearly using bullet points
        - Avoid long introductions
        - If question is unrelated, say:
        'I only answer career-related questions.'

        Question: {user_input}

        Answer:
        """,
                "stream": False,
                "options": {
                    "num_predict": 300,
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_ctx": 1024
                }
            },
            timeout=60
        )

        json_data = response.json()
        answer = json_data.get("response", "")

        answer = answer.strip()

        answer = fix_bca_answer(answer, user_input)

        return answer

    except Exception as e:
        return f"Error: {str(e)}"