import streamlit as st
import subprocess
import os
import time
import json
import re
import ast
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

st.set_page_config(
    page_title="Text-To-Video AI", 
    page_icon="🎬", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load .env for log4UI toggle
load_dotenv()
LOG4UI = os.getenv("log4UI", "true").lower() == "true"

# Move API keys to sidebar
with st.sidebar:
    st.header("API Settings")
    st.text("OpenAI API Key: ********")
    st.text("Pexels API Key: ********")

# Main content
st.title("Text-To-Video AI 🔥")
st.write("Generate video from text using AI")

# tab_labels = ["Custom Script", "Topic", "Upload Media", "Upload Background Video"]
tab_labels = ["Custom Script", "Topic", "Upload Audio"]
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
elif selected_tab == "Upload Audio":
    uploaded_audio = st.file_uploader("Upload WAV audio file", type=["wav"], key="audio_upload")
    title = st.text_input("Title (required)", value="", key="video_title_input")
    if st.session_state["validation_msg"]:
        st.warning(st.session_state["validation_msg"])
    if uploaded_audio and st.session_state["validation_msg"]:
        st.session_state["validation_msg"] = ""

# Load voice options from schema
schema_path = Path(__file__).parent / "app" / "schemas" / "kokoro_voices.json"
with open(schema_path) as f:
    voice_data = json.load(f)
    available_voices = voice_data["voices"]

# --- Background video uploader ---
uploaded_bg_video = st.file_uploader(
    "Background Video (optional, will be used as the sole background for the entire video)",
    type=["mp4", "mov", "avi", "mkv"],
    key="bg_video_upload"
)
bg_video_path = None
if uploaded_bg_video is not None:
    try:
        bg_video_path = os.path.join(os.getcwd(), "background_uploaded.mp4")
        # Remove if a directory exists at this path
        if os.path.isdir(bg_video_path):
            import shutil
            shutil.rmtree(bg_video_path)
        # Remove if a file exists at this path
        if os.path.isfile(bg_video_path):
            os.remove(bg_video_path)
        with open(bg_video_path, "wb") as f:
            f.write(uploaded_bg_video.read())
        print(f"Background video saved to: {bg_video_path}")
        # --- Clear and disable theme when background video is uploaded ---
        st.session_state["theme_input"] = ""
        theme_disabled = True
    except Exception as e:
        st.error(f"Failed to save background video: {e}")
        bg_video_path = None
        theme_disabled = False
else:
    theme_disabled = False

# Theme input above voice provider
theme = st.text_input(
    "Theme",
    value=st.session_state.get("theme_input", "Add video theme"),
    key="theme_input",
    disabled=theme_disabled
)
if "theme_validation_msg" not in st.session_state:
    st.session_state["theme_validation_msg"] = ""
if not theme.strip() and not theme_disabled:
    st.session_state["theme_validation_msg"] = "Theme cannot be blank."
    st.warning(st.session_state["theme_validation_msg"])
elif st.session_state["theme_validation_msg"]:
    st.session_state["theme_validation_msg"] = ""

# --- Place soundtrack uploader and volume control here, standalone ---
uploaded_soundtrack = st.file_uploader(
    "Audio Soundtrack (optional, will loop/fade, default 10% volume)",
    type=["mp3", "wav", "aac", "m4a", "ogg"],
    key="soundtrack_upload"
)
soundtrack_path = None
if uploaded_soundtrack is not None:
    try:
        soundtrack_path = os.path.join(os.getcwd(), "audio_soundtrack_uploaded.wav")
        # Defensive: If a directory exists at this path, remove it
        if os.path.isdir(soundtrack_path):
            import shutil
            shutil.rmtree(soundtrack_path)
        # If file exists, remove it before writing
        if os.path.exists(soundtrack_path):
            os.remove(soundtrack_path)
        with open(soundtrack_path, "wb") as f:
            f.write(uploaded_soundtrack.read())
        print(f"Soundtrack saved to: {soundtrack_path}")
    except Exception as e:
        st.error(f"Failed to save soundtrack: {e}")
        soundtrack_path = None

soundtrack_volume = st.number_input(
    "Soundtrack Volume (0.0 - 1.0, default 0.1)",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.01,
    format="%.2f",
    key="soundtrack_volume"
)

# --- Add controls for max script duration and max words ---
col_dur, col_words = st.columns(2)
with col_dur:
    max_script_duration = st.number_input(
        "Max Script Duration (seconds)",
        min_value=15,
        max_value=600,
        value=15,
        step=15,
        key="max_script_duration"
    )
with col_words:
    max_script_words = st.number_input(
        "Max Script Words",
        min_value=50,
        max_value=1000,
        value=50,
        step=50,
        key="max_script_words"
    )

# --- Arrange Aspect Ratio, Rendering Mode, and Voice Provider in a single row ---
col_ar, col_rm, col_vp = st.columns(3)
with col_ar:
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        options=["landscape", "portrait", "square"],
        index=0,
        key="aspect_ratio"
    )
