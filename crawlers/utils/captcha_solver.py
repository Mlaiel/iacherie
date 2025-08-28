"""
CAPTCHA Solver Module
=====================

Professional CAPTCHA solving capabilities for web crawling operations.
Implements multiple solving strategies and external service integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

import base64
import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import cv2
import numpy as np
from PIL import Image
import io
import json
import hashlib
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class CaptchaType(Enum):
    """CAPTCHA type classification."""
    TEXT_BASED = "text_based"
    IMAGE_RECOGNITION = "image_recognition"
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    CLOUDFLARE = "cloudflare"
    FUNCAPTCHA = "funcaptcha"
    GEETEST = "geetest"
    AUDIO_CAPTCHA = "audio_captcha"
    MATH_CAPTCHA = "math_captcha"
    SLIDER_CAPTCHA = "slider_captcha"
    UNKNOWN = "unknown"

@dataclass
class CaptchaChallenge:
    """CAPTCHA challenge data structure."""
    captcha_type: CaptchaType
    challenge_data: Union[str, bytes, Dict]
    site_key: Optional[str] = None
    page_url: Optional[str] = None
    challenge_id: Optional[str] = None
    additional_params: Dict = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}
        if self.challenge_id is None:
            self.challenge_id = self._generate_challenge_id()
    
    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID."""
        data = f"{self.captcha_type.value}_{self.site_key}_{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()

@dataclass
class CaptchaSolution:
    """CAPTCHA solution result."""
    success: bool
    solution: Optional[str] = None
    confidence: float = 0.0
    solving_time: float = 0.0
    solver_used: str = "unknown"
    error_message: Optional[str] = None
    additional_data: Dict = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}

class CaptchaDetector:
    """
    CAPTCHA detection and classification.
    
    Features:
    - Automatic CAPTCHA type detection
    - DOM analysis for CAPTCHA elements
    - Image-based CAPTCHA recognition
    - reCAPTCHA and hCaptcha detection
    """
    
    def __init__(self):
        """Initialize CAPTCHA detector."""
        self.captcha_patterns = {
            'recaptcha_v2': [
                r'g-recaptcha',
                r'recaptcha.*?sitekey',
                r'www\.google\.com/recaptcha'
            ],
            'recaptcha_v3': [
                r'grecaptcha\.execute',
                r'recaptcha.*?v3',
                r'action.*?recaptcha'
            ],
            'hcaptcha': [
                r'h-captcha',
                r'hcaptcha.*?sitekey',
                r'hcaptcha\.com'
            ],
            'cloudflare': [
                r'cf-challenge',
                r'cloudflare.*?challenge',
                r'cf-ray'
            ],
            'funcaptcha': [
                r'funcaptcha',
                r'arkoselabs',
                r'enforcement\.arkoselabs\.com'
            ],
            'geetest': [
                r'geetest',
                r'gt-captcha',
                r'geetest\.com'
            ]
        }
    
    async def detect_captcha(self, html_content: str, page_url: str) -> List[CaptchaChallenge]:
        """Detect CAPTCHAs in HTML content."""
        detected_captchas = []
        
        try:
            # Check for known CAPTCHA patterns
            for captcha_type, patterns in self.captcha_patterns.items():
                for pattern in patterns:
                    import re
                    if re.search(pattern, html_content, re.IGNORECASE):
                        challenge = await self._extract_captcha_details(
                            html_content, captcha_type, page_url
                        )
                        if challenge:
                            detected_captchas.append(challenge)
                        break
            
            # Check for image-based CAPTCHAs
            image_captcha = await self._detect_image_captcha(html_content, page_url)
            if image_captcha:
                detected_captchas.append(image_captcha)
            
        except Exception as e:
            logger.error(f"CAPTCHA detection error: {e}")
        
        return detected_captchas
    
    async def _extract_captcha_details(
        self, 
        html_content: str, 
        captcha_type: str, 
        page_url: str
    ) -> Optional[CaptchaChallenge]:
        """Extract CAPTCHA details from HTML."""
        try:
            import re
            
            if captcha_type in ['recaptcha_v2', 'recaptcha_v3']:
                # Extract site key
                sitekey_match = re.search(
                    r'data-sitekey=["\']([^"\']+)["\']|sitekey:\s*["\']([^"\']+)["\']',
                    html_content, re.IGNORECASE
                )
                
                if sitekey_match:
                    site_key = sitekey_match.group(1) or sitekey_match.group(2)
                    captcha_enum = CaptchaType.RECAPTCHA_V2 if 'v2' in captcha_type else CaptchaType.RECAPTCHA_V3
                    
                    return CaptchaChallenge(
                        captcha_type=captcha_enum,
                        challenge_data=html_content,
                        site_key=site_key,
                        page_url=page_url
                    )
            
            elif captcha_type == 'hcaptcha':
                sitekey_match = re.search(
                    r'data-sitekey=["\']([^"\']+)["\']',
                    html_content, re.IGNORECASE
                )
                
                if sitekey_match:
                    site_key = sitekey_match.group(1)
                    return CaptchaChallenge(
                        captcha_type=CaptchaType.HCAPTCHA,
                        challenge_data=html_content,
                        site_key=site_key,
                        page_url=page_url
                    )
            
            # Add more CAPTCHA type extractions as needed
            
        except Exception as e:
            logger.error(f"CAPTCHA detail extraction error: {e}")
        
        return None
    
    async def _detect_image_captcha(self, html_content: str, page_url: str) -> Optional[CaptchaChallenge]:
        """Detect image-based CAPTCHAs."""
        try:
            import re
            
            # Look for CAPTCHA images
            img_patterns = [
                r'<img[^>]*captcha[^>]*src=["\']([^"\']+)["\']',
                r'<img[^>]*src=["\']([^"\']*captcha[^"\']*)["\']',
                r'<img[^>]*verification[^>]*src=["\']([^"\']+)["\']'
            ]
            
            for pattern in img_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    img_url = match.group(1)
                    
                    # Make URL absolute
                    if img_url.startswith('/'):
                        from urllib.parse import urljoin
                        img_url = urljoin(page_url, img_url)
                    
                    return CaptchaChallenge(
                        captcha_type=CaptchaType.IMAGE_RECOGNITION,
                        challenge_data=img_url,
                        page_url=page_url
                    )
            
        except Exception as e:
            logger.error(f"Image CAPTCHA detection error: {e}")
        
        return None

