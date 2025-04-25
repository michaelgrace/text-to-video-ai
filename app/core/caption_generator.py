import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
import wave

def get_audio_duration(audio_filename):
    try:
        with wave.open(audio_filename, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        return None

def generate_timed_captions(audio_filename,model_size="base"):
    print("Generating captions...")
    try:
        WHISPER_MODEL = load_model(model_size)
        gen = transcribe_timestamped(WHISPER_MODEL, audio_filename, verbose=False, fp16=False)
        captions = getCaptionsWithTime(gen)
        # --- Fix: Only extend last caption if gap is small and not a duplicate or single word ---
        audio_duration = get_audio_duration(audio_filename)
        if captions and audio_duration:
            last_start, last_end = captions[-1][0]
            gap = audio_duration - last_end
            last_text = captions[-1][1].strip()
            # Remove duplicate last caption
            if len(captions) > 1 and last_text == captions[-2][1].strip():
                captions = captions[:-1]
                last_start, last_end = captions[-1][0]
                gap = audio_duration - last_end
                last_text = captions[-1][1].strip()
            # Only extend if gap is less than 0.5s and last caption is not a single word
            if 0 < gap < 0.5 and " " in last_text:
                captions[-1] = ((last_start, audio_duration), last_text)
        return captions
    except Exception as e:
        print(f"Error generating captions: {e}")
        raise

def splitWordsBySize(words, maxCaptionSize):
   
    halfCaptionSize = maxCaptionSize / 2
    captions = []
    while words:
        caption = words[0]
        words = words[1:]
        while words and len(caption + ' ' + words[0]) <= maxCaptionSize:
            caption += ' ' + words[0]
            words = words[1:]
            if len(caption) >= halfCaptionSize and words:
                break
        captions.append(caption)
    return captions

def getTimestampMapping(whisper_analysis):
   
    index = 0
    locationToTimestamp = {}
    print("Mapping timestamps...")
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            newIndex = index + len(word['text'])+1
            locationToTimestamp[(index, newIndex)] = word['end']
            index = newIndex
    return locationToTimestamp

def cleanWord(word):
   
    return re.sub(r'[^\w\s\-_"\'\']', '', word)

def interpolateTimeFromDict(word_position, d):
   
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def getCaptionsWithTime(whisper_analysis, maxCaptionSize=40, considerPunctuation=False):
   
    print("Processing captions with time...")
    wordLocationToTime = getTimestampMapping(whisper_analysis)
    position = 0
    start_time = 0
    CaptionsPairs = []
    text = whisper_analysis['text']
    
    if considerPunctuation:
        sentences = re.split(r'(?<=[.!?]) +', text)
        words = [word for sentence in sentences for word in splitWordsBySize(sentence.split(), maxCaptionSize)]
    else:
        words = text.split()
        words = [cleanWord(word) for word in splitWordsBySize(words, maxCaptionSize)]
    
    for word in words:
        position += len(word) + 1
        end_time = interpolateTimeFromDict(position, wordLocationToTime)
        if end_time and word:
            CaptionsPairs.append(((start_time, end_time), word))
            start_time = end_time

    return CaptionsPairs

def merge_captions_by_duration(captions, min_segment_duration=8, max_segment_duration=12):
    """
    Merge adjacent captions so each segment is at least min_segment_duration
    and at most max_segment_duration seconds.
    """
    merged = []
    i = 0
    while i < len(captions):
        start, _ = captions[i][0]
        texts = [captions[i][1]]
        end = captions[i][0][1]
        j = i + 1
        # Merge until min_segment_duration is reached or max_segment_duration is exceeded
        while (end - start) < min_segment_duration and j < len(captions):
            end = captions[j][0][1]
            texts.append(captions[j][1])
            j += 1
            if (end - start) >= max_segment_duration:
                break
        merged.append(((start, end), " ".join(texts)))
        i = j
    return merged
