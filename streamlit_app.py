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

# Input field for topic
topic = st.text_input("Topic for Video", value="Interesting Facts About Space")

# Load voice options from schema
schema_path = Path(__file__).parent / "app" / "schemas" / "kokoro_voices.json"
with open(schema_path) as f:
    voice_data = json.load(f)
    available_voices = voice_data["voices"]

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
    # Remove API key checks since they're handled by environment
    os.environ["VOICE_PROVIDER"] = voice_provider
    os.environ["VOICE_ID"] = voice_id
    os.environ["SPEECH_RATE"] = str(speech_rate)
    
    with st.spinner("Generating your video... This might take a while."):
        try:
            # Run the app.py script with the given topic
            process = subprocess.Popen(["python", "app.py", topic], 
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
                st.success("Video generated successfully!")
                
                # Check if the output file exists
                output_file = Path("rendered_video.mp4")
                if output_file.exists():
                    # Display the video
                    st.video(str(output_file))
                    
                    # Add download button
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
2. Type in a topic for your video
3. Click 'Generate Video' and wait for the process to complete
4. The generated video will appear below for viewing and download
""")
