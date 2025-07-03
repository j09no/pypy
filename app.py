import streamlit as st
import json
import uuid
from supabase import create_client
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://bowbamuzpsomopkbzoso.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJvd2JhbXV6cHNvbW9wa2J6b3NvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1MTczNTAsImV4cCI6MjA2NzA5MzM1MH0.MDzmRISVp7Eyg6gwuKVEn2E-MfR-nWe7E27Q5IhtJHA"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

    .answer-text {
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

    /* File Manager Styles */
    .file-manager-header {
        color: #4CAF50;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #4CAF50;
    }

    .folder-item {
        background-color: #3D3E3F;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        border-left: 3px solid #4CAF50;
        cursor: pointer;
        color: white;
    }

    .file-item {
        background-color: #404142;
        padding: 8px;
        margin: 3px 0;
        border-radius: 3px;
        border-left: 2px solid #FFA726;
        cursor: pointer;
        color: white;
        font-size: 14px;
    }

    .breadcrumb {
        color: #4CAF50;
        font-size: 14px;
        margin-bottom: 15px;
        padding: 5px 0;
        border-bottom: 1px solid #555;
    }

    .stTextInput > div > div > input {
        background-color: #404142 !important;
        color: white !important;
        border: 1px solid #555 !important;
    }

    .stTextArea > div > div > textarea {
        background-color: #404142 !important;
        color: white !important;
        border: 1px solid #555 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'cached_json_data' not in st.session_state:
    st.session_state.cached_json_data = None
if 'cached_json_text' not in st.session_state:
    st.session_state.cached_json_text = ""
if 'show_file_manager' not in st.session_state:
    st.session_state.show_file_manager = False
if 'current_folder_id' not in st.session_state:
    st.session_state.current_folder_id = None
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = []
if 'quiz_source' not in st.session_state:
    st.session_state.quiz_source = "paste"  # "paste" or "file"
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None

# Supabase Functions
def create_folder(name, parent_id=None):
    """Create a new folder in Supabase"""
    try:
        folder_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "parent_id": parent_id,
            "created_at": datetime.now().isoformat()
        }
        result = supabase.table("folders").insert(folder_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error creating folder: {str(e)}")
        return None

def upload_file_to_supabase(name, content, folder_id=None):
    """Upload file to Supabase"""
    try:
        file_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "folder_id": folder_id,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        result = supabase.table("files").insert(file_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return None

def get_folders(parent_id=None):
    """Get folders from Supabase"""
    try:
        if parent_id is None:
            result = supabase.table("folders").select("*").is_("parent_id", None).order("name").execute()
        else:
            result = supabase.table("folders").select("*").eq("parent_id", parent_id).order("name").execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Error fetching folders: {str(e)}")
        return []

def get_files(folder_id=None):
    """Get files from Supabase"""
    try:
        if folder_id is None:
            result = supabase.table("files").select("*").is_("folder_id", None).order("name").execute()
        else:
            result = supabase.table("files").select("*").eq("folder_id", folder_id).order("name").execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Error fetching files: {str(e)}")
        return []

def delete_file(file_id):
    """Delete file from Supabase"""
    try:
        result = supabase.table("files").delete().eq("id", file_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")
        return False

def delete_folder(folder_id):
    """Delete folder from Supabase"""
    try:
        result = supabase.table("folders").delete().eq("id", folder_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting folder: {str(e)}")
        return False

def get_all_files():
    """Get all files from all folders for quiz selection"""
    try:
        result = supabase.table("files").select("*").order("name").execute()
        return result.data if result.data else []
    except Exception as e:
        st.error(f"Error fetching files: {str(e)}")
        return []

# File Manager Functions
def render_file_manager():
    """File manager with Supabase integration"""
    if not st.session_state.show_file_manager:
        return
    
    with st.sidebar:
        st.markdown('<div class="file-manager-header">📁 File Manager</div>', unsafe_allow_html=True)
        
        # Breadcrumb navigation
        breadcrumb = "Root"
        if st.session_state.folder_path:
            breadcrumb = " > ".join([folder['name'] for folder in st.session_state.folder_path])
        st.markdown(f'<div class="breadcrumb">📍 {breadcrumb}</div>', unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Root", key="nav_root"):
                st.session_state.current_folder_id = None
                st.session_state.folder_path = []
                st.rerun()
        
        with col2:
            if st.session_state.folder_path and st.button("⬆️ Back", key="nav_back"):
                st.session_state.folder_path.pop()
                st.session_state.current_folder_id = st.session_state.folder_path[-1]['id'] if st.session_state.folder_path else None
                st.rerun()
        
        st.markdown("---")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📁 New Folder", key="new_folder_btn"):
                st.session_state.show_new_folder_input = True
        
        with col2:
            if st.button("📤 Upload File", key="upload_file_btn"):
                st.session_state.show_upload_input = True
        
        # New folder input
        if hasattr(st.session_state, 'show_new_folder_input') and st.session_state.show_new_folder_input:
            folder_name = st.text_input("Folder Name:", key="new_folder_name")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create", key="create_folder"):
                    if folder_name.strip():
                        result = create_folder(folder_name.strip(), st.session_state.current_folder_id)
                        if result:
                            st.session_state.show_new_folder_input = False
                            st.success(f"Folder '{folder_name}' created!")
                            st.rerun()
            with col2:
                if st.button("Cancel", key="cancel_folder"):
                    st.session_state.show_new_folder_input = False
                    st.rerun()
        
        # File upload input
        if hasattr(st.session_state, 'show_upload_input') and st.session_state.show_upload_input:
            uploaded_file = st.file_uploader("Choose a file", key="file_uploader")
            if uploaded_file is not None:
                file_content = uploaded_file.read().decode('utf-8')
                result = upload_file_to_supabase(uploaded_file.name, file_content, st.session_state.current_folder_id)
                if result:
                    st.session_state.show_upload_input = False
                    st.success(f"File '{uploaded_file.name}' uploaded!")
                    st.rerun()
            
            if st.button("Cancel Upload", key="cancel_upload"):
                st.session_state.show_upload_input = False
                st.rerun()
        
        st.markdown("---")
        
        # Display folders and files from Supabase
        folders = get_folders(st.session_state.current_folder_id)
        files = get_files(st.session_state.current_folder_id)
        
        # Folders
        if folders:
            st.markdown("**📁 Folders:**")
            for folder in folders:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"📁 {folder['name']}", key=f"folder_{folder['id']}"):
                        st.session_state.current_folder_id = folder['id']
                        st.session_state.folder_path.append(folder)
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_folder_{folder['id']}", help="Delete folder"):
                        if delete_folder(folder['id']):
                            st.success(f"Folder '{folder['name']}' deleted!")
                            st.rerun()
        
        # Files
        if files:
            st.markdown("**📄 Files:**")
            for file in files:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"📄 {file['name']}")
                with col2:
                    if st.button("🗑️", key=f"delete_file_{file['id']}", help="Delete file"):
                        if delete_file(file['id']):
                            st.success(f"File '{file['name']}' deleted!")
                            st.rerun()
        
        if not folders and not files:
            st.info("No files or folders yet. Create a folder or upload a file!")
        
        # Close button
        if st.button("❌ Close", key="close_file_manager"):
            st.session_state.show_file_manager = False
            st.rerun()

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

# ✅ Updated function
def display_question(question_data, question_index, section_key=""):
    question_key = f"{section_key}_q{question_index}"

    st.markdown(f'<div class="question-text">{question_index}. {question_data.get("question", "")}</div>', unsafe_allow_html=True)

    options = question_data.get("options", {})
    answer = question_data.get("answer", "No answer provided")

    # Extract correct option key
    correct_option = None
    if answer.startswith("(") and ")" in answer:
        correct_option = answer[1:answer.index(")")]

    selected_option = st.session_state.get(f"selected_option_{question_key}", None)
    show_answer = st.session_state.get(f"show_answer_{question_key}", False)

    # Show buttons if answer not revealed
    if not show_answer:
        for option_key, option_text in options.items():
            button_key = f"{question_key}_{option_key}"
            if st.button(f"({option_key})   {option_text}", key=button_key, use_container_width=True):
                st.session_state[f"selected_option_{question_key}"] = option_key
                st.session_state[f"show_answer_{question_key}"] = True
                st.session_state[f"pending_score_update_{question_key}"] = True
                st.rerun()
    else:
        # Show options as plain text (no color)
        for option_key, option_text in options.items():
            st.markdown(
                f'<div class="answer-text" style="color: white;">({option_key}) {option_text}</div>',
                unsafe_allow_html=True
            )

    # Show colored answer
    if show_answer:
        color = "#4CAF50" if selected_option == correct_option else "#FF6B6B"
        st.markdown(
            f'<div class="answer-text" style="color: {color};">Answer: {answer}</div>',
            unsafe_allow_html=True
        )

        # Score update
        if st.session_state.get(f"pending_score_update_{question_key}", False):
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
    
    # Handle list data structure
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and ("question" in item or "options" in item):
                total_questions += 1
        return total_questions
    
    # Handle dictionary data structure
    if isinstance(data, dict):
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
    # File Manager Button in top right
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("📁 Files", key="toggle_file_manager"):
            st.session_state.show_file_manager = not st.session_state.show_file_manager
            st.rerun()
    
    # Render file manager if active
    render_file_manager()
    
    # Main quiz interface
    st.markdown('<div class="main-header">QP</div>', unsafe_allow_html=True)

    # Quiz source selection
    col1, col2 = st.columns([1, 1])
    with col1:
        quiz_source = st.radio(
            "Choose Quiz Source:",
            ["📄 Select from Uploaded Files", "✏️ Paste JSON Code"],
            key="quiz_source_radio"
        )
    
    # Update session state based on selection
    if "Select from Uploaded" in quiz_source:
        st.session_state.quiz_source = "file"
    else:
        st.session_state.quiz_source = "paste"

    st.markdown('<div class="json-input-container">', unsafe_allow_html=True)
    
    json_input = ""
    
    if st.session_state.quiz_source == "file":
        # File selection mode
        st.subheader("")
        all_files = get_all_files()
        
        if all_files:
            file_options = ["Select a file..."] + [f"{file['name']}" for file in all_files]
            selected_file_name = st.selectbox(
                "Choose a quiz file:",
                options=file_options,
                key="file_selector"
            )
            
            if selected_file_name != "Select a file...":
                # Find the selected file and get its content
                selected_file = next((f for f in all_files if f['name'] == selected_file_name), None)
                if selected_file:
                    st.session_state.selected_file = selected_file
                    json_input = selected_file.get('content', '')
                    st.info(f"📄 Using content from: {selected_file_name}")
        else:
            st.warning("No files found! Upload some quiz files first using the Files button.")
    
    else:
        # Manual JSON input mode
        st.subheader("")
        json_input = st.text_area(
            "Paste your JSON data here:",
            height=200,
            placeholder='Paste your quiz JSON data here...'
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

            # Handle title if present (only for dict structure)
            if isinstance(parsed_data, dict) and "title" in parsed_data:
                st.markdown(f'<div class="main-header">{parsed_data["title"]}</div>', unsafe_allow_html=True)

            # Handle different JSON structures
            if isinstance(parsed_data, list):
                # Direct list of questions
                for q_index, question in enumerate(parsed_data, 1):
                    if isinstance(question, dict) and ("question" in question or "options" in question):
                        display_question(question, q_index)
            elif isinstance(parsed_data, dict):
                if "sections" in parsed_data and parsed_data["sections"]:
                    for section_index, section in enumerate(parsed_data["sections"]):
                        section_key = f"section_{section_index}"
                        if "heading" in section:
                            st.markdown(f'<div class="section-header">{section["heading"]}</div>', unsafe_allow_html=True)
                        questions = section.get("questions", [])
                        for q_index, question in enumerate(questions, 1):
                            display_question(question, q_index, section_key)
                elif "questions" in parsed_data and parsed_data["questions"]:
                    for q_index, question in enumerate(parsed_data["questions"], 1):
                        display_question(question, q_index)
                else:
                    question_count = 1
                    for key, value in parsed_data.items():
                        if isinstance(value, dict) and ("question" in value or "options" in value):
                            display_question(value, question_count)
                            question_count += 1
    else:
        st.info("")

if __name__ == "__main__":
    main()
