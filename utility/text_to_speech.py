import os
from utility.services.kokoro_tts.kokoro_service import kokoro_client

VOICE_PROVIDER = os.getenv('VOICE_PROVIDER', 'kokoro')

async def generate_speech(text: str) -> bytes:
    """Generate speech using configured TTS provider."""
    if VOICE_PROVIDER != 'kokoro':
        raise NotImplementedError(f"Voice provider {VOICE_PROVIDER} not implemented")
        
    audio_data = await kokoro_client.create_speech(
        text=text,
        voice="af_heart",
        speed=0.8,
        response_format="mp3"
    )
    return audio_data