with col_rm:
    render_mode = st.selectbox(
        "Rendering Mode",
        options=["video", "photo", "hybrid (both)"],
        index=0,
        key="render_mode"
    )
with col_vp:
    voice_provider = st.selectbox(
        "Voice Provider",
        options=["kokoro", "edge", "elevenlabs", "tiktok"],
        index=0
    )

# --- Arrange Language, Voice, and Speech Rate in a single row ---
col_lang, col_voice, col_rate = st.columns(3)
with col_lang:
    language = st.selectbox(
        "Language",
        options=["English", "British"],
        index=0
    )

# Filter voices based on language selection
filtered_voices = [v for v in available_voices if v.startswith(('af_', 'am_') if language == 'English' else ('bf_', 'bm_'))]

with col_voice:
    voice_id = st.selectbox(
        "Voice",
        options=filtered_voices,
        index=0,
        format_func=lambda x: x.split('_')[1].capitalize()  # Show only the name part
    )

with col_rate:
    speech_rate = st.number_input(
        "Speech Rate (0.4 - 2.5)",
        min_value=0.4,
        max_value=2.5,
        value=0.8,
        step=0.1,
        format="%.1f"
    )

# Add toggles for disabling captions and audio (show not implemented)
col1, col2 = st.columns(2)
with col1:
    disable_captions = st.checkbox("Disable Captions")
with col2:
    disable_audio = st.checkbox("Disable Audio")

# --- Log saving helpers ---
def get_log_save_path(title):
    base_dir = Path("exports/logs/video_generation")
    base_dir.mkdir(parents=True, exist_ok=True)
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    base_name = safe_title if safe_title else "video_log"
    filename = f"{base_name}.json"
    i = 1
    while (base_dir / filename).exists():
        filename = f"{base_name}_{i}.json"
        i += 1
    return base_dir / filename

def save_log(log_data, title):
    log_path = get_log_save_path(title)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)
    return log_path

