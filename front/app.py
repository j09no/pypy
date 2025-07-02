import streamlit as st
import json

# Custom CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #1B1C1D;
    }

    .main-header {
        color: white;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
        padding: 20px 0;
    }

    .section-header {
        color: white;
        font-size: 22px;
        font-weight: bold;
        margin: 30px 0 20px 0;
        padding: 10px 0;
        border-bottom: 2px solid #4CAF50;
    }

    .question-text {
        color: white;
        font-size: 18px;
        font-weight: 500;
        margin: 20px 0 10px 0;
        line-height: 1.4;
    }

    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 2px 0 2px 12px !important;
        color: white !important;
        font-size: 16px !important;
        text-align: left !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        width: 100% !important;
        cursor: pointer !important;
        display: block !important;
        margin: 0 !important;
    }

    .stButton > button:hover {
        color: grey !important;
    }

    .stButton {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    .element-container {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    .answer-text {
        color: white;
        font-size: 16px;
        margin: 5px 0;
    }

    .json-input-container {
        background-color: #2D2E2F;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }

    .error-message {
        background-color: #3D1A1A;
        border: 2px solid #FF6B6B;
        border-radius: 8px;
        padding: 15px;
        color: #FF6B6B;
        margin: 10px 0;
    }

    .score-container {
        background-color: #2D2E2F;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        text-align: center;
    }

    .score-text {
        color: #4CAF50;
        font-size: 24px;
        font-weight: bold;
        margin: 5px 0;
    }

    .score-details {
        color: white;
        font-size: 14px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session cache init
if 'cached_json_data' not in st.session_state:
    st.session_state.cached_json_data = None
if 'cached_json_text' not in st.session_state:
    st.session_state.cached_json_text = ""

def parse_json_data(json_text):
    if (st.session_state.cached_json_text == json_text and
        st.session_state.cached_json_data is not None):
        return st.session_state.cached_json_data, None
    try:
        data = json.loads(json_text)
        st.session_state.cached_json_data = data
        st.session_state.cached_json_text = json_text
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON format: {str(e)}"

def display_question(question_data, question_index, section_key=""):
    question_key = f"{section_key}_q{question_index}"
    
    st.markdown(f'<div class="question-text">{question_index}. {question_data.get("question", "")}</div>', unsafe_allow_html=True)

    options = question_data.get("options", {})
    if isinstance(options, dict):
        for option_key, option_text in options.items():
            button_key = f"{question_key}_{option_key}"
            if st.button(f"({option_key})   {option_text}", key=button_key, use_container_width=True):
                st.session_state[f"selected_option_{question_key}"] = option_key
                st.session_state[f"show_answer_{question_key}"] = True
                st.session_state[f"pending_score_update_{question_key}"] = True
                st.rerun()

    answer = question_data.get("answer", "No answer provided")
    if st.session_state.get(f"show_answer_{question_key}", False):
        st.markdown(f'<div class="answer-text">Answer: {answer}</div>', unsafe_allow_html=True)

        # Update score once per question
        if st.session_state.get(f"pending_score_update_{question_key}", False):
            selected_option = st.session_state.get(f"selected_option_{question_key}")
            correct_option = None
            if answer.startswith("(") and ")" in answer:
                correct_option = answer[1:answer.index(")")]

            if "total_score" not in st.session_state:
                st.session_state["total_score"] = 0

            if selected_option == correct_option:
                st.session_state["total_score"] += 4
            else:
                st.session_state["total_score"] -= 1

            st.session_state[f"pending_score_update_{question_key}"] = False
    else:
        st.markdown('<div class="answer-text">Answer:</div>', unsafe_allow_html=True)

def count_total_questions(data):
    if not data:
        return 0
    total_questions = 0
    if "sections" in data and data["sections"]:
        for section in data["sections"]:
            if "questions" in section and section["questions"]:
                total_questions += len(section["questions"])
    elif "questions" in data and data["questions"]:
        total_questions = len(data["questions"])
    else:
        for key, value in data.items():
            if isinstance(value, dict) and ("question" in value or "options" in value):
                total_questions += 1
    return total_questions

def display_score_counter(total_questions):
    current_score = st.session_state.get("total_score", 0)
    max_possible_score = total_questions * 4
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f'''
        <div class="score-container">
            <div class="score-text">Score: {current_score}/{max_possible_score}</div>
            <div class="score-details">Current: {current_score} | Max Possible: {max_possible_score}</div>
            <div class="score-details">Total Questions: {total_questions} | +4 correct, -1 wrong</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        if st.button(" Reset Score", key="reset_score"):
            keys_to_remove = [key for key in st.session_state.keys()
                              if key.startswith(("show_answer_", "selected_option_", "score_updated_", "pending_score_update_"))]
            for key in keys_to_remove:
                del st.session_state[key]
            st.session_state["total_score"] = 0
            st.rerun()

def main():
    st.markdown('<div class="main-header">QP</div>', unsafe_allow_html=True)

    st.markdown('<div class="json-input-container">', unsafe_allow_html=True)
    st.subheader(" Paste JSON Data")

    json_input = st.text_area(
        "Paste your JSON data here:",
        height=200,
        placeholder=''''''
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if json_input.strip():
        parsed_data, error = parse_json_data(json_input)

        if error:
            st.markdown(f'<div class="error-message">q {error}</div>', unsafe_allow_html=True)
        else:
            total_questions = count_total_questions(parsed_data)
            if total_questions > 0:
                display_score_counter(total_questions)

            if parsed_data and "title" in parsed_data:
                st.markdown(f'<div class="main-header">{parsed_data["title"]}</div>', unsafe_allow_html=True)

            if "sections" in parsed_data:
                for section_index, section in enumerate(parsed_data["sections"]):
                    section_key = f"section_{section_index}"
                    if "heading" in section:
                        st.markdown(f'<div class="section-header">{section["heading"]}</div>', unsafe_allow_html=True)
                    questions = section.get("questions", [])
                    for q_index, question in enumerate(questions, 1):
                        display_question(question, q_index, section_key)
            elif "questions" in parsed_data:
                for q_index, question in enumerate(parsed_data["questions"], 1):
                    display_question(question, q_index)
            else:
                question_count = 1
                for key, value in parsed_data.items():
                    if isinstance(value, dict) and ("question" in value or "options" in value):
                        display_question(value, question_count)
                        question_count += 1
    else:
        st.info("""
        """)
        st.markdown("")
        

if __name__ == "__main__":
    main()
