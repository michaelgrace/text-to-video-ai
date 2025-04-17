import streamlit as st
import subprocess
import os
import time
from pathlib import Path

st.set_page_config(page_title="Text-To-Video AI", page_icon="🎬")

st.title("Text-To-Video AI 🔥")
st.write("Generate video from text using AI")

# Input field for API keys
openai_key = st.text_input("OpenAI API Key", type="password", 
                          value=os.environ.get("OPENAI_API_KEY", ""))
pexels_key = st.text_input("Pexels API Key", type="password",
                          value=os.environ.get("PEXELS_API_KEY", ""))

# Input field for topic
topic = st.text_input("Topic for Video", value="Interesting Facts About Space")

# Process button
if st.button("Generate Video"):
    if not openai_key or not pexels_key:
        st.error("Please provide both API keys")
    else:
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["PEXELS_API_KEY"] = pexels_key
        
        with st.spinner("Generating your video... This might take a while."):
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
                    "script:": (script_placeholder, "🤖 Generating script..."),
                    "audio_tts": (audio_placeholder, "🎵 Creating audio..."),
                    "timed_captions": (captions_placeholder, "📝 Generating captions..."),
                    "background_video": (video_placeholder, "🎬 Processing video...")
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
                                current_progress += 25
                                progress_bar.progress(min(current_progress, 100))
                        
                        # Show all output in main placeholder
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
