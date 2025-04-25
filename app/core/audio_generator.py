import os
import edge_tts
# from loguru import logger
from app.services.kokoro_service import kokoro_client

VOICE_PROVIDER = os.getenv('VOICE_PROVIDER', 'kokoro')  # Kokoro is default

async def generate_audio(text, output_filename):
    print("Generating audio...")
    try:
        if VOICE_PROVIDER == 'edge':
            communicate = edge_tts.Communicate(text, "en-AU-WilliamNeural")
            await communicate.save(output_filename)
            
        elif VOICE_PROVIDER == 'kokoro':
            voice_id = os.getenv('VOICE_ID', 'af_heart')
            speech_rate = float(os.getenv('SPEECH_RATE', '0.8'))
            
            # logger.debug(f"Using Kokoro TTS for: {text[:50]}...")
            audio_data = await kokoro_client.create_speech(
                text=text,
                voice=voice_id,
                speed=speech_rate,
                response_format="wav"
            )
            if not audio_data:
                # logger.error("Kokoro service failed to generate audio, falling back to edge-tts")
                communicate = edge_tts.Communicate(text, "en-AU-WilliamNeural")
                await communicate.save(output_filename)
                return
                
            # Save the audio bytes to file
            with open(output_filename, 'wb') as f:
                f.write(audio_data)
            # logger.success(f"Audio generated successfully: {output_filename}")
            
        else:
            raise ValueError(f"Unsupported voice provider: {VOICE_PROVIDER}")
            
    except Exception as e:
        print(f"Error generating audio: {e}")
        raise





