# -*- coding: utf-8 -*-
import os, base64, json, requests, mimetypes, uuid, time
from typing import Optional, Dict, Any
from services.core.api_config import GEMINI_IMAGE_MODEL, gemini_image_endpoint, IMAGE_GEN_TIMEOUT
from services.core.key_manager import get_all_keys, refresh


class ImageGenError(Exception):
    """Image generation error"""
    pass


def generate_image_gemini(prompt: str, timeout: int = None, retry_delay: float = 5.0, log_callback=None) -> bytes:
    """
    Generate image using Gemini Flash Image model with SMART rate limiting
    
    FIXED: Add 5-second delay between key switches to prevent instant exhaustion
    
    Args:
        prompt: Text prompt for image generation
        timeout: Request timeout in seconds (default from api_config)
        retry_delay: Delay between key switches (5.0s for rate limiting)
        log_callback: Optional callback function for logging (receives string messages)
        
    Returns:
        Generated image as bytes
        
    Raises:
        ImageGenError: If generation fails
    """
    def log(msg):
        if log_callback:
            log_callback(msg)
    
    timeout = timeout or IMAGE_GEN_TIMEOUT
    refresh()
    keys = get_all_keys('google')
    if not keys:
        raise ImageGenError("No Google API keys available")
    
    log(f"[DEBUG] Tìm thấy {len(keys)} Google API keys")
    
    last_error = None
    for key_idx, api_key in enumerate(keys):
        try:
            # CRITICAL FIX: Add delay between key switches
            if key_idx > 0:
                log(f"[INFO] Chờ {retry_delay}s trước khi thử key tiếp theo...")
                time.sleep(retry_delay)
            
            key_preview = f"...{api_key[-6:]}\