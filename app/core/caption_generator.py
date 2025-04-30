import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
import wave

def get_audio_duration(audio_filename):
    try:
        with wave.open(audio_filename, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            print(f"DEBUG: WAV duration for {audio_filename}: {duration}")
            return duration
    except Exception as e:
        print(f"DEBUG: Failed to get WAV duration for {audio_filename}: {e}")
        return None

def generate_timed_captions(audio_filename, model_size="base", aspect_ratio="landscape", max_caption_size=None):
    print("Generating captions...")
    try:
        WHISPER_MODEL = load_model(model_size)
        gen = transcribe_timestamped(WHISPER_MODEL, audio_filename, verbose=False, fp16=False)
        # Use provided max_caption_size if given, else default by aspect_ratio
        if max_caption_size is not None:
            maxCaptionSize = max_caption_size
        else:
            maxCaptionSize = 20 if aspect_ratio == "portrait" else 25
        captions = getCaptionsWithTime(gen, maxCaptionSize=maxCaptionSize)
        audio_duration = get_audio_duration(audio_filename)
        # If the last caption ends >1s before the audio ends, extend it by a small buffer, not the full gap
        if captions and audio_duration:
            last_start, last_end = captions[-1][0]
            if audio_duration - last_end > 1.0:
                buffer = 0.3  # seconds
                new_end = min(audio_duration, last_end + buffer)
                print(f"Extending last caption from {last_end} to {new_end}")
                captions[-1] = ((last_start, new_end), captions[-1][1])
            # Remove duplicate last caption if present
            last_text = captions[-1][1].strip()
            if len(captions) > 1 and last_text == captions[-2][1].strip():
                captions = captions[:-1]
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
            newIndex = index + len(word['text']) + 1
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

def getCaptionsWithTime(
    whisper_analysis,
    maxCaptionSize=30,
    preserve_punctuation=True,
    split_on_sentences=False  # Not needed for this logic
):
    print("Processing captions with time...")
    wordLocationToTime = getTimestampMapping(whisper_analysis)
    position = 0
    start_time = 0
    CaptionsPairs = []
    text = whisper_analysis['text']

    # Find sentence boundaries (start indices in the text)
    sentence_endings = [m.end() for m in re.finditer(r'[.!?]', text)]
    sentence_starts = [0] + [i+1 for i in sentence_endings if i+1 < len(text)]
    sentence_starts_set = set(sentence_starts)

    words = text.split()
    idx_in_text = 0
    chunk_words = []
    chunk_start_in_text = 0

    for i, word in enumerate(words):
        # Find the index of this word in the original text
        idx_in_text = text.find(word, idx_in_text)
        # If this word is the start of a sentence (except for the first word), and we already have words in chunk, flush the chunk
        if i > 0 and idx_in_text in sentence_starts_set and chunk_words:
            # End the current caption at the previous word (end of previous sentence)
            caption = " ".join(chunk_words) if preserve_punctuation else cleanWord(" ".join(chunk_words))
            position += len(caption) + 1
            end_time = interpolateTimeFromDict(position, wordLocationToTime)
            if end_time:
                CaptionsPairs.append(((start_time, end_time), caption))
                start_time = end_time
            chunk_words = []
            chunk_start_in_text = idx_in_text
        chunk_words.append(word)
        # If adding the next word would exceed maxCaptionSize, flush the chunk
        if (i + 1 < len(words)):
            next_word = words[i+1]
            # Check if next word is the start of a sentence
            next_idx_in_text = text.find(next_word, idx_in_text + len(word))
            if len(" ".join(chunk_words + [next_word])) > maxCaptionSize or (next_idx_in_text in sentence_starts_set and chunk_words):
                caption = " ".join(chunk_words) if preserve_punctuation else cleanWord(" ".join(chunk_words))
                position += len(caption) + 1
                end_time = interpolateTimeFromDict(position, wordLocationToTime)
                if end_time:
                    CaptionsPairs.append(((start_time, end_time), caption))
                    start_time = end_time
                chunk_words = []
                chunk_start_in_text = next_idx_in_text
    # Add any remaining words as the last caption
    if chunk_words:
        caption = " ".join(chunk_words) if preserve_punctuation else cleanWord(" ".join(chunk_words))
        position += len(caption) + 1
        end_time = interpolateTimeFromDict(position, wordLocationToTime)
        if end_time:
            CaptionsPairs.append(((start_time, end_time), caption))
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
