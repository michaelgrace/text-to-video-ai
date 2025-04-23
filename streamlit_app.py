import streamlit as st
import subprocess
import os
import time
import json
from pathlib import Path

st.set_page_config(
    page_title="Text-To-Video AI", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Move API keys to sidebar
with st.sidebar:
    st.header("API Settings")
    st.text("OpenAI API Key: ********")
    st.text("Pexels API Key: ********")

# Main content
st.title("Text-To-Video AI 🔥")
st.write("Generate video from text using AI")

tab_labels = ["Custom Script", "Topic"]
# Track previous tab to detect tab switch
if "prev_tab" not in st.session_state:
    st.session_state["prev_tab"] = tab_labels[0]
selected_tab = st.radio("Select Input Mode", tab_labels, horizontal=True, key="tab_select")

if "validation_msg" not in st.session_state:
    st.session_state["validation_msg"] = ""

# Clear validation message when switching tabs
if selected_tab != st.session_state["prev_tab"]:
    st.session_state["validation_msg"] = ""
st.session_state["prev_tab"] = selected_tab

if selected_tab == "Custom Script":
    custom_script = st.text_area("Enter your custom script", value="", key="custom_script_input")
    # Title is required for custom script
    title = st.text_input("Title (required)", value="", key="video_title_input")
    if st.session_state["validation_msg"]:
        st.warning(st.session_state["validation_msg"])
    if custom_script.strip() and st.session_state["validation_msg"]:
        st.session_state["validation_msg"] = ""
elif selected_tab == "Topic":
    topic = st.text_input("Topic for Video", value="Interesting Facts About Space", key="topic_input")
    # Title defaults to topic, but can be edited
    if "video_title_input" not in st.session_state or not st.session_state["video_title_input"]:
        st.session_state["video_title_input"] = st.session_state["topic_input"]
    title = st.text_input("Title (required)", value=st.session_state["video_title_input"], key="video_title_input")
    if st.session_state["validation_msg"]:
        st.warning(st.session_state["validation_msg"])
    if topic.strip() and st.session_state["validation_msg"]:
        st.session_state["validation_msg"] = ""

# Load voice options from schema
schema_path = Path(__file__).parent / "app" / "schemas" / "kokoro_voices.json"
with open(schema_path) as f:
    voice_data = json.load(f)
    available_voices = voice_data["voices"]

# Theme input above voice provider
theme = st.text_input("Theme", value="Add video theme", key="theme_input")
if "theme_validation_msg" not in st.session_state:
    st.session_state["theme_validation_msg"] = ""
if not theme.strip():
    st.session_state["theme_validation_msg"] = "Theme cannot be blank."
    st.warning(st.session_state["theme_validation_msg"])
elif st.session_state["theme_validation_msg"]:
    st.session_state["theme_validation_msg"] = ""

# Aspect ratio select box
aspect_ratio = st.selectbox(
    "Aspect Ratio",
    options=["landscape", "portrait", "square"],
    index=0,
    key="aspect_ratio"
)

# Voice control settings
voice_provider = st.selectbox(
    "Voice Provider",
    options=["kokoro", "edge", "elevenlabs", "tiktok"],
    index=0
)

language = st.selectbox(
    "Language",
    options=["English", "British"],
    index=0
)

# Filter voices based on language selection
filtered_voices = [v for v in available_voices if v.startswith(('af_', 'am_') if language == 'English' else ('bf_', 'bm_'))]

voice_id = st.selectbox(
    "Voice",
    options=filtered_voices,
    index=0,
    format_func=lambda x: x.split('_')[1].capitalize()  # Show only the name part
)

speech_rate = st.number_input(
    "Speech Rate (0.4 - 2.5)",
    min_value=0.4,
    max_value=2.5,
    value=0.8,
    step=0.1,
    format="%.1f"
)

# Process button
if st.button("Generate Video"):
    # Prevent running if theme is blank
    if not st.session_state["theme_input"].strip():
        st.session_state["theme_validation_msg"] = "Theme cannot be blank."
        st.warning(st.session_state["theme_validation_msg"])
        st.stop()
    else:
        st.session_state["theme_validation_msg"] = ""
    
    # Validate title
    if not st.session_state["video_title_input"].strip():
        st.session_state["validation_msg"] = "Title is required."
        st.warning(st.session_state["validation_msg"])
        st.stop()
    
    # Use custom script if selected, otherwise use topic
    if selected_tab == "Custom Script":
        if not st.session_state["custom_script_input"].strip():
            st.session_state["validation_msg"] = "Please add your custom script."
            st.experimental_rerun()
        else:
            st.session_state["validation_msg"] = ""
            input_text = st.session_state["custom_script_input"]
            # Ensure both --theme and --custom-script are included
            input_args = [
                "python", "app.py", input_text,
                "--theme", st.session_state["theme_input"],
                "--aspect-ratio", st.session_state["aspect_ratio"],
                "--title", st.session_state["video_title_input"],
                "--custom-script"
            ]
    else:
        if not st.session_state["topic_input"].strip():
            st.session_state["validation_msg"] = "Please add your topic."
            st.experimental_rerun()
        else:
            st.session_state["validation_msg"] = ""
            input_text = st.session_state["topic_input"]
            input_args = [
                "python", "app.py", input_text,
                "--theme", st.session_state["theme_input"],
                "--aspect-ratio", st.session_state["aspect_ratio"],
                "--title", st.session_state["video_title_input"]
            ]

    if not st.session_state["validation_msg"]:
        os.environ["VOICE_PROVIDER"] = voice_provider
        os.environ["VOICE_ID"] = voice_id
        os.environ["SPEECH_RATE"] = str(speech_rate)
        
        with st.spinner("Generating your video... This might take a while."):
            try:
                # Use input_args to pass the flag if needed
                process = subprocess.Popen(input_args, 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          text=True)
                
                # Create a placeholder for the output
                output_placeholder = st.empty()
                
                # Show output in real-time
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        output_placeholder.text(output.strip())
                
                # Check if process completed successfully
                if process.returncode == 0:
                    output_file = Path("rendered_video.mp4")
                    if output_file.exists():
                        st.success("Video generated successfully!")
                        st.video(str(output_file))
                        with open(output_file, "rb") as file:
                            st.download_button(
                                label="Download Video",
                                data=file,
                                file_name="rendered_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error("Video file not found. Check the console output for details.")
                else:
                    error = process.stderr.read()
                    st.error(f"Error generating video: {error}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

st.write("---")
st.write("### How it works")
st.write("""
1. Enter your OpenAI and Pexels API keys
2. Type in a topic for your video or enter a custom script
3. Click 'Generate Video' and wait for the process to complete
4. The generated video will appear below for viewing and download
""")
