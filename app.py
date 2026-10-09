import os
import json
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from dotenv import load_dotenv
from groq import Groq
from rag_engine import ask_rag



# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Groq API key not found. Please check your .env file.")
    st.stop()

client = Groq(api_key=api_key)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GenVI Learning",
    page_icon="🎓",
    layout="wide"
)
# =========================================================
# GENVI PROFESSIONAL UI
# =========================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 20% 20%, rgba(126, 34, 206, 0.30), transparent 35%),
        radial-gradient(circle at 80% 10%, rgba(168, 85, 247, 0.22), transparent 30%),
        radial-gradient(circle at 70% 80%, rgba(88, 28, 135, 0.25), transparent 35%),
        linear-gradient(135deg, #050507 0%, #0b0612 45%, #160b24 100%);
}

.block-container {
    padding-top: 2rem;s
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1 {
    font-size: 3.2rem !important;
    font-weight: 800 !important;
}

h2, h3 {
    font-weight: 700 !important;
}

p, label {
    color: #dbeafe !important;
}

textarea {
    background: rgba(255,255,255,0.06) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
}

.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
}

[data-testid="stAlert"] {
    border-radius: 14px !important;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

div[role="radiogroup"] {
    background: rgba(255,255,255,0.03);
    padding: 12px;
    border-radius: 12px;
}

hr {
    border-color: rgba(255,255,255,0.10) !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CUSTOM TITLE
# =========================================================

st.title("🎓 GenVI Learning")

st.subheader("Your Personalized AI Study Coach")

st.write(
    "Ask questions, understand difficult concepts, "
    "create study plans, and improve your weak areas."
)


# =========================================================
# SIDEBAR - STUDENT PROFILE
# =========================================================

st.sidebar.header("👩‍🎓 Student Profile")

level = st.sidebar.selectbox(
    "Your Level",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)

learning_style = st.sidebar.selectbox(
    "Learning Style",
    [
        "Simple Explanation",
        "Examples Based",
        "Step-by-Step",
        "Exam Focused"
    ]
)

subject = st.sidebar.selectbox(
    "📚 Current Subject",
    [
        "Operating System",
        "Data Structures & Algorithms",
        "DBMS",
        "Computer Networks",
        "Computer Organization & Architecture",
        "OOPs",
        "Java",
        "Python",
        "C Programming",
        "C++",
        "Software Engineering",
        "Artificial Intelligence",
        "Machine Learning",
        "Cyber Security",
        "Web Development",
        "Cloud Computing",
        "Discrete Mathematics",
        "Theory of Computation",
        "Compiler Design"
    ]
)
# =========================================================
# NAVIGATION
# =========================================================

page = st.sidebar.radio(
    "📌 Menu",
    [
        "AI Mentor",
        "Study Planner",
        "Quiz",
        "Progress",
        "My Notes",
        "Settings",
        "Logout"
    ]
)
# =========================================================
# PAGE NAVIGATION
# =========================================================

if page == "Study Planner":
    st.title("📅 Study Planner")

    task = st.text_input("Enter study task")
    study_date = st.date_input("Select date")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

    if st.button("➕ Add Task"):
        if task.strip():
            if "tasks" not in st.session_state:
                st.session_state.tasks = []

            st.session_state.tasks.append({
                "task": task,
                "date": str(study_date),
                "priority": priority,
                "done": False
            })

            st.success("Task added!")
        else:
            st.warning("Enter a task first.")

    if "tasks" in st.session_state:
        st.subheader("📋 Your Tasks")

        for i, item in enumerate(st.session_state.tasks):

            done = st.checkbox(
                item["task"],
                value=item["done"],
                key=f"done_{i}"
            )

            st.session_state.tasks[i]["done"] = done

            st.caption(
                f"Date: {item['date']} | Priority: {item['priority']}"
            )

    st.stop()




# =========================================================
# USER QUESTION
# =========================================================

st.header("💬 Ask Your Mentor")

question = st.text_area(
    "What do you want to learn?",
    placeholder="Example: Explain process scheduling in Operating System.",
    height=120
)


# =========================================================
# ASK AI MENTOR
# =========================================================

if st.button("🚀 Ask AI Mentor"):

    if not question.strip():

        st.warning("Please enter a question first.")

    else:

        system_prompt = f"""
You are an intelligent, patient and friendly AI Learning Mentor
for B.Tech Computer Science students.

Student Level: {level}

Learning Style: {learning_style}

Subject: {subject}

Your job is to explain the student's question clearly.

Follow these rules:

1. Explain the concept according to the student's level.
2. Use simple language.
3. Give examples whenever useful.
4. Use headings and bullet points.
5. If the topic contains steps, explain them step-by-step.
6. If the concept can be understood better using a diagram,
   flowchart, architecture diagram, timeline, tree,
   process diagram, network diagram or hierarchy,
   identify that a visual is useful.

At the VERY END of your response write exactly:

VISUAL_NEEDED: YES or NO
VISUAL_TYPE: short description

Examples:

VISUAL_NEEDED: YES
VISUAL_TYPE: Class inheritance hierarchy diagram

OR

VISUAL_NEEDED: YES
VISUAL_TYPE: CPU scheduling flow diagram

OR

VISUAL_NEEDED: NO
VISUAL_TYPE: None

Do not write anything after these two lines.
"""

        with st.spinner("🧠 Your AI Mentor is thinking..."):

            answer = ask_rag(
                question,
                level,
                learning_style,
                subject
            )

        # Save answer so it stays available
        st.session_state["answer"] = answer

        st.success("✨ Here's your personalized explanation:")
        # -------------------------------------------------
        # REMOVE VISUAL INSTRUCTIONS FROM VISIBLE ANSWER
        # -------------------------------------------------

        clean_answer = answer

        if "VISUAL_NEEDED:" in clean_answer:

            clean_answer = clean_answer.split(
                "VISUAL_NEEDED:",
                1
            )[0].strip()

        st.markdown(clean_answer)


# ==========================================
# VISUAL LEARNING + RAG SOURCE
# ==========================================

if "answer" in st.session_state:

    answer = st.session_state["answer"]

    
    # -------------------------------
    # CHECK VISUAL REQUIREMENT
    # -------------------------------

    visual_needed = "VISUAL_NEEDED: YES" in answer.upper()

    visual_type = "educational diagram"

    if "VISUAL_TYPE:" in answer:

        visual_type = (
            answer.split("VISUAL_TYPE:", 1)[1]
            .split("\n")[0]
            .strip()
        )

    # -------------------------------
    # CREATE VISUAL
    # -------------------------------

    if visual_needed:

        st.subheader("🖼️ Visual Learning")

        

        # STACK
        if "stack" in visual_type.lower():

            fig, ax = plt.subplots(figsize=(8, 5))

            values = ["10", "20", "30"]

            for i, value in enumerate(values):

                ax.add_patch(
                    plt.Rectangle(
                        (0, i),
                        3,
                        0.8,
                        fill=False,
                        linewidth=2
                    )
                )

                ax.text(
                    1.5,
                    i + 0.4,
                    value,
                    ha="center",
                    va="center",
                    fontsize=16
                )

            ax.text(
                1.5,
                3.2,
                "TOP",
                ha="center",
                fontsize=14
            )

            ax.annotate(
                "PUSH",
                xy=(3, 2.4),
                xytext=(5, 2.4),
                arrowprops=dict(arrowstyle="->"),
                fontsize=13
            )

            ax.annotate(
                "POP",
                xy=(3, 2.0),
                xytext=(5, 1.2),
                arrowprops=dict(arrowstyle="->"),
                fontsize=13
            )

            ax.text(
                1.5,
                -0.5,
                "LIFO - Last In, First Out",
                ha="center",
                fontsize=13
            )

            ax.set_xlim(-1, 6)
            ax.set_ylim(-1, 4)
            ax.axis("off")

            st.pyplot(fig)

            st.caption(
                "Stack showing PUSH, POP and TOP operations."
            )

        # CPU SCHEDULING
        elif "scheduling" in visual_type.lower():

            fig, ax = plt.subplots(figsize=(9, 3))

            processes = ["P1", "P2", "P3", "P4"]
            start = [0, 2, 5, 7]
            duration = [2, 3, 2, 3]

            for i in range(len(processes)):

                ax.barh(
                    0,
                    duration[i],
                    left=start[i],
                    height=0.5
                )

                ax.text(
                    start[i] + duration[i] / 2,
                    0,
                    processes[i],
                    ha="center",
                    va="center"
                )

            ax.set_title("CPU Process Scheduling")
            ax.set_xlabel("CPU Time")
            ax.set_yticks([])

            st.pyplot(fig)

            st.caption(
                "Example Gantt chart for CPU process scheduling."
            )

        # LINKED LIST
        elif "linked list" in visual_type.lower():

            fig, ax = plt.subplots(figsize=(10, 3))

            nodes = ["10", "20", "30", "40"]

            for i, node in enumerate(nodes):

                ax.add_patch(
                    plt.Rectangle(
                        (i * 2, 0),
                        1.2,
                        0.8,
                        fill=False,
                        linewidth=2
                    )
                )

                ax.text(
                    i * 2 + 0.6,
                    0.4,
                    node,
                    ha="center",
                    va="center",
                    fontsize=14
                )

                if i < len(nodes) - 1:

                    ax.annotate(
                        "",
                        xy=(i * 2 + 2, 0.4),
                        xytext=(i * 2 + 1.2, 0.4),
                        arrowprops=dict(arrowstyle="->")
                    )

            ax.text(
                0,
                1.1,
                "HEAD",
                fontsize=12
            )

            ax.axis("off")

            st.pyplot(fig)

            st.caption(
                "Linked List showing nodes and connections."
            )

        # GENERIC VISUAL
        else:

            fig, ax = plt.subplots(figsize=(9, 3))

            steps = [
                "Concept",
                "Understand",
                "Apply",
                "Practice"
            ]

            for i, step in enumerate(steps):

                ax.add_patch(
                    plt.Rectangle(
                        (i * 2, 0),
                        1.5,
                        0.8,
                        fill=False,
                        linewidth=2
                    )
                )

                ax.text(
                    i * 2 + 0.75,
                    0.4,
                    step,
                    ha="center",
                    va="center"
                )

                if i < len(steps) - 1:

                    ax.annotate(
                        "",
                        xy=(i * 2 + 2, 0.4),
                        xytext=(i * 2 + 1.5, 0.4),
                        arrowprops=dict(arrowstyle="->")
                    )

            ax.axis("off")

            st.pyplot(fig)

            st.caption(
                "Concept → Understand → Apply → Practice"
            )
    answer = st.session_state["answer"]

    visual_needed = (
        "VISUAL_NEEDED: YES" in answer.upper()
    )

    visual_type = "educational diagram"

    if "VISUAL_TYPE:" in answer:

        visual_type = (
            answer.split(
                "VISUAL_TYPE:",
                1
            )[1]
            .split("\n")[0]
            .strip()
        )


    # =====================================================
    # CREATE VISUAL
    # =====================================================

    if visual_needed:

    

        st.info(
            "💡 This concept can be understood better with a visual: "
            + visual_type
        )

        fig, ax = plt.subplots(
            figsize=(10, 5)
        )

        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)

        ax.axis("off")


        # =================================================
        # CLASS INHERITANCE
        # =================================================

        if (
            "inheritance" in visual_type.lower()
            or "class hierarchy" in visual_type.lower()
        ):

            parent = FancyBboxPatch(
                (4, 4),
                2,
                1,
                boxstyle="round,pad=0.05",
                linewidth=2
            )

            dog = FancyBboxPatch(
                (1.5, 1.5),
                2,
                1,
                boxstyle="round,pad=0.05",
                linewidth=2
            )

            cat = FancyBboxPatch(
                (6.5, 1.5),
                2,
                1,
                boxstyle="round,pad=0.05",
                linewidth=2
            )

            ax.add_patch(parent)
            ax.add_patch(dog)
            ax.add_patch(cat)

            ax.text(
                5,
                4.5,
                "Animal\nParent Class",
                ha="center",
                va="center",
                fontsize=12,
                fontweight="bold"
            )

            ax.text(
                2.5,
                2,
                "Dog\nChild Class",
                ha="center",
                va="center",
                fontsize=12,
                fontweight="bold"
            )

            ax.text(
                7.5,
                2,
                "Cat\nChild Class",
                ha="center",
                va="center",
                fontsize=12,
                fontweight="bold"
            )

            ax.annotate(
                "",
                xy=(2.5, 2.5),
                xytext=(4.4, 4),
                arrowprops=dict(
                    arrowstyle="->",
                    linewidth=2
                )
            )

            ax.annotate(
                "",
                xy=(7.5, 2.5),
                xytext=(5.6, 4),
                arrowprops=dict(
                    arrowstyle="->",
                    linewidth=2
                )
            )

            ax.text(
                5,
                5.5,
                "Class Inheritance Hierarchy",
                ha="center",
                fontsize=16,
                fontweight="bold"
            )


        # =================================================
        # CPU SCHEDULING
        # =================================================

        elif (
            "scheduling" in visual_type.lower()
            or "gantt" in visual_type.lower()
        ):

            labels = [
                "Ready Queue",
                "Scheduler",
                "CPU",
                "Running Process"
            ]

            positions = [
                0.5,
                3,
                5.5,
                8
            ]

            for i in range(len(labels)):

                box = FancyBboxPatch(
                    (
                        positions[i],
                        2.5
                    ),
                    1.5,
                    1,
                    boxstyle="round,pad=0.05",
                    linewidth=2
                )

                ax.add_patch(box)

                ax.text(
                    positions[i] + 0.75,
                    3,
                    labels[i],
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold"
                )

                if i < len(labels) - 1:

                    ax.annotate(
                        "",
                        xy=(
                            positions[i + 1],
                            3
                        ),
                        xytext=(
                            positions[i] + 1.5,
                            3
                        ),
                        arrowprops=dict(
                            arrowstyle="->",
                            linewidth=2
                        )
                    )

            ax.text(
                5,
                5.3,
                "CPU Process Scheduling",
                ha="center",
                fontsize=16,
                fontweight="bold"
            )


        # =================================================
        # PROCESS STATES
        # =================================================

        elif (
            "process state" in visual_type.lower()
            or "state transition" in visual_type.lower()
        ):

            states = [
                (0.5, 3, "NEW"),
                (2.7, 3, "READY"),
                (4.9, 3, "RUNNING"),
                (7.1, 4.2, "WAITING"),
                (7.1, 1.8, "TERMINATED")
            ]

            for x, y, label in states:

                box = FancyBboxPatch(
                    (x, y),
                    1.6,
                    0.8,
                    boxstyle="round,pad=0.05",
                    linewidth=2
                )

                ax.add_patch(box)

                ax.text(
                    x + 0.8,
                    y + 0.4,
                    label,
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold"
                )


            ax.annotate(
                "",
                xy=(2.7, 3.4),
                xytext=(2.1, 3.4),
                arrowprops=dict(
                    arrowstyle="->",
                    linewidth=2
                )
            )

            ax.annotate(
                "",
                xy=(4.9, 3.4),
                xytext=(4.3, 3.4),
                arrowprops=dict(
                    arrowstyle="->",
                    linewidth=2
                )
            )

            ax.annotate(
                "",
                xy=(7.1, 4.6),
                xytext=(6.5, 3.7),
                arrowprops=dict(
                    arrowstyle="->",
                    linewidth=2
                )
            )

            ax.annotate(
                "",
                xy=(7.1, 2.2),
                xytext=(6.5, 3.1),
                arrowprops=dict(
                    arrowstyle="->",
                    linewidth=2
                )
            )

            ax.text(
                5,
                5.5,
                "Process State Transition",
                ha="center",
                fontsize=16,
                fontweight="bold"
            )


        # =================================================
        # NETWORK DIAGRAM
        # =================================================

        elif "network" in visual_type.lower():

            nodes = [
                (1.5, 3, "Computer"),
                (5, 3, "Router"),
                (8.5, 3, "Server")
            ]

            for x, y, label in nodes:

                circle = plt.Circle(
                    (x, y),
                    0.8,
                    fill=False,
                    linewidth=2
                )

                ax.add_patch(circle)

                ax.text(
                    x,
                    y,
                    label,
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold"
                )


            ax.annotate(
                "",
                xy=(4.2, 3),
                xytext=(2.3, 3),
                arrowprops=dict(
                    arrowstyle="<->",
                    linewidth=2
                )
            )

            ax.annotate(
                "",
                xy=(7.7, 3),
                xytext=(5.8, 3),
                arrowprops=dict(
                    arrowstyle="<->",
                    linewidth=2
                )
            )

            ax.text(
                5,
                5.3,
                "Basic Network Communication",
                ha="center",
                fontsize=16,
                fontweight="bold"
            )




# =========================================================
# QUIZ
# =========================================================

st.divider()

st.subheader("🧠 Test Your Understanding")

st.write(
    "Let's check how well you understood this concept."
)


if st.button("🎯 Generate Quick Quiz"):

    if not question.strip():

        st.warning(
            "Please ask a question first so I can create a quiz."
        )

    else:

        with st.spinner(
            "💭 Creating your personalized quiz..."
        ):

            quiz_response = client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=[

                    {
                        "role": "system",

                        "content": """
You are an expert B.Tech Computer Science quiz generator.

Create exactly 5 multiple-choice questions.

Requirements:

- Exactly 5 questions.
- Exactly 4 options per question.
- Include correct answer.
- Include short explanation.
- Match student's level.
- Mix easy, medium and conceptual questions.
- correct_answer must exactly match one option.
- Return ONLY valid JSON.

JSON format:

{
    "questions": [
        {
            "question": "Question text",
            "options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ],
            "correct_answer": "Option 1",
            "explanation": "Short explanation"
        }
    ]
}
"""
                    },

                    {
                        "role": "user",

                        "content": (
                            "Create a quiz based on:\n\n"
                            "Subject: " + subject + "\n"
                            "Student Level: " + level + "\n"
                            "Learning Style: " + learning_style + "\n"
                            "Topic/Question: " + question
                        )
                    }
                ],

                response_format={
                    "type": "json_object"
                },

                temperature=0.5,

                max_tokens=2000
            )


        quiz_data = json.loads(
            quiz_response.choices[0].message.content
        )

        st.session_state["quiz_data"] = quiz_data
        # -----------------------------