def pretty_json_or_text(line):
    # --- Pretty-print JSON ---
    try:
        obj = json.loads(line)
        return json.dumps(obj, indent=2)
    except Exception:
        pass
    # --- Pretty-print timed_captions: lines vertically ---
    if line.strip().startswith("timed_captions:"):
        match = re.search(r'timed_captions:\s*(\[.*\])', line)
        if match:
            captions_str = match.group(1)
            try:
                captions = ast.literal_eval(captions_str)
                pretty_lines = []
                for segment in captions:
                    time_range, text = segment
                    pretty_lines.append(f"  {time_range}: {text}")
                return "timed_captions:\n" + "\n".join(pretty_lines)
            except Exception:
                return line
    # --- Pretty-print Timed Captions:((...))((...)) lines vertically ---
    if line.strip().startswith("Timed Captions:"):
        matches = re.findall(r'\(\(([^,]+), ([^\)]+)\), [\'"](.+?)[\'"]\)', line)
        if matches:
            pretty_lines = []
            for start, end, text in matches:
                pretty_lines.append(f"  [{start}, {end}]: {text}")
            return "Timed Captions:\n" + "\n".join(pretty_lines)
    # --- Pretty-print Text ```json [ ... ] ``` lines vertically ---
    # Handles both: Text ```json [ ... ] ``` and  ```json [ ... ] ```
    match = re.search(r'```json\s*(\[.*\])\s*```', line)
    if match:
        try:
            arr = ast.literal_eval(match.group(1))
            pretty_lines = []
            for segment in arr:
                if isinstance(segment, list) and len(segment) == 2:
                    time_range, keywords = segment
                    pretty_lines.append(f"  {time_range}: {keywords}")
            return "Text JSON:\n" + "\n".join(pretty_lines)
        except Exception:
            return line
    # Handles: Text ```json [ ... ] ``` inline (no newlines)
    match2 = re.search(r'Text ```json\s*(\[.*\])\s*```', line)
    if match2:
        try:
            arr = ast.literal_eval(match2.group(1))
            pretty_lines = []
            for segment in arr:
                if isinstance(segment, list) and len(segment) == 2:
                    time_range, keywords = segment
                    pretty_lines.append(f"  {time_range}: {keywords}")
            return "Text JSON:\n" + "\n".join(pretty_lines)
        except Exception:
            return line
    # --- Pretty-print background_video_urls: lines vertically ---
    if line.strip().startswith("background_video_urls:"):
        match = re.search(r'background_video_urls:\s*(\[.*\])', line)
        if match:
            urls_str = match.group(1)
            try:
                arr = ast.literal_eval(urls_str)
                pretty_lines = []
                for segment in arr:
                    if isinstance(segment, list) and len(segment == 2):
                        time_range, url = segment
                        pretty_lines.append(f"  {time_range}: {url}")
                return "background_video_urls:\n" + "\n".join(pretty_lines)
            except Exception:
                return line
    return line

def sanitize_title_for_filename(title):
    # Replace spaces with hyphens, remove illegal/special characters
    safe = re.sub(r'[^A-Za-z0-9_\-]', '', title.replace(' ', '-'))
    return safe if safe else "video"

def get_incremented_download_name(base_name, ext=".mp4"):
    # Only for download, not for saving on disk
    candidate = f"{base_name}{ext}"
    i = 1
    while os.path.exists(candidate):
        candidate = f"{base_name}({i}){ext}"
        i += 1
    return candidate

# --- Video output placeholder ---
video_placeholder = st.empty()

