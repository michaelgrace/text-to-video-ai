import streamlit as st
import subprocess
import os
import time
from pathlib import Path
from config.settings import settings

st.set_page_config(
    page_title=settings.APP_NAME, 
    page_icon=settings.APP_ICON
)

st.title(f"{settings.APP_NAME} 🔥")
st.write(settings.APP_DESCRIPTION)

# Input field for API keys
openai_key = st.text_input("OpenAI API Key", type="password", 
                          value=os.environ.get("OPENAI_API_KEY", ""))
pexels_key = st.text_input("Pexels API Key", type="password",
                          value=os.environ.get("PEXELS_API_KEY", ""))

# Input field for topic
topic = st.text_input("Topic for Video")

def format_filename(topic):
    # Replace spaces with hyphens and remove special characters
    filename = topic.replace(' ', '-')
    # Keep only alphanumeric chars and hyphens
    filename = ''.join(c for c in filename if c.isalnum() or c == '-')
    return f"{filename}.mp4"

# Process button
if st.button("Generate Video"):
    if not openai_key or not pexels_key:
        st.error(settings.ERROR_MESSAGES["API_KEYS_MISSING"])
    else:
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["PEXELS_API_KEY"] = pexels_key
        
        with st.spinner(settings.GENERATING_MESSAGE):
            try:
                # Run the app.py script with the given topic
                process = subprocess.Popen(["python", "app.py", topic], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          text=True)
                
                # Create a placeholder for the output
                output_placeholder = st.empty()
                
                # Create placeholders for different stages
                script_placeholder = st.empty()
                audio_placeholder = st.empty()
                captions_placeholder = st.empty()
                video_placeholder = st.empty()
                progress_bar = st.progress(0)
                
                # Show output in real-time with stage tracking
                stages = {
                    "script:": (script_placeholder, settings.PROGRESS_STAGES["script"]["name"]),
                    "audio_tts": (audio_placeholder, settings.PROGRESS_STAGES["audio"]["name"]),
                    "timed_captions": (captions_placeholder, settings.PROGRESS_STAGES["captions"]["name"]),
                    "background_video": (video_placeholder, settings.PROGRESS_STAGES["video"]["name"])
                }
                
                current_progress = 0
                while True:
                    # This code captures and displays the output
                    output = process.stdout.readline()
                    if output:
                        output_placeholder.text(output.strip())
                    
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Update relevant stage placeholder
                        for key, (placeholder, message) in stages.items():
                            if key in output.lower():
                                placeholder.info(message)
                                current_progress += settings.PROGRESS_STAGES[key.replace(":", "")]["weight"]
                                progress_bar.progress(min(current_progress, 100))
                        
                        # Show all output in main placeholder
                        output_placeholder.text(output.strip())
                
                # Check if process completed successfully
                if process.returncode == 0:
                    st.success("Video generated successfully!")
                    
                    try:
                        # Look for video in container root where render_engine.py writes it
                        output_file = Path("/app") / settings.DEFAULT_OUTPUT_FILENAME
                        if output_file.exists():
                            # Display the video
                            st.video(str(output_file))
                            
                            # Add download button with formatted filename
                            with open(output_file, "rb") as file:
                                st.download_button(
                                    label="Download Video",
                                    data=file,
                                    file_name=format_filename(topic),  # Use formatted topic name
                                    mime="video/mp4"
                                )
                        else:
                            st.error(settings.ERROR_MESSAGES["VIDEO_NOT_FOUND"])
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
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
