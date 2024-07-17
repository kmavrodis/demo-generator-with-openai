import os
import streamlit as st
from openai import AzureOpenAI
import tempfile
import importlib.util
import sys
from dotenv import load_dotenv
import traceback
import io
import uuid
import json

load_dotenv()
st.set_page_config(layout="wide", page_title="AI Demo Generator")

# Load System messages for AI models
PRODUCT_OWNER_AI = open("product_owner_ai.txt", "r").read()
SOFTWARE_ENGINEER_AI = open("software_engineer_ai.txt", "r").read()

# Load environment variables
AZURE_WHISPER_KEY = os.getenv("AZURE_WHISPER_KEY")
AZURE_WHISPER_DEPLOYMENT = os.getenv("AZURE_WHISPER_DEPLOYMENT")
AZURE_WHISPER_ENDPOINT = os.getenv("AZURE_WHISPER_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
DOCUMENT_INTELLIGENCE_KEY = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version="2023-05-15",
    azure_endpoint=OPENAI_ENDPOINT
)

client_whisper = AzureOpenAI(
    api_key=AZURE_WHISPER_KEY,
    api_version="2024-02-01",
    azure_endpoint=AZURE_WHISPER_ENDPOINT
)

# Initialize session state variables
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'script_path' not in st.session_state:
    st.session_state.script_path = None
if 'use_case_description' not in st.session_state:
    st.session_state.use_case_description = ""
if 'detailed_description' not in st.session_state:
    st.session_state.detailed_description = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'last_successful_run' not in st.session_state:
    st.session_state.last_successful_run = None

def generate_detailed_description(use_case_description):
    st.toast("Generating detailed description...")
    prompt = f"""
    Demo description:
    {use_case_description}
    """
    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": PRODUCT_OWNER_AI},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def generate_code(detailed_description, error_message=None):
    st.toast("Generating code...")
    if error_message:
        prompt = f"""
        Detailed description: {detailed_description}
        
        The current code produced the following error:
        {error_message}
        
        Please fix the code to resolve this error. Provide only the Python code with comments and without any additional text or explanations. Don't return any markdown. ONLY Python code. Don't output ```python and ``` at the beginning and end of the code. Always return the whole Python file.
        """
    else:
        prompt = f"{detailed_description} - Provide only the Python code with comments and without any additional text or explanations. - Don't return any markdown. ONLY Python code. Don't output ```python and ``` at the beginning and end of the code. - Always return the whole Python file."
    
    mess = [
        {"role": "system", "content": SOFTWARE_ENGINEER_AI},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT_NAME,
        messages=mess,
        temperature=1,
        max_tokens=4096
    )
    return response.choices[0].message.content

def save_and_load_script(code):
    if code is None:
        st.error("No code was generated. Please try again.")
        return None
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
        print(temp_file_path)
    
    return temp_file_path

def run_script(script_path):
    st.toast("Running the script...")
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        spec = importlib.util.spec_from_file_location("dynamic_script", script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["dynamic_script"] = module
        spec.loader.exec_module(module)
    except Exception as e:
        error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
        return False, error_message
    finally:
        sys.stdout = old_stdout
    
    output = redirected_output.getvalue()
    return True, output
    



def edit_code(user_input, current_code):
    st.info("Editing code based on your request...")
    prompt = f"""
    Current code:
    {current_code}

    User request:
    {user_input}

    Please modify the code according to the user's request. Return only the updated Python code without any additional text or explanations.
    """
    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": SOFTWARE_ENGINEER_AI},
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        max_tokens=4096
    )
    
    return response.choices[0].message.content


# Add this new function to save demos
def save_demo(use_case, detailed_description, code):
    if not os.path.exists('demos'):
        os.makedirs('demos')
    
    demo_id = str(uuid.uuid4())
    demo_data = {
        'id': demo_id,
        'use_case': use_case,
        'detailed_description': detailed_description,
        'code': code
    }
    
    with open(f'demos/{demo_id}.json', 'w') as f:
        json.dump(demo_data, f)
    
    return demo_data

# Add a new function to delete a demo
def delete_demo(demo_id):
    file_path = f'demos/{demo_id}.json'
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

# Add a new function to load a demo
def load_demo(demo_id):
    file_path = f'demos/{demo_id}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