class BaseCaptchaSolver:
    """Base class for CAPTCHA solvers."""
    
    def __init__(self, name: str):
        """Initialize solver."""
        self.name = name
        self.success_rate = 0.0
        self.average_solve_time = 0.0
        self.total_attempts = 0
        self.successful_attempts = 0
    
    async def solve(self, challenge: CaptchaChallenge) -> CaptchaSolution:
        """Solve CAPTCHA challenge - base implementation."""
        try:
            import time
            start_time = time.time()
            
            logger.info(f"Attempting to solve CAPTCHA challenge {challenge.challenge_id} with {self.name}")
            
            # Basic implementation - simulate solving
            if not self.can_solve(challenge.captcha_type):
                return CaptchaSolution(
                    challenge_id=challenge.challenge_id,
                    success=False,
                    error="Solver cannot handle this CAPTCHA type",
                    solve_time=time.time() - start_time,
                    solver_name=self.name
                )
            
            # Simulate solving time
            import asyncio
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Basic solution - for demonstration only
            solution_text = "simulated_solution"
            confidence = 0.8  # 80% confidence
            
            solve_time = time.time() - start_time
            success = True  # Simulate success
            
            # Update statistics
            self._update_statistics(success, solve_time)
            
            result = CaptchaSolution(
                challenge_id=challenge.challenge_id,
                solution=solution_text,
                confidence=confidence,
                success=success,
                solve_time=solve_time,
                solver_name=self.name,
                metadata={
                    "simulated": True,
                    "captcha_type": challenge.captcha_type.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"CAPTCHA solved successfully in {solve_time:.3f}s with confidence {confidence:.2f}")
            return result
            
        except Exception as e:
            solve_time = time.time() - start_time
            logger.error(f"Error solving CAPTCHA: {str(e)}")
            
            # Update statistics
            self._update_statistics(False, solve_time)
            
            return CaptchaSolution(
                challenge_id=challenge.challenge_id,
                success=False,
                error=str(e),
                solve_time=solve_time,
                solver_name=self.name
            )
    
    def can_solve(self, captcha_type: CaptchaType) -> bool:
        """Check if solver can handle this CAPTCHA type - base implementation."""
        # Basic implementation supports most common types
        supported_types = {
            CaptchaType.TEXT,
            CaptchaType.IMAGE,
            CaptchaType.AUDIO,
            CaptchaType.MATH
        }
        
        can_handle = captcha_type in supported_types
        logger.debug(f"Solver {self.name} {'can' if can_handle else 'cannot'} handle {captcha_type.value}")
        
        return can_handle
    
    def _update_statistics(self, success: bool, solve_time: float) -> None:
        """Update solver statistics."""
        self.total_attempts += 1
        if success:
            self.successful_attempts += 1
        
        self.success_rate = self.successful_attempts / self.total_attempts
        
        # Update average solve time
        if self.total_attempts == 1:
            self.average_solve_time = solve_time
        else:
            self.average_solve_time = (
                (self.average_solve_time * (self.total_attempts - 1) + solve_time) /
                self.total_attempts
            )

class ImageCaptchaSolver(BaseCaptchaSolver):
    """
    Image-based CAPTCHA solver using computer vision.
    
    Features:
    - OCR for text CAPTCHAs
    - Object recognition
    - Preprocessing and enhancement
    - Machine learning classification
    """
    
    def __init__(self):
        """Initialize image CAPTCHA solver."""
        super().__init__("ImageCaptchaSolver")
        self.supported_types = {
            CaptchaType.TEXT_BASED,
            CaptchaType.IMAGE_RECOGNITION,
            CaptchaType.MATH_CAPTCHA
        }
    
    def can_solve(self, captcha_type: CaptchaType) -> bool:
        """Check if can solve this type."""
        return captcha_type in self.supported_types
    
    async def solve(self, challenge: CaptchaChallenge) -> CaptchaSolution:
        """Solve image-based CAPTCHA."""
        start_time = time.time()
        
        try:
            if isinstance(challenge.challenge_data, str):
                # Download image
                image_data = await self._download_image(challenge.challenge_data)
            else:
                image_data = challenge.challenge_data
            
            if not image_data:
                return CaptchaSolution(
                    success=False,
                    error_message="Failed to download CAPTCHA image",
                    solver_used=self.name
                )
            
            # Process image
            processed_image = self._preprocess_image(image_data)
            
            # Extract text using OCR
            solution_text = self._extract_text(processed_image)
            
            solve_time = time.time() - start_time
            success = bool(solution_text)
            
            self._update_statistics(success, solve_time)
            
            return CaptchaSolution(
                success=success,
                solution=solution_text,
                confidence=0.8 if success else 0.0,
                solving_time=solve_time,
                solver_used=self.name
            )
            
        except Exception as e:
            solve_time = time.time() - start_time
            self._update_statistics(False, solve_time)
            
            return CaptchaSolution(
                success=False,
                error_message=str(e),
                solving_time=solve_time,
                solver_used=self.name
            )
    
    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download CAPTCHA image."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception as e:
            logger.error(f"Failed to download CAPTCHA image: {e}")
        
        return None
    
    def _preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Preprocess CAPTCHA image for better OCR."""
        try:
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply preprocessing
            # 1. Noise reduction
            img_array = cv2.medianBlur(img_array, 3)
            
            # 2. Threshold to binary
            _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 3. Morphological operations to clean up
            kernel = np.ones((2, 2), np.uint8)
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
            
            # 4. Resize for better OCR
            height, width = img_array.shape
            if height < 50 or width < 100:
                scale_factor = max(50 / height, 100 / width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return np.array([])
    
    def _extract_text(self, image: np.ndarray) -> Optional[str]:
        """Extract text from preprocessed image using OCR."""
        try:
            import pytesseract
            
            # Configure Tesseract for CAPTCHA
            config = '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            
            # Extract text
            text = pytesseract.image_to_string(image, config=config)
            
            # Clean extracted text
            text = ''.join(char for char in text if char.isalnum())
            
            return text if text else None
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return None

class ExternalCaptchaSolver(BaseCaptchaSolver):
    """
    External CAPTCHA solving service integration.
    
    Supports services like:
    - 2captcha
    - AntiCaptcha
    - DeathByCaptcha
    - CapMonster
    """
    
    def __init__(self, service_name: str, api_key: str):
        """Initialize external solver."""
        super().__init__(f"External_{service_name}")
        self.service_name = service_name
        self.api_key = api_key
        self.service_config = self._get_service_config(service_name)
    
    def _get_service_config(self, service_name: str) -> Dict:
        """Get configuration for external service."""
        configs = {
            '2captcha': {
                'submit_url': 'http://2captcha.com/in.php',
                'result_url': 'http://2captcha.com/res.php',
                'supported_types': {
                    CaptchaType.RECAPTCHA_V2,
                    CaptchaType.RECAPTCHA_V3,
                    CaptchaType.HCAPTCHA,
                    CaptchaType.IMAGE_RECOGNITION,
                    CaptchaType.TEXT_BASED
                }
            },
            'anticaptcha': {
                'api_url': 'https://api.anti-captcha.com',
                'supported_types': {
                    CaptchaType.RECAPTCHA_V2,
                    CaptchaType.RECAPTCHA_V3,
                    CaptchaType.HCAPTCHA,
                    CaptchaType.FUNCAPTCHA
                }
            }
        }
        
        return configs.get(service_name.lower(), {})
    
    def can_solve(self, captcha_type: CaptchaType) -> bool:
        """Check if service supports this CAPTCHA type."""
        supported_types = self.service_config.get('supported_types', set())
        return captcha_type in supported_types
    
    async def solve(self, challenge: CaptchaChallenge) -> CaptchaSolution:
        """Solve CAPTCHA using external service."""
        start_time = time.time()
        
        try:
            if self.service_name.lower() == '2captcha':
                return await self._solve_2captcha(challenge, start_time)
            elif self.service_name.lower() == 'anticaptcha':
                return await self._solve_anticaptcha(challenge, start_time)
            else:
                return CaptchaSolution(
                    success=False,
                    error_message=f"Unsupported service: {self.service_name}",
                    solver_used=self.name
                )
                
        except Exception as e:
            solve_time = time.time() - start_time
            self._update_statistics(False, solve_time)
            
            return CaptchaSolution(
                success=False,
                error_message=str(e),
                solving_time=solve_time,
                solver_used=self.name
            )
    
    async def _solve_2captcha(self, challenge: CaptchaChallenge, start_time: float) -> CaptchaSolution:
        """Solve using 2captcha service."""
        try:
            async with aiohttp.ClientSession() as session:
                # Submit CAPTCHA
                submit_data = {
                    'key': self.api_key,
                    'method': self._get_2captcha_method(challenge.captcha_type),
                    'pageurl': challenge.page_url
                }
                
                if challenge.captcha_type in [CaptchaType.RECAPTCHA_V2, CaptchaType.RECAPTCHA_V3]:
                    submit_data['googlekey'] = challenge.site_key
                elif challenge.captcha_type == CaptchaType.HCAPTCHA:
                    submit_data['sitekey'] = challenge.site_key
                
                # Submit
                async with session.post(self.service_config['submit_url'], data=submit_data) as response:
                    submit_result = await response.text()
                    
                    if not submit_result.startswith('OK|'):
                        raise Exception(f"Submit failed: {submit_result}")
                    
                    captcha_id = submit_result.split('|')[1]
                
                # Wait for solution
                max_wait_time = 120  # 2 minutes
                check_interval = 5   # 5 seconds
                
                for _ in range(max_wait_time // check_interval):
                    await asyncio.sleep(check_interval)
                    
                    result_data = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': captcha_id
                    }
                    
                    async with session.get(self.service_config['result_url'], params=result_data) as response:
                        result = await response.text()
                        
                        if result == 'CAPCHA_NOT_READY':
                            continue
                        elif result.startswith('OK|'):
                            solution = result.split('|')[1]
                            solve_time = time.time() - start_time
                            
                            self._update_statistics(True, solve_time)
                            
                            return CaptchaSolution(
                                success=True,
                                solution=solution,
                                confidence=0.9,
                                solving_time=solve_time,
                                solver_used=self.name
                            )
                        else:
                            raise Exception(f"Solve failed: {result}")
                
                raise Exception("Timeout waiting for solution")
                
        except Exception as e:
            solve_time = time.time() - start_time
            self._update_statistics(False, solve_time)
            raise e
    
    def _get_2captcha_method(self, captcha_type: CaptchaType) -> str:
        """Get 2captcha method for CAPTCHA type."""
        method_map = {
            CaptchaType.RECAPTCHA_V2: 'userrecaptcha',
            CaptchaType.RECAPTCHA_V3: 'userrecaptcha',
            CaptchaType.HCAPTCHA: 'hcaptcha',
            CaptchaType.IMAGE_RECOGNITION: 'base64',
            CaptchaType.TEXT_BASED: 'base64'
        }
        return method_map.get(captcha_type, 'base64')

class CaptchaSolver:
    """
    Main CAPTCHA solver with multiple solving strategies.
    
    Features:
    - Multiple solver backends
    - Automatic solver selection
    - Fallback mechanisms
    - Performance optimization
    - Cost management
    """
    
    def __init__(self):
        """Initialize CAPTCHA solver."""
        self.solvers: List[BaseCaptchaSolver] = []
        self.detector = CaptchaDetector()
        self.solve_attempts = {}
        self.max_attempts_per_challenge = 3
    
    def add_solver(self, solver: BaseCaptchaSolver) -> None:
        """Add CAPTCHA solver backend."""
        self.solvers.append(solver)
        logger.info(f"Added CAPTCHA solver: {solver.name}")
    
    async def detect_and_solve(self, html_content: str, page_url: str) -> List[CaptchaSolution]:
        """Detect and solve all CAPTCHAs in content."""
        solutions = []
        
        try:
            # Detect CAPTCHAs
            challenges = await self.detector.detect_captcha(html_content, page_url)
            
            if not challenges:
                logger.debug("No CAPTCHAs detected")
                return solutions
            
            logger.info(f"Detected {len(challenges)} CAPTCHA(s)")
            
            # Solve each challenge
            for challenge in challenges:
                solution = await self.solve_challenge(challenge)
                solutions.append(solution)
            
        except Exception as e:
            logger.error(f"CAPTCHA detection and solving error: {e}")
        
        return solutions
    
    async def solve_challenge(self, challenge: CaptchaChallenge) -> CaptchaSolution:
        """Solve specific CAPTCHA challenge."""
        challenge_key = challenge.challenge_id
        
        # Check attempt count
        if challenge_key in self.solve_attempts:
            if self.solve_attempts[challenge_key] >= self.max_attempts_per_challenge:
                return CaptchaSolution(
                    success=False,
                    error_message="Max attempts exceeded",
                    solver_used="none"
                )
        else:
            self.solve_attempts[challenge_key] = 0
        
        # Select best solver
        best_solver = self._select_solver(challenge.captcha_type)
        if not best_solver:
            return CaptchaSolution(
                success=False,
                error_message=f"No solver available for {challenge.captcha_type.value}",
                solver_used="none"
            )
        
        # Attempt to solve
        self.solve_attempts[challenge_key] += 1
        
        logger.info(f"Solving {challenge.captcha_type.value} with {best_solver.name}")
        solution = await best_solver.solve(challenge)
        
        if solution.success:
            logger.info(f"CAPTCHA solved successfully in {solution.solving_time:.2f}s")
        else:
            logger.warning(f"CAPTCHA solving failed: {solution.error_message}")
        
        return solution
    
    def _select_solver(self, captcha_type: CaptchaType) -> Optional[BaseCaptchaSolver]:
        """Select best solver for CAPTCHA type."""
        # Filter solvers that can handle this type
        capable_solvers = [s for s in self.solvers if s.can_solve(captcha_type)]
        
        if not capable_solvers:
            return None
        
        # Sort by success rate and speed
        capable_solvers.sort(
            key=lambda s: (s.success_rate, -s.average_solve_time),
            reverse=True
        )
        
        return capable_solvers[0]
    
    def get_solver_statistics(self) -> Dict:
        """Get statistics for all solvers."""
        stats = {}
        
        for solver in self.solvers:
            stats[solver.name] = {
                'success_rate': solver.success_rate,
                'average_solve_time': solver.average_solve_time,
                'total_attempts': solver.total_attempts,
                'successful_attempts': solver.successful_attempts
            }
        
        return stats
    
    def clear_attempt_history(self) -> None:
        """Clear solve attempt history."""
        self.solve_attempts.clear()
        logger.info("Cleared CAPTCHA solve attempt history")

# Utility functions
def create_image_captcha_solver() -> ImageCaptchaSolver:
    """Create image CAPTCHA solver."""
    return ImageCaptchaSolver()

def create_2captcha_solver(api_key: str) -> ExternalCaptchaSolver:
    """Create 2captcha external solver."""
    return ExternalCaptchaSolver('2captcha', api_key)

def create_anticaptcha_solver(api_key: str) -> ExternalCaptchaSolver:
    """Create AntiCaptcha external solver."""
    return ExternalCaptchaSolver('anticaptcha', api_key)

def setup_default_captcha_solver(
    external_api_keys: Optional[Dict[str, str]] = None
) -> CaptchaSolver:
    """Setup CAPTCHA solver with default configuration."""
    solver = CaptchaSolver()
    
    # Add image solver
    solver.add_solver(create_image_captcha_solver())
    
    # Add external solvers if API keys provided
    if external_api_keys:
        if '2captcha' in external_api_keys:
            solver.add_solver(create_2captcha_solver(external_api_keys['2captcha']))
        
        if 'anticaptcha' in external_api_keys:
            solver.add_solver(create_anticaptcha_solver(external_api_keys['anticaptcha']))
    
    return solver
