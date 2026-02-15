# CHECKPOINT_4_MULTIMODAL_INPUT
"""
Voice API Endpoints
===================
REST endpoints for voice input processing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from backend.api.voice import get_voice_service, VoiceInputService
from backend.utils.logger import get_logger

logger = get_logger("voice_api")
router = APIRouter(prefix="/voice", tags=["voice"])


# ============================================
# Request/Response Models
# ============================================

class TranscriptionResponse(BaseModel):
    """Response model for transcription"""
    text: str
    success: bool
    processing_time_ms: Optional[float] = None


class VoiceExpenseRequest(BaseModel):
    """Request to process voice input as expense"""
    text: str
    user_id: str


# ============================================
# Voice Endpoints
# ============================================

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    mode: str = "local"
):
    """
    Transcribe uploaded audio file to text.
    
    Supports: wav, mp3, m4a, webm, ogg
    
    Parameters:
        audio_file: Audio file to transcribe
        mode: Transcription mode (local, groq, openai)
    """
    import time
    start_time = time.time()
    
    try:
        # Get voice service
        voice_service = get_voice_service(mode)
        
        # Read audio bytes
        audio_bytes = await audio_file.read()
        
        # Get file extension
        filename = audio_file.filename or "audio.wav"
        format = filename.split(".")[-1] if "." in filename else "wav"
        
        logger.info(f"Transcribing audio file: {filename} ({len(audio_bytes)} bytes)")
        
        # Transcribe
        text = await voice_service.transcribe_audio_bytes(
            audio_bytes,
            format=format
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"✓ Transcription complete: {text}")
        
        return TranscriptionResponse(
            text=text,
            success=True,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/record-and-transcribe", response_model=TranscriptionResponse)
async def record_and_transcribe(
    duration: int = 5,
    mode: str = "local"
):
    """
    Record audio from server microphone and transcribe.
    
    Note: This only works if the server has a microphone.
    For production, use the /transcribe endpoint with client-recorded audio.
    
    Parameters:
        duration: Recording duration in seconds (1-30)
        mode: Transcription mode (local, groq, openai)
    """
    import time
    start_time = time.time()
    
    # Validate duration
    if not (1 <= duration <= 30):
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 1 and 30 seconds"
        )
    
    try:
        from backend.api.voice import transcribe_recording
        
        logger.info(f"Recording audio for {duration} seconds...")
        
        # Record and transcribe
        text = await transcribe_recording(duration, mode)
        
        processing_time = (time.time() - start_time) * 1000
        
        return TranscriptionResponse(
            text=text,
            success=True,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Recording/transcription failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Recording failed: {str(e)}"
        )


@router.get("/health")
async def voice_health_check():
    """Check if voice service is available"""
    try:
        service = get_voice_service()
        return {
            "status": "healthy",
            "mode": service.mode,
            "model_loaded": service.model is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
