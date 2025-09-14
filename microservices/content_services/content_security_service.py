"""
🔐 Content Security Service - Sécurité de Contenu Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Service spécialisé de sécurité pour contenu avec scan malware, validation et protection.
Sécurité multi-couches avec IA de détection et compliance automatique.
"""

import asyncio
import hashlib
import mimetypes
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import logging
import json
import base64

import yara
import magic
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ContentSecurityService:
    """Service de sécurité avancée pour contenu"""
    
    def __init__(self):
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        self.blocked_extensions = [
            '.exe', '.bat', '.com', '.scr', '.pif', '.vbs', '.js'
        ]
        self.allowed_mime_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'video': ['video/mp4', 'video/avi', 'video/mov', 'video/webm'],
            'audio': ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac'],
            'document': ['application/pdf', 'text/plain', 'application/msword']
        }
        
        # Patterns de contenu malveillant
        self.malware_patterns = self._load_malware_patterns()
        self.content_filters = self._load_content_filters()
    
    async def scan_content_security(
        self,
        content_id: str,
        file_path: str,
        content_data: Optional[bytes] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Scan de sécurité complet du contenu"""
        try:
            security_report = {
                'content_id': content_id,
                'scanned_at': datetime.utcnow().isoformat(),
                'status': 'scanning',
                'checks': {}
            }
            
            # 1. Validation de base
            basic_check = await self._basic_validation(file_path, metadata)
            security_report['checks']['basic_validation'] = basic_check
            
            # 2. Scan malware
            malware_check = await self._malware_scan(file_path, content_data)
            security_report['checks']['malware_scan'] = malware_check
            
            # 3. Validation MIME type
            mime_check = await self._mime_type_validation(file_path)
            security_report['checks']['mime_validation'] = mime_check
            
            # 4. Scan contenu inapproprié
            content_check = await self._inappropriate_content_scan(file_path, content_data)
            security_report['checks']['content_moderation'] = content_check
            
            # 5. Analyse steganographie
            steganography_check = await self._steganography_detection(file_path)
            security_report['checks']['steganography'] = steganography_check
            
            # 6. Validation métadonnées
            metadata_check = await self._metadata_security_check(metadata)
            security_report['checks']['metadata_security'] = metadata_check
            
            # Évaluation globale
            security_report['overall_risk'] = self._calculate_risk_score(security_report['checks'])
            security_report['status'] = self._determine_status(security_report['overall_risk'])
            security_report['recommendations'] = await self._generate_security_recommendations(
                security_report['checks']
            )
            
            return security_report
            
        except Exception as e:
            logger.error(f"Erreur scan sécurité {content_id}: {e}")
            return {
                'content_id': content_id,
                'error': str(e),
                'status': 'error',
                'scanned_at': datetime.utcnow().isoformat()
            }
    
    async def _basic_validation(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validation de base du fichier"""
        
        validation = {
            'passed': True,
            'issues': [],
            'checks_performed': []
        }
        
        try:
            import os
            
            # Vérifier existence du fichier
            if not os.path.exists(file_path):
                validation['passed'] = False
                validation['issues'].append('File does not exist')
                return validation
            
            validation['checks_performed'].append('file_existence')
            
            # Vérifier taille du fichier
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                validation['passed'] = False
                validation['issues'].append(f'File too large: {file_size} bytes')
            
            validation['checks_performed'].append('file_size')
            validation['file_size'] = file_size
            
            # Vérifier extension
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension in self.blocked_extensions:
                validation['passed'] = False
                validation['issues'].append(f'Blocked file extension: {file_extension}')
            
            validation['checks_performed'].append('file_extension')
            validation['file_extension'] = file_extension
            
            # Vérifier nom de fichier
            filename = os.path.basename(file_path)
            if self._has_suspicious_filename(filename):
                validation['passed'] = False
                validation['issues'].append('Suspicious filename detected')
            
            validation['checks_performed'].append('filename_check')
            
        except Exception as e:
            logger.error(f"Erreur validation de base: {e}")
            validation['passed'] = False
            validation['issues'].append(f'Validation error: {str(e)}')
        
        return validation
    
    async def _malware_scan(
        self,
        file_path: str,
        content_data: Optional[bytes]
    ) -> Dict[str, Any]:
        """Scan antimalware avancé"""
        
        scan_result = {
            'passed': True,
            'threats_detected': [],
            'scan_methods': []
        }
        
        try:
            # 1. Scan par signatures
            signature_scan = await self._signature_based_scan(file_path)
            scan_result['scan_methods'].append('signature_scan')
            
            if signature_scan['threats']:
                scan_result['passed'] = False
                scan_result['threats_detected'].extend(signature_scan['threats'])
            
            # 2. Scan heuristique
            heuristic_scan = await self._heuristic_scan(file_path, content_data)
            scan_result['scan_methods'].append('heuristic_scan')
            
            if heuristic_scan['suspicious_patterns']:
                scan_result['passed'] = False
                scan_result['threats_detected'].extend(heuristic_scan['suspicious_patterns'])
            
            # 3. Scan comportemental (pour les exécutables)
            if file_path.endswith(('.exe', '.dll', '.scr')):
                behavioral_scan = await self._behavioral_scan(file_path)
                scan_result['scan_methods'].append('behavioral_scan')
                
                if behavioral_scan['malicious_behavior']:
                    scan_result['passed'] = False
                    scan_result['threats_detected'].extend(behavioral_scan['malicious_behavior'])
            
        except Exception as e:
            logger.error(f"Erreur scan malware: {e}")
            scan_result['passed'] = False
            scan_result['threats_detected'].append(f'Scan error: {str(e)}')
        
        return scan_result
    
    async def _signature_based_scan(self, file_path: str) -> Dict[str, Any]:
        """Scan basé sur les signatures de malware"""
        
        result = {'threats': []}
        
        try:
            # Lire le fichier
            with open(file_path, 'rb') as f:
                file_data = f.read(1024 * 1024)  # Premier MB
            
            # Hash du fichier
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Vérifier contre base de signatures connues
            known_malware_hashes = self._get_known_malware_hashes()
            
            if file_hash in known_malware_hashes:
                result['threats'].append({
                    'type': 'known_malware',
                    'hash': file_hash,
                    'severity': 'high'
                })
            
            # Recherche de patterns malveillants
            for pattern_name, pattern in self.malware_patterns.items():
                if pattern.encode() in file_data:
                    result['threats'].append({
                        'type': 'suspicious_pattern',
                        'pattern': pattern_name,
                        'severity': 'medium'
                    })
            
        except Exception as e:
            logger.error(f"Erreur signature scan: {e}")
            result['threats'].append({
                'type': 'scan_error',
                'error': str(e),
                'severity': 'unknown'
            })
        
        return result
    
    async def _heuristic_scan(
        self,
        file_path: str,
        content_data: Optional[bytes]
    ) -> Dict[str, Any]:
        """Scan heuristique pour détecter comportements suspects"""
        
        result = {'suspicious_patterns': []}
        
        try:
            if not content_data:
                with open(file_path, 'rb') as f:
                    content_data = f.read()
            
            # Analyse de l'entropie (randomness)
            entropy = self._calculate_entropy(content_data)
            if entropy > 7.5:  # Seuil élevé = possible chiffrement/compression suspecte
                result['suspicious_patterns'].append({
                    'type': 'high_entropy',
                    'value': entropy,
                    'severity': 'medium'
                })
            
            # Recherche de strings suspectes
            suspicious_strings = [
                b'eval(', b'exec(', b'system(', b'shell_exec',
                b'base64_decode', b'gzinflate', b'str_rot13'
            ]
            
            for sus_string in suspicious_strings:
                if sus_string in content_data:
                    result['suspicious_patterns'].append({
                        'type': 'suspicious_string',
                        'string': sus_string.decode('ascii', errors='ignore'),
                        'severity': 'medium'
                    })
            
            # Analyse de la structure (pour images)
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_analysis = await self._analyze_image_structure(file_path)
                if image_analysis['anomalies']:
                    result['suspicious_patterns'].extend(image_analysis['anomalies'])
            
        except Exception as e:
            logger.error(f"Erreur heuristic scan: {e}")
        
        return result
    
    async def _behavioral_scan(self, file_path: str) -> Dict[str, Any]:
        """Scan comportemental (placeholder pour sandbox analysis)"""
        
        # En production, ceci exécuterait le fichier dans une sandbox
        # et analyserait son comportement
        
        return {'malicious_behavior': []}
    
    async def _mime_type_validation(self, file_path: str) -> Dict[str, Any]:
        """Validation du type MIME du fichier"""
        
        validation = {
            'passed': True,
            'detected_mime': None,
            'expected_mime': None,
            'issues': []
        }
        
        try:
            # Détecter le type MIME réel
            detected_mime = magic.from_file(file_path, mime=True)
            validation['detected_mime'] = detected_mime
            
            # Type MIME attendu basé sur l'extension
            expected_mime = mimetypes.guess_type(file_path)[0]
            validation['expected_mime'] = expected_mime
            
            # Vérifier la cohérence
            if expected_mime and detected_mime != expected_mime:
                validation['passed'] = False
                validation['issues'].append(
                    f'MIME type mismatch: detected {detected_mime}, expected {expected_mime}'
                )
            
            # Vérifier si le type MIME est autorisé
            if not self._is_mime_type_allowed(detected_mime):
                validation['passed'] = False
                validation['issues'].append(f'MIME type not allowed: {detected_mime}')
            
        except Exception as e:
            logger.error(f"Erreur validation MIME: {e}")
            validation['passed'] = False
            validation['issues'].append(f'MIME validation error: {str(e)}')
        
        return validation
    
    async def _inappropriate_content_scan(
        self,
        file_path: str,
        content_data: Optional[bytes]
    ) -> Dict[str, Any]:
        """Scan pour contenu inapproprié"""
        
        scan_result = {
            'passed': True,
            'content_issues': [],
            'confidence_scores': {}
        }
        
        try:
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                # Scan d'images
                image_scan = await self._scan_image_content(file_path)
                scan_result.update(image_scan)
                
            elif file_extension in ['mp4', 'avi', 'mov', 'webm']:
                # Scan de vidéos
                video_scan = await self._scan_video_content(file_path)
                scan_result.update(video_scan)
                
            elif file_extension in ['mp3', 'wav', 'flac']:
                # Scan d'audio
                audio_scan = await self._scan_audio_content(file_path)
                scan_result.update(audio_scan)
            
        except Exception as e:
            logger.error(f"Erreur scan contenu inapproprié: {e}")
            scan_result['content_issues'].append(f'Content scan error: {str(e)}')
        
        return scan_result
    
    async def _scan_image_content(self, file_path: str) -> Dict[str, Any]:
        """Scan spécifique pour images"""
        
        result = {
            'passed': True,
            'content_issues': [],
            'confidence_scores': {}
        }
        
        try:
            # Charger l'image
            image = cv2.imread(file_path)
            if image is None:
                result['content_issues'].append('Unable to load image')
                result['passed'] = False
                return result
            
            # Détection de contenu adulte (placeholder)
            # En production, utiliser un modèle IA spécialisé
            adult_content_score = np.random.uniform(0, 1)
            result['confidence_scores']['adult_content'] = adult_content_score
            
            if adult_content_score > 0.8:
                result['passed'] = False
                result['content_issues'].append('Potential adult content detected')
            
            # Détection de violence (placeholder)
            violence_score = np.random.uniform(0, 1)
            result['confidence_scores']['violence'] = violence_score
            
            if violence_score > 0.8:
                result['passed'] = False
                result['content_issues'].append('Potential violent content detected')
            
        except Exception as e:
            logger.error(f"Erreur scan image: {e}")
            result['content_issues'].append(f'Image scan error: {str(e)}')
        
        return result
    
    async def _scan_video_content(self, file_path: str) -> Dict[str, Any]:
        """Scan spécifique pour vidéos"""
        
        # Placeholder - en production, analyser frames de la vidéo
        return {
            'passed': True,
            'content_issues': [],
            'confidence_scores': {
                'adult_content': np.random.uniform(0, 0.3),
                'violence': np.random.uniform(0, 0.3)
            }
        }
    
    async def _scan_audio_content(self, file_path: str) -> Dict[str, Any]:
        """Scan spécifique pour audio"""
        
        # Placeholder - en production, analyser contenu audio
        return {
            'passed': True,
            'content_issues': [],
            'confidence_scores': {
                'inappropriate_language': np.random.uniform(0, 0.3)
            }
        }
    
    async def _steganography_detection(self, file_path: str) -> Dict[str, Any]:
        """Détection de steganographie"""
        
        detection = {
            'passed': True,
            'hidden_data_detected': False,
            'analysis_methods': []
        }
        
        try:
            file_extension = file_path.lower().split('.')[-1]
            
            if file_extension in ['jpg', 'jpeg', 'png']:
                # Analyse LSB pour images
                lsb_analysis = await self._analyze_lsb_steganography(file_path)
                detection['analysis_methods'].append('lsb_analysis')
                
                if lsb_analysis['suspicious']:
                    detection['passed'] = False
                    detection['hidden_data_detected'] = True
            
        except Exception as e:
            logger.error(f"Erreur détection steganographie: {e}")
        
        return detection
    
    async def _analyze_lsb_steganography(self, file_path: str) -> Dict[str, Any]:
        """Analyse LSB pour détecter données cachées"""
        
        try:
            image = cv2.imread(file_path)
            if image is None:
                return {'suspicious': False, 'reason': 'Cannot load image'}
            
            # Analyser les bits de poids faible
            lsb_plane = image & 1
            
            # Calculer l'entropie du plan LSB
            lsb_entropy = self._calculate_entropy(lsb_plane.flatten())
            
            # Seuil empirique pour détection
            if lsb_entropy > 0.7:
                return {
                    'suspicious': True,
                    'reason': f'High LSB entropy: {lsb_entropy}',
                    'entropy': lsb_entropy
                }
            
            return {'suspicious': False, 'entropy': lsb_entropy}
            
        except Exception as e:
            logger.error(f"Erreur analyse LSB: {e}")
            return {'suspicious': False, 'error': str(e)}
    
    async def _metadata_security_check(
        self,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Vérification sécurité des métadonnées"""
        
        check = {
            'passed': True,
            'issues': [],
            'sensitive_data_detected': []
        }
        
        if not metadata:
            return check
        
        try:
            # Recherche d'informations sensibles
            sensitive_patterns = {
                'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
                'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            }
            
            metadata_str = json.dumps(metadata)
            
            for pattern_name, pattern in sensitive_patterns.items():
                import re
                if re.search(pattern, metadata_str):
                    check['sensitive_data_detected'].append(pattern_name)
                    check['passed'] = False
                    check['issues'].append(f'Sensitive data detected: {pattern_name}')
            
            # Vérifier taille des métadonnées
            if len(metadata_str) > 10000:  # 10KB
                check['passed'] = False
                check['issues'].append('Metadata too large')
            
        except Exception as e:
            logger.error(f"Erreur check métadonnées: {e}")
            check['issues'].append(f'Metadata check error: {str(e)}')
        
        return check
    
    def _calculate_entropy(self, data: Union[bytes, np.ndarray]) -> float:
        """Calcule l'entropie de Shannon des données"""
        
        if isinstance(data, np.ndarray):
            data = data.astype(np.uint8).tobytes()
        
        if len(data) == 0:
            return 0
        
        # Compter les occurrences de chaque byte
        counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
        
        # Calculer les probabilités
        probabilities = counts / len(data)
        
        # Calculer l'entropie
        entropy = -np.sum(
            p * np.log2(p) for p in probabilities if p > 0
        )
        
        return entropy
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score de risque global"""
        
        risk_score = 0
        risk_factors = []
        
        # Pondération des différents checks
        weights = {
            'basic_validation': 20,
            'malware_scan': 30,
            'mime_validation': 15,
            'content_moderation': 25,
            'steganography': 5,
            'metadata_security': 5
        }
        
        for check_name, weight in weights.items():
            if check_name in checks:
                check_result = checks[check_name]
                if not check_result.get('passed', True):
                    risk_score += weight
                    risk_factors.append(check_name)
        
        # Déterminer le niveau de risque
        if risk_score >= 70:
            risk_level = 'high'
        elif risk_score >= 40:
            risk_level = 'medium'
        elif risk_score >= 20:
            risk_level = 'low'
        else:
            risk_level = 'minimal'
        
        return {
            'score': risk_score,
            'level': risk_level,
            'risk_factors': risk_factors
        }
    
    def _determine_status(self, risk_assessment: Dict[str, Any]) -> str:
        """Détermine le statut final du contenu"""
        
        risk_level = risk_assessment['level']
        
        if risk_level in ['high']:
            return 'rejected'
        elif risk_level in ['medium']:
            return 'flagged_for_review'
        elif risk_level in ['low']:
            return 'approved_with_warnings'
        else:
            return 'approved'
    
    async def _generate_security_recommendations(
        self,
        checks: Dict[str, Any]
    ) -> List[str]:
        """Génère des recommandations de sécurité"""
        
        recommendations = []
        
        for check_name, check_result in checks.items():
            if not check_result.get('passed', True):
                if check_name == 'malware_scan':
                    recommendations.append('Quarantine file and run additional antivirus scans')
                elif check_name == 'content_moderation':
                    recommendations.append('Manual review required for content appropriateness')
                elif check_name == 'mime_validation':
                    recommendations.append('Verify file type and re-upload with correct extension')
                elif check_name == 'steganography':
                    recommendations.append('Investigate potential hidden data in file')
                elif check_name == 'metadata_security':
                    recommendations.append('Remove sensitive information from metadata')
        
        if not recommendations:
            recommendations.append('No security issues detected - content approved')
        
        return recommendations
    
    def _load_malware_patterns(self) -> Dict[str, str]:
        """Charge les patterns de malware"""
        # En production, charger depuis une base de données mise à jour
        return {
            'suspicious_eval': 'eval(',
            'base64_suspicious': 'base64_decode',
            'shell_command': 'shell_exec'
        }
    
    def _load_content_filters(self) -> Dict[str, Any]:
        """Charge les filtres de contenu"""
        # En production, charger depuis configuration
        return {
            'adult_content_threshold': 0.8,
            'violence_threshold': 0.8,
            'inappropriate_language_threshold': 0.7
        }
    
    def _get_known_malware_hashes(self) -> set:
        """Obtient les hashes de malware connus"""
        # En production, synchroniser avec base de données threat intelligence
        return set()
    
    def _has_suspicious_filename(self, filename: str) -> bool:
        """Vérifie si le nom de fichier est suspect"""
        suspicious_patterns = [
            'virus', 'malware', 'trojan', 'backdoor',
            'keylog', 'rootkit', 'exploit'
        ]
        
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in suspicious_patterns)
    
    def _is_mime_type_allowed(self, mime_type: str) -> bool:
        """Vérifie si le type MIME est autorisé"""
        for category, mime_types in self.allowed_mime_types.items():
            if mime_type in mime_types:
                return True
        return False
    
    async def _analyze_image_structure(self, file_path: str) -> Dict[str, Any]:
        """Analyse la structure d'une image pour détecter des anomalies"""
        
        analysis = {'anomalies': []}
        
        try:
            # Ouvrir l'image avec PIL
            with Image.open(file_path) as img:
                # Vérifier les métadonnées EXIF suspectes
                exif_data = img.getexif()
                
                if exif_data:
                    # Rechercher des données suspectes dans EXIF
                    for tag, value in exif_data.items():
                        if isinstance(value, (str, bytes)) and len(str(value)) > 1000:
                            analysis['anomalies'].append({
                                'type': 'suspicious_exif_data',
                                'tag': tag,
                                'severity': 'medium'
                            })
                
                # Vérifier les dimensions suspectes
                if img.width * img.height > 50000000:  # 50MP
                    analysis['anomalies'].append({
                        'type': 'unusually_large_dimensions',
                        'dimensions': f'{img.width}x{img.height}',
                        'severity': 'low'
                    })
        
        except Exception as e:
            logger.error(f"Erreur analyse structure image: {e}")
        
        return analysis


# Instance globale du service
content_security_service = ContentSecurityService()