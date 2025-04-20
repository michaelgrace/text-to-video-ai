import torch
import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
from config.settings import settings

def generate_timed_captions(audio_filename, model_size=settings.WHISPER_MODEL_SIZE):
    # DTW used internally by whisper_timestamped to align transcribed text with audio timestamps
    WHISPER_MODEL = load_model(model_size)
   
    gen = transcribe_timestamped(
        WHISPER_MODEL, 
        audio_filename, 
        verbose=settings.WHISPER_VERBOSE, 
        fp16=settings.WHISPER_FP16_ENABLED
    )
   
    return getCaptionsWithTime(gen)

def splitWordsByChars(words, maxCaptionChars):  # Renamed for clarity
    halfLength = maxCaptionChars / 2
    captions = []
    while words:
        caption = words[0]
        words = words[1:]
        while words and len(caption + ' ' + words[0]) <= maxCaptionChars:
            caption += ' ' + words[0]
            words = words[1:]
            if len(caption) >= halfLength and words:
                break
        captions.append(caption)
    return captions

def getTimestampMapping(whisper_analysis):
   
    index = 0
    locationToTimestamp = {}
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            newIndex = index + len(word['text'])+1
            locationToTimestamp[(index, newIndex)] = word['end']
            index = newIndex
    return locationToTimestamp

def cleanWord(word):
    return re.sub(settings.WORD_CLEANING_PATTERN, '', word)

def interpolateTimeFromDict(word_position, d):
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

def getCaptionsWithTime(whisper_analysis, maxCaptionChars=settings.MAX_CAPTION_CHARS, considerPunctuation=False):
    # Here's where caption splitting happens
    wordLocationToTime = getTimestampMapping(whisper_analysis)
    position = 0
    start_time = 0
    CaptionsPairs = []
    text = whisper_analysis['text']
    
    if considerPunctuation:
        sentences = re.split(settings.SENTENCE_SPLIT_PATTERN, text)
        words = [word for sentence in sentences 
                for word in splitWordsByChars(sentence.split(), maxCaptionChars)]
    else:
        words = text.split()
        words = [cleanWord(word) for word in splitWordsByChars(words, maxCaptionChars)]
    
    for word in words:
        position += len(word) + 1
        end_time = interpolateTimeFromDict(position, wordLocationToTime)
        if end_time and word:
            CaptionsPairs.append(((start_time, end_time), word))
            start_time = end_time

    return CaptionsPairs