# Modify the save_and_load_script function
def save_and_load_script(code):
    if code is None:
        st.error("No code was generated. Please try again.")
        return None
    
    if not os.path.exists('demos'):
        os.makedirs('demos')
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', dir='demos') as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
        print(temp_file_path)
    
    return temp_file_path

def main():
    st.header("AI Demo Generator 🚀")
    # Add status bar
    progress_bar = st.progress(st.session_state.progress)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Describe Use Case",
        "🧠 Generate Demo",
        "🚀 Run Demo",
        "✏️ Edit Code",
        "📚 Demo Library"
    ])


    with tab1:
        st.markdown("""

            This tool helps you quickly generate and iterate on code based on your use case description. Here's how to use it:

            1. **Describe** 📝: Start by describing your use case in the text area below. Be as specific as possible about what you want the code to do.

            2. **Generate** 🧠: Once you've entered your description, the tool will automatically generate a detailed description and the corresponding code. You can view and compare them side by side.

            3. **Run Code** 🚀: After the code is generated, you can run it to see the results. If there are any errors, the tool will attempt to fix them automatically.

            4. **Edit Code** ✏️: If you want to make changes to the generated code, you can do so in the Edit Code tab. Simply describe the changes you want, and the AI will update the code accordingly.

            5. **Manage Demos** 📚: Save your current demo to the library, view saved demos, load previous demos, or delete demos you no longer need.

            Remember, the more detailed and clear your initial description, the better the generated code will be.💻 
        """)
        st.subheader("Describe Your Use Case")
        use_case_description = st.text_area("Your description will be provided to a Product Owner AI to generate a detailed solution plan", value=st.session_state.use_case_description)
        if st.button("Generate Demo"):
            st.session_state.use_case_description = use_case_description
            st.session_state.detailed_description = None
            st.session_state.generated_code = None
            st.session_state.progress = 0
            progress_bar.progress(st.session_state.progress)
            st.session_state.last_successful_run = None
            st.info("Generating detailed description and code... Please switch to the Generate 🧠 tab to see the results.")
            st.session_state.progress = 25
            progress_bar.progress(st.session_state.progress)


    with tab2:
        if st.session_state.use_case_description:
            col1, col2 = st.columns(2)
            with col1:
                if not st.session_state.detailed_description:
                    with st.spinner("Product Owner AI is generating a detailed description..."):
                        detailed_description = generate_detailed_description(st.session_state.use_case_description)
                        st.session_state.detailed_description = detailed_description
                        st.session_state.progress = 50
                        progress_bar.progress(st.session_state.progress)
                st.subheader("Detailed Description")
                st.markdown(st.session_state.detailed_description)
            with col2:
                if not st.session_state.generated_code:
                    with st.spinner("Software Engineer AI is generating code..."):
                        generated_code = generate_code(st.session_state.detailed_description)
                        if generated_code:
                            st.session_state.generated_code = generated_code
                            script_path = save_and_load_script(generated_code)
                            if script_path:
                                st.session_state.script_path = script_path
                                st.session_state.progress = 75
                                progress_bar.progress(st.session_state.progress)
                                st.empty()
                            else:
                                st.error("Failed to save the generated code. Please try again.")
                        else:
                            st.error("Failed to generate code. Please try again with a different description.")
                st.subheader("Generated Code")
                if st.session_state.generated_code:
                    st.code(st.session_state.generated_code, language='python')
                    if st.button("Save Demo"):
                        demo_id = save_demo(st.session_state.use_case_description, st.session_state.detailed_description, st.session_state.generated_code)
                        st.success(f"Demo saved successfully! ID: {demo_id}")
                else:
                    st.info("No code generated yet. Please describe your use case and click 'Generate Demo'.")
        else:
            st.info("Please describe your use case in the 'Describe' tab first.")

    with tab3:
        if st.session_state.generated_code and st.session_state.script_path:
            st.info("The generated code will run automatically. If there are errors, it will attempt to regenerate and rerun the code.")
            
            max_attempts = 3
            for attempt in range(max_attempts):
                success, result = run_script(st.session_state.script_path)

                if success:
                    st.success("Code ran successfully!")
                    st.text(result)
                    st.session_state.progress = 100
                    progress_bar.progress(st.session_state.progress)
                    st.session_state.last_successful_run = st.session_state.generated_code
                    break
                else:
                    if attempt < max_attempts - 1:
                        st.warning(f"Attempt {attempt + 1} failed. Regenerating code...")
                        st.warning("Attempting to fix error: " + result)
                        generated_code = edit_code(st.session_state.generated_code, result)
                        if generated_code:
                            st.session_state.generated_code = generated_code
                            script_path = save_and_load_script(generated_code)
                            if script_path:
                                st.session_state.script_path = script_path
                                st.session_state.progress = 50
                                progress_bar.progress(st.session_state.progress)
                                st.rerun()
                            else:
                                st.error("Failed to save the regenerated code. Please try again.")
                                break
                        else:
                            st.error("Failed to regenerate code. Please try again with a different description.")
                            break
                    else:
                        st.error("Failed to generate working code after multiple attempts. Please try again with a different description.")
                        st.text(result)
        else:
            st.info("No code has been generated yet. Please go to the 'Generate' tab to create a script.")

    with tab4:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Current Code")
            if st.session_state.generated_code:
                st.code(st.session_state.generated_code, language='python')
            else:
                st.info("No code generated yet. Please generate code first.")
        with col2:
            st.subheader("Chat")
            user_input = st.text_area("Enter your code edit request:")
            if st.button("Submit Edit Request"):
                if st.session_state.generated_code:
                    edited_code = edit_code(user_input, st.session_state.generated_code)
                    st.session_state.generated_code = edited_code
                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(("assistant", "Code updated based on your request."))
                    script_path = save_and_load_script(edited_code)
                    if script_path:
                        st.session_state.script_path = script_path
                        st.session_state.progress = 0
                        progress_bar.progress(st.session_state.progress)
                        st.success("Code updated successfully! Please go to the Run Demo tab to verify the changes.")
                        success, result = run_script(st.session_state.script_path)
                        st.rerun()
                    else:
                        st.error("Failed to save the updated code. Please try again.")
                else:
                    st.warning("No code has been generated yet. Please generate code first.")

            # Display chat history
            for role, message in st.session_state.chat_history:
                if role == "user":
                    st.text_input("You:", message, key=f"user_{uuid.uuid4()}", disabled=True)
                else:
                    st.text_area("Assistant:", message, key=f"assistant_{uuid.uuid4()}", disabled=True)
    with tab5:
        
        # Add "Save Current Demo" button
        if st.session_state.use_case_description and st.session_state.detailed_description and st.session_state.generated_code:
            if st.button("Save Current Demo"):
                demo_data = save_demo(st.session_state.use_case_description, st.session_state.detailed_description, st.session_state.generated_code)
                st.success(f"Demo saved successfully! ID: {demo_data['id']}")
        else:
            st.info("Generate a demo before saving to the library.")
        
        st.subheader("Saved Demos:")
        if os.path.exists('demos'):
            demo_files = [f for f in os.listdir('demos') if f.endswith('.json')]
            for demo_file in demo_files:
                with open(f'demos/{demo_file}', 'r') as f:
                    demo_data = json.load(f)
                
                
                with st.expander(f"{demo_data['use_case']}"):

                    col1, col2, col3, col4 = st.columns([4, 1, 1, 3])
                    with col1:
                        st.markdown(f"#### {demo_data['use_case']}")
                        st.write(f"Demo ID: {demo_data['id']}")

                    with col4:
                        if st.button(f"View {demo_data['id'][:8]}"):
                            st.write("Detailed Description:")
                            st.write(demo_data['detailed_description'])
                            st.write("Code:")
                            st.code(demo_data['code'], language='python')
                    with col2:
                        if st.button(f"Load {demo_data['id'][:8]}"):
                            st.session_state.use_case_description = demo_data['use_case']
                            st.session_state.detailed_description = demo_data['detailed_description']
                            st.session_state.generated_code = demo_data['code']
                            st.session_state.script_path = save_and_load_script(demo_data['code'])
                            st.success(f"Demo {demo_data['id']} loaded successfully!")
                            st.info("Switch to the 'Run Code' tab to execute the loaded demo.")
                            st.rerun()
                    with col3:
                        if st.button(f"Delete {demo_data['id'][:8]}"):
                            if delete_demo(demo_data['id']):
                                st.success(f"Demo {demo_data['id']} deleted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete demo {demo_data['id']}.")

        else:
            st.info("No demos saved yet. Generate and save some demos to see them here!")


if __name__ == "__main__":
    main()