# --- Log window, progress bar, and status placeholders (always visible, below video) ---
if LOG4UI:
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    log_placeholder = st.empty()  # <-- use st.empty() for a single updatable window
    download_log_placeholder = st.empty()
    st.markdown(
        """
        <style>
        .log-window {
            font-family: monospace;
            background: #181818;
            color: #f0f0f0;
            height: 500px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #444;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if "log_lines" not in st.session_state:
        st.session_state["log_lines"] = []
    if "log_metadata" not in st.session_state:
        st.session_state["log_metadata"] = []
    if "last_log_line" not in st.session_state:
        st.session_state["last_log_line"] = ""
    if "last_progress" not in st.session_state:
        st.session_state["last_progress"] = 0
    if "current_stage" not in st.session_state:
        st.session_state["current_stage"] = ""
    if "log_file_path" not in st.session_state:
        st.session_state["log_file_path"] = None
else:
    log_placeholder = None
    status_placeholder = None
    progress_placeholder = None
    download_log_placeholder = None

# Process button
if st.button("Generate Video"):
    # Prevent running if theme is blank
    if not st.session_state["theme_input"].strip() and not theme_disabled:
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
    
    # Use custom script if selected, otherwise use topic or audio
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
                "--custom-script",
                "--render-mode", render_mode  # <-- pass render mode
            ]
            if disable_captions:
                input_args.append("--disable-captions")
            if disable_audio:
                input_args.append("--disable-audio")
            if soundtrack_path:
                input_args += ["--soundtrack-file", soundtrack_path, "--soundtrack-volume", str(soundtrack_volume)]
            if bg_video_path:
                input_args += ["--background-video-file", bg_video_path]
    elif selected_tab == "Topic":
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
                "--title", st.session_state["video_title_input"],
                "--render-mode", render_mode,
                "--max-seconds", str(st.session_state.get("max_script_duration", 45)),
                "--max-words", str(st.session_state.get("max_script_words", 50))
            ]
            if disable_captions:
                input_args.append("--disable-captions")
            if disable_audio:
                input_args.append("--disable-audio")
            if soundtrack_path:
                input_args += ["--soundtrack-file", soundtrack_path, "--soundtrack-volume", str(soundtrack_volume)]
            if bg_video_path:
                input_args += ["--background-video-file", bg_video_path]
    elif selected_tab == "Upload Audio":
        if not uploaded_audio:
            st.session_state["validation_msg"] = "Please upload a WAV audio file."
            st.experimental_rerun()
        elif not st.session_state["video_title_input"].strip():
            st.session_state["validation_msg"] = "Title is required."
            st.experimental_rerun()
        elif not st.session_state.get("theme_input", "").strip() and not theme_disabled:
            st.session_state["theme_validation_msg"] = "Theme cannot be blank."
            st.experimental_rerun()
        else:
            st.session_state["validation_msg"] = ""
            # Save uploaded audio to disk
            audio_save_path = "audio_uploaded.wav"
            with open(audio_save_path, "wb") as f:
                f.write(uploaded_audio.read())
            input_args = [
                "python", "app.py",
                "--audio-file", audio_save_path,
                "--theme", st.session_state.get("theme_input", "Add video theme"),
                "--aspect-ratio", st.session_state["aspect_ratio"],
                "--title", st.session_state["video_title_input"],
                "--render-mode", render_mode
            ]
            if soundtrack_path:
                input_args += ["--soundtrack-file", soundtrack_path, "--soundtrack-volume", str(soundtrack_volume)]
            if disable_captions:
                input_args.append("--disable-captions")
            if disable_audio:
                input_args.append("--disable-audio")
            if bg_video_path:
                input_args += ["--background-video-file", bg_video_path]
    elif selected_tab == "Upload Background Video":
        st.warning("Background video upload is not implemented yet.")
        st.stop()

    # Clear log window and metadata for new run
    if LOG4UI:
        st.session_state["log_lines"] = []
        st.session_state["log_metadata"] = []
        st.session_state["last_log_line"] = ""
        st.session_state["last_progress"] = 0
        st.session_state["current_stage"] = ""
        st.session_state["log_file_path"] = None
        log_placeholder.markdown('<div class="log-window"></div>', unsafe_allow_html=True)
        status_placeholder.info("Starting video generation...")
        progress_placeholder.progress(0)
        download_log_placeholder.empty()

    if not st.session_state["validation_msg"]:
        os.environ["VOICE_PROVIDER"] = voice_provider
        os.environ["VOICE_ID"] = voice_id
        os.environ["SPEECH_RATE"] = str(speech_rate)
        
        # --- Pass updated environment to subprocess ---
        sub_proc = os.environ.copy()
        sub_proc["VOICE_PROVIDER"] = voice_provider
        sub_proc["VOICE_ID"] = voice_id
        sub_proc["SPEECH_RATE"] = str(speech_rate)

        with st.spinner("Generating your video... This might take a while."):
            try:
                process = subprocess.Popen(
                    input_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    env=sub_proc  # <-- renamed from env to sub_proc
                )
                progress = 0
                while True:
                    line = process.stdout.readline()
                    if line == '' and process.poll() is not None:
                        break
                    if not line:
                        continue
                    line = line.rstrip()
                    # --- Filter progress bar lines and consecutive duplicates ---
                    if "%|" in line:
                        import re
                        match = re.search(r"(\d+)%\|", line)
                        if match:
                            progress = int(match.group(1))
                            if LOG4UI:
                                progress_placeholder.progress(progress / 100)
                        continue
                    if line == st.session_state["last_log_line"]:
                        continue
                    st.session_state["last_log_line"] = line

                    # --- Metadata for log ---
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "stage": st.session_state.get("current_stage", ""),
                        "line": line
                    }
                    st.session_state["log_metadata"].append(log_entry)

                    # --- Pretty-print JSON if possible ---
                    display_line = pretty_json_or_text(line)

                    # --- Detect and update stage/status ---
                    stage_map = [
                        ("Generating script", "Generating script with OpenAI..."),
                        ("Generating audio", "Generating audio..."),
                        ("Generating captions", "Generating captions..."),
                        ("Generating search terms", "Generating search terms..."),
                        ("Searching for Pexels", "Searching for Pexels videos..."),
                        ("Rendering video", "Rendering video..."),
                        ("Video generation complete", "Video generation complete!"),
                        ("Error", "An error occurred."),
                    ]
                    for key, msg in stage_map:
                        if key.lower() in line.lower():
                            st.session_state["current_stage"] = msg
                            if LOG4UI:
                                if "error" in key.lower():
                                    status_placeholder.error(msg)
                                elif "complete" in key.lower():
                                    status_placeholder.success(msg)
                                else:
                                    status_placeholder.info(msg)
                            break
                    # --- Append to log window ---
                    if LOG4UI:
                        st.session_state["log_lines"].append(display_line)
                        log_html = (
                            '<div class="log-window" id="logwin">'
                            + "<br>".join(
                                l if l.startswith("{") or l.startswith("[") or l.startswith("<pre>")
                                else f"{l}"
                                for l in st.session_state["log_lines"]
                            )
                            + "</div>"
                            + """
                            <script>
                            var logwin = window.parent.document.getElementById('logwin');
                            if(logwin){logwin.scrollTop = logwin.scrollHeight;}
                            </script>
                            """
                        )
                        log_placeholder.markdown(log_html, unsafe_allow_html=True)  # <-- always update this one placeholder
                # --- Final status and video output ---
                if process.returncode == 0:
                    output_file = Path("rendered_video.mp4")
                    if output_file.exists():
                        st.success("Video generated successfully!")
                        video_placeholder.video(str(output_file))
                        # --- Use sanitized, incremented filename for download only ---
                        user_title = st.session_state["video_title_input"]
                        safe_title = sanitize_title_for_filename(user_title)
                        download_name = get_incremented_download_name(safe_title)
                        with open(output_file, "rb") as file:
                            st.download_button(
                                label="Download Video",
                                data=file,
                                file_name=download_name,
                                mime="video/mp4"
                            )
                        if LOG4UI:
                            status_placeholder.success("Video generation complete!")
                            progress_placeholder.progress(1.0)
                    else:
                        st.error("Video file not found. Check the console output for details.")
                        if LOG4UI:
                            status_placeholder.error("Video file not found.")
                else:
                    error = process.stdout.read()
                    st.error(f"Error generating video: {error}")
                    if LOG4UI:
                        status_placeholder.error("Error generating video.")
                # --- Save log to disk and show download button ---
                if LOG4UI:
                    log_data = {
                        "title": st.session_state["video_title_input"],
                        "generated_at": datetime.now().isoformat(),
                        "log": st.session_state["log_metadata"]
                    }
                    log_path = save_log(log_data, st.session_state["video_title_input"])
                    st.session_state["log_file_path"] = log_path
                    with open(log_path, "rb") as f:
                        download_log_placeholder.download_button(
                            label=f"Download Log ({log_path.name})",
                            data=f,
                            file_name=log_path.name,
                            mime="application/json"
                        )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if LOG4UI:
                    status_placeholder.error(f"An error occurred: {str(e)}")
                    # Save log even on error
                    log_data = {
                        "title": st.session_state["video_title_input"],
                        "generated_at": datetime.now().isoformat(),
                        "log": st.session_state["log_metadata"]
                    }
                    log_path = save_log(log_data, st.session_state["video_title_input"])
                    st.session_state["log_file_path"] = log_path
                    with open(log_path, "rb") as f:
                        download_log_placeholder.download_button(
                            label=f"Download Log ({log_path.name})",
                            data=f,
                            file_name=log_path.name,
                            mime="application/json"
                        )