# LEARNING PROGRESS
# -----------------------------

if "quiz_scores" not in st.session_state:
    st.session_state["quiz_scores"] = []


# =========================================================
# DISPLAY QUIZ
# =========================================================

if "quiz_data" in st.session_state:

    quiz_data = st.session_state["quiz_data"]

    st.success(
        "🎉 Your personalized quiz is ready!"
    )

    questions = quiz_data["questions"]


    for i, q in enumerate(questions):

        st.markdown(
            f"### Question {i + 1}"
        )

        st.write(
            q["question"]
        )

        st.radio(
            "Choose your answer:",

            q["options"],

            index=None,

            key=f"quiz_answer_{i}"
        )


    # =====================================================
    # SUBMIT QUIZ
    # =====================================================

    if st.button("✅ Submit Quiz"):

        score = 0

        for i, q in enumerate(questions):

            selected = st.session_state.get(
                f"quiz_answer_{i}"
            )

            if selected == q["correct_answer"]:

                score += 1


        st.success(
            f"🏆 Your Score: {score} / {len(questions)}"
        )
        # Save score for progress tracking
        st.session_state["quiz_scores"].append({
            "score": score,
            "total": len(questions),
            "subject": subject
        })

        st.divider()

        st.subheader(
            "📝 Answer Review"
        )


        for i, q in enumerate(questions):

            selected = st.session_state.get(
                f"quiz_answer_{i}"
            )

            st.markdown(
                f"**Question {i + 1}: {q['question']}**"
            )

            st.write(
                f"Your answer: {selected}"
            )

            st.write(
                f"Correct answer: {q['correct_answer']}"
            )

            st.info(
                q["explanation"]
            )
            # -----------------------------
