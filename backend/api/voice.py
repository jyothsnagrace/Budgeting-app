# CHECKPOINT_4_MULTIMODAL_INPUT
"""
Voice Input Service
===================
Speech-to-text using OpenAI Whisper (local or API).
"""

import io
import os
import tempfile
from typing import Optional, Literal
from pathlib import Path

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_RECORDING_AVAILABLE = True
except ImportError:
    AUDIO_RECORDING_AVAILABLE = False

from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("voice_input")


class VoiceInputService:
    """
    Service for handling voice input using Whisper STT.
    
    Supports multiple modes:
    1. Local Whisper (openai-whisper) - FREE, runs locally
    2. Groq Whisper API - FREE tier available
    3. OpenAI Whisper API - Pay-per-use
    """
    
    def __init__(self, mode: Literal["local", "groq", "openai"] = "local"):
        self.mode = mode
        self.model = None
        
        if mode == "local":
            self._initialize_local_whisper()
        
        logger.info(f"VoiceInputService initialized in {mode} mode")
    
    def _initialize_local_whisper(self):
        """Initialize local Whisper model"""
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "openai-whisper not installed. Install with: pip install openai-whisper"
            )
        
        try:
            # Use base model for speed/accuracy balance
            # Options: tiny, base, small, medium, large
            model_size = settings.WHISPER_MODEL_SIZE if hasattr(settings, 'WHISPER_MODEL_SIZE') else "base"
            
            logger.info(f"Loading Whisper model: {model_size}")
            self.model = whisper.load_model(model_size)
            logger.info("✓ Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe_audio_file(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file (wav, mp3, m4a, etc.)
        
        Returns:
            Transcribed text
        """
        if self.mode == "local":
            return await self._transcribe_local(audio_file_path)
        elif self.mode == "groq":
            return await self._transcribe_groq(audio_file_path)
        elif self.mode == "openai":
            return await self._transcribe_openai(audio_file_path)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    async def _transcribe_local(self, audio_file_path: str) -> str:
        """Transcribe using local Whisper model"""
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_file_path,
                language="en",  # Can be None for auto-detection
                fp16=False  # Use fp32 for CPU compatibility
            )
            
            text = result["text"].strip()
            logger.info(f"Transcription result: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"Local transcription failed: {e}")
            raise
    
    async def _transcribe_groq(self, audio_file_path: str) -> str:
        """Transcribe using Groq Whisper API (FREE tier)"""
        try:
            from groq import Groq
            
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            with open(audio_file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    language="en"
                )
            
            text = transcription.text.strip()
            logger.info(f"Groq transcription: {text}")
            return text
            
        except ImportError:
            logger.error("groq package not installed. Install with: pip install groq")
            raise
        except Exception as e:
            logger.error(f"Groq transcription failed: {e}")
            raise
    
    async def _transcribe_openai(self, audio_file_path: str) -> str:
        """Transcribe using OpenAI Whisper API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            with open(audio_file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            
            text = transcription.text.strip()
            logger.info(f"OpenAI transcription: {text}")
            return text
            
        except ImportError:
            logger.error("openai package not installed. Install with: pip install openai")
            raise
        except Exception as e:
            logger.error(f"OpenAI transcription failed: {e}")
            raise
    
    async def transcribe_audio_bytes(self, audio_bytes: bytes, format: str = "wav") -> str:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Audio data as bytes
            format: Audio format (wav, mp3, m4a, etc.)
        
        Returns:
            Transcribed text
        """
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        try:
            # Transcribe
            text = await self.transcribe_audio_file(temp_path)
            return text
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def record_audio(
        self,
        duration: int = 5,
        sample_rate: int = 16000
    ) -> str:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            sample_rate: Sample rate in Hz (16000 is recommended for Whisper)
        
        Returns:
            Path to recorded audio file
        """
        if not AUDIO_RECORDING_AVAILABLE:
            raise ImportError(
                "Audio recording not available. Install with: "
                "pip install sounddevice soundfile numpy"
            )
        
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            
            # Record audio
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()  # Wait for recording to finish
            
            # Save to temporary file
            temp_path = os.path.join(
                tempfile.gettempdir(),
                f"recording_{os.getpid()}.wav"
            )
            
            sf.write(temp_path, audio, sample_rate)
            logger.info(f"✓ Audio recorded: {temp_path}")
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Audio recording failed: {e}")
            raise


# ============================================
# Singleton Instance
# ============================================

_voice_service: Optional[VoiceInputService] = None


def get_voice_service(mode: str = "local") -> VoiceInputService:
    """Get voice input service singleton"""
    global _voice_service
    
    if _voice_service is None:
        _voice_service = VoiceInputService(mode=mode)
    
    return _voice_service


# ============================================
# Convenience Functions
# ============================================

async def transcribe_audio(audio_file_path: str, mode: str = "local") -> str:
    """
    Convenience function to transcribe audio file.
    
    Args:
        audio_file_path: Path to audio file
        mode: Transcription mode (local, groq, openai)
    
    Returns:
        Transcribed text
    """
    service = get_voice_service(mode)
    return await service.transcribe_audio_file(audio_file_path)


async def transcribe_recording(duration: int = 5, mode: str = "local") -> str:
    """
    Convenience function to record and transcribe audio.
    
    Args:
        duration: Recording duration in seconds
        mode: Transcription mode (local, groq, openai)
    
    Returns:
        Transcribed text
    """
    service = get_voice_service(mode)
    
    # Record audio
    audio_path = service.record_audio(duration)
    
    try:
        # Transcribe
        text = await service.transcribe_audio_file(audio_path)
        return text
    finally:
        # Clean up recording
        try:
            os.unlink(audio_path)
        except:
            pass
