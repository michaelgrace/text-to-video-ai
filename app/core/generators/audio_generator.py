import os
import edge_tts
from loguru import logger
from app.core.services.kokoro_service import kokoro_client
from config.settings import settings

VOICE_PROVIDER = settings.VOICE_PROVIDER  # Kokoro is default

async def generate_audio(text, output_filename):
    """Generate audio using configured provider"""
    logger.info(f"Generating audio using {VOICE_PROVIDER} provider")
    
    try:
        if VOICE_PROVIDER == 'edge':
            communicate = edge_tts.Communicate(text, settings.FALLBACK_VOICE)
            await communicate.save(output_filename)
            
        elif VOICE_PROVIDER == 'kokoro':
            logger.debug(f"Using Kokoro TTS for: {text[:50]}...")
            audio_data = await kokoro_client.create_speech(
                text=text,
                voice=settings.DEFAULT_VOICE,
                speed=settings.DEFAULT_VOICE_SPEED,
                response_format="mp3"
            )
            if not audio_data:
                logger.error("Kokoro service failed to generate audio, falling back to edge-tts")
                communicate = edge_tts.Communicate(text, settings.FALLBACK_VOICE)
                await communicate.save(output_filename)
                return
                
            # Save the audio bytes to file
            with open(output_filename, 'wb') as f:
                f.write(audio_data)
            logger.success(f"Audio generated successfully: {output_filename}")
            
        else:
            raise ValueError(f"Unsupported voice provider: {VOICE_PROVIDER}")
            
    except Exception as e:
        logger.exception(f"Error generating audio: {e}")
        raise