# PROGRESS DASHBOARD
# -----------------------------

st.divider()

st.header("📊 My Learning Progress")
st.write("Track your quiz performance and see how you're improving.")

scores = st.session_state.get("quiz_scores", [])

if scores:

    total_attempts = len(scores)

    total_score = sum(item["score"] for item in scores)
    total_questions = sum(item["total"] for item in scores)

    accuracy = (total_score / total_questions) * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🎯 Quizzes Attempted",
            total_attempts
        )

    with col2:
        st.metric(
            "⭐ Average Accuracy",
            f"{accuracy:.1f}%"
        )

    with col3:
        st.metric(
            "🏆 Total Score",
            f"{total_score}/{total_questions}"
        )

    st.subheader("📈 Quiz Performance")

    chart_data = {
        "Quiz": [
            f"Quiz {i + 1}"
            for i in range(total_attempts)
        ],
        "Score (%)": [
            (item["score"] / item["total"]) * 100
            for item in scores
        ]
    }

    st.line_chart(
        data=chart_data,
        x="Quiz",
        y="Score (%)"
    )

    st.subheader("📚 Subject-wise Attempts")

    for item in scores:
        percentage = (item["score"] / item["total"]) * 100

        st.write(
            f"**{item['subject']}** — "
            f"{item['score']}/{item['total']} "
            f"({percentage:.0f}%)"
        )

else:

    st.info(
        "📝 Complete your first quiz to start tracking your progress!"
    )
