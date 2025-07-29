
import re
import numpy as np
from difflib import SequenceMatcher
from jellyfish import jaro_winkler_similarity, soundex
import Levenshtein
from typing import Dict, Tuple
from config import settings
from utils import extract_email_username, normalize_phone_number, parse_address, standardize_address_abbreviations
from loguru import logger
from models import IdentityRecord, SimilarityResult

class RuleBasedIdentityMatcher:
    def __init__(self):
        self.weights = settings.FIELD_WEIGHTS
        self.threshold = settings.RULE_BASED_THRESHOLD
    
    def _compute_string_similarity(self, str1: str, str2: str) -> dict:
        """Compute multiple similarity metrics for strings"""
        if not str1 and not str2:
            return {
                'jaro_winkler': 1.0,
                'levenshtein': 1.0,
                'sequence_matcher': 1.0,
                'exact': 1.0
            }
        
        if not str1 or not str2:
            return {
                'jaro_winkler': 0.0,
                'levenshtein': 0.0,
                'sequence_matcher': 0.0,
                'exact': 0.0
            }
        
        # Normalize strings
        norm1 = str1.lower().strip()
        norm2 = str2.lower().strip()
        
        return {
            'jaro_winkler': jaro_winkler_similarity(norm1, norm2),
            'levenshtein': 1.0 - (Levenshtein.distance(norm1, norm2) / max(len(norm1), len(norm2))),
            'sequence_matcher': SequenceMatcher(None, norm1, norm2).ratio(),
            'exact': 1.0 if norm1 == norm2 else 0.0
        }
    
    def _compute_phonetic_similarity(self, name1: str, name2: str) -> float:
        """Compare names using phonetic algorithms"""
        try:
            if not name1 and not name2:
                return 1.0
            if not name1 or not name2:
                return 0.0
                
            s1 = soundex(name1)
            s2 = soundex(name2)
            return 1.0 if s1 == s2 else 0.0
        except Exception as e:
            logger.warning(f"Phonetic similarity failed: {e}")
            return 0.0
    
    def _compute_email_similarity(self, email1: str, email2: str) -> Tuple[float, dict]:
        """Compute email similarity with detailed metrics"""
        username1 = extract_email_username(email1)
        username2 = extract_email_username(email2)
        
        if not username1 and not username2:
            return 1.0, {'type': 'both_empty'}
        
        if not username1 or not username2:
            return 0.0, {'type': 'one_empty'}
        
        # Exact match
        if username1 == username2:
            return 1.0, {'type': 'exact_match'}
        
        # Compute various similarities
        similarities = self._compute_string_similarity(username1, username2)
        
        # Check for common variation patterns
        pattern_score = 0.0
        if re.search(r'\d', email1) or re.search(r'\d', email2):
            pattern_score = 0.3  # Slight boost for number variations
        
        # Weighted combination
        final_score = max(similarities.values()) * 0.7 + pattern_score * 0.3
        
        return min(final_score, 1.0), {
            'similarities': similarities,
            'pattern_boost': pattern_score,
            'type': 'fuzzy_match'
        }
    
    def _compute_name_similarity(self, name1: str, name2: str) -> Tuple[float, dict]:
        """Compute name similarity with phonetic matching"""
        if not name1 and not name2:
            return 1.0, {'type': 'both_empty'}
        
        if not name1 or not name2:
            return 0.0, {'type': 'one_empty'}
        
        # Normalize names
        norm1 = re.sub(r'[^\w\s]', '', name1.lower()).strip()
        norm2 = re.sub(r'[^\w\s]', '', name2.lower()).strip()
        
        if not norm1 and not norm2:
            return 1.0, {'type': 'both_empty_after_norm'}
        
        if not norm1 or not norm2:
            return 0.0, {'type': 'one_empty_after_norm'}
        
        # Direct similarity metrics
        similarities = self._compute_string_similarity(norm1, norm2)
        
        # Phonetic similarity
        phonetic_sim = self._compute_phonetic_similarity(norm1, norm2)
        
        # Check reversed names (first last vs last first)
        reversed_sim = 0.0
        parts1 = norm1.split()
        parts2 = norm2.split()
        if len(parts1) == 2 and len(parts2) == 2:
            reversed_name1 = f"{parts1[1]} {parts1[0]}"
            reversed_sim = jaro_winkler_similarity(reversed_name1, norm2)
        
        # Nickname handling (basic)
        nickname_boost = 0.0
        nicknames = {
            'bob': 'robert', 'rob': 'robert', 'bill': 'william',
            'jim': 'james', 'joe': 'joseph', 'mike': 'michael'
        }
        if norm1 in nicknames and nicknames[norm1] == norm2:
            nickname_boost = 0.5
        elif norm2 in nicknames and nicknames[norm2] == norm1:
            nickname_boost = 0.5
        
        # Combine scores
        max_string_sim = max(similarities.values())
        final_score = max(max_string_sim, phonetic_sim, reversed_sim) + nickname_boost
        
        return min(final_score, 1.0), {
            'string_similarities': similarities,
            'phonetic_similarity': phonetic_sim,
            'reversed_similarity': reversed_sim,
            'nickname_boost': nickname_boost,
            'type': 'complex_match' if final_score > 0.8 else 'low_similarity'
        }
    
    def _compute_phone_similarity(self, phone1: str, phone2: str) -> Tuple[float, dict]:
        """Compute phone similarity using phonenumbers library"""
        if not phone1 and not phone2:
            return 1.0, {'type': 'both_empty'}
        
        if not phone1 or not phone2:
            return 0.0, {'type': 'one_empty'}
        
        try:
            norm_phone1, country1 = normalize_phone_number(phone1)
            norm_phone2, country2 = normalize_phone_number(phone2)
            
            if not norm_phone1 and not norm_phone2:
                return 1.0, {'type': 'both_invalid'}
            
            if not norm_phone1 or not norm_phone2:
                return 0.0, {'type': 'one_invalid'}
            
            # Exact match
            if norm_phone1 == norm_phone2:
                return 1.0, {
                    'type': 'exact_match',
                    'country_match': country1 == country2
                }
            
            # Partial match (last 7 digits for US numbers)
            if len(norm_phone1) >= 7 and len(norm_phone2) >= 7:
                if norm_phone1[-7:] == norm_phone2[-7:]:
                    return 0.8, {
                        'type': 'partial_match',
                        'match_type': 'last_7_digits'
                    }
            
            return 0.0, {'type': 'no_match'}
            
        except Exception as e:
            logger.warning(f"Phone similarity computation failed: {e}")
            return 0.0, {'type': 'error', 'error': str(e)}
    
    def _compute_address_similarity(self, addr1: str, addr2: str) -> Tuple[float, dict]:
        """Compute address similarity with advanced parsing"""
        if not addr1 and not addr2:
            return 1.0, {'type': 'both_empty'}
        
        if not addr1 or not addr2:
            return 0.0, {'type': 'one_empty'}
        
        # Standardize abbreviations
        std_addr1 = standardize_address_abbreviations(addr1, settings.ADDRESS_ABBREVIATIONS)
        std_addr2 = standardize_address_abbreviations(addr2, settings.ADDRESS_ABBREVIATIONS)
        
        # Basic string similarity
        string_sim = self._compute_string_similarity(std_addr1, std_addr2)
        max_string_sim = max(string_sim.values())
        
        # Parse addresses for component matching
        try:
            parsed1 = parse_address(addr1)
            parsed2 = parse_address(addr2)
            
            if parsed1 and parsed2:
                # Compare key components
                component_matches = 0
                total_components = 0
                
                for key in ['AddressNumber', 'StreetName', 'StreetNamePostType', 'PlaceName']:
                    val1 = parsed1.get(key, '')
                    val2 = parsed2.get(key, '')
                    if val1 or val2:
                        total_components += 1
                        if val1.lower() == val2.lower():
                            component_matches += 1
                
                if total_components > 0:
                    component_score = component_matches / total_components
                    # Combine with string similarity
                    final_score = (max_string_sim + component_score) / 2
                    return min(final_score, 1.0), {
                        'type': 'parsed_match',
                        'component_score': component_score,
                        'string_similarity': max_string_sim
                    }
        except Exception as e:
            logger.warning(f"Address parsing failed: {e}")
        
        return max_string_sim, {
            'type': 'string_match',
            'similarities': string_sim
        }
    
    def compute_similarity(self, record1: IdentityRecord, record2: IdentityRecord) -> SimilarityResult:
        """Compute overall similarity between two identity records"""
        try:
            # Compute individual field similarities
            email_sim, email_details = self._compute_email_similarity(record1.email or '', record2.email or '')
            name_sim, name_details = self._compute_name_similarity(record1.name or '', record2.name or '')
            phone_sim, phone_details = self._compute_phone_similarity(record1.phone or '', record2.phone or '')
            address_sim, address_details = self._compute_address_similarity(record1.address or '', record2.address or '')
            
            # Weighted average
            similarity = (
                self.weights['email'] * email_sim +
                self.weights['name'] * name_sim +
                self.weights['phone'] * phone_sim +
                self.weights['address'] * address_sim
            )
            
            # Determine if same person
            is_same = similarity >= self.threshold
            
            # Confidence based on highest similarity score
            max_field_sim = max(email_sim, name_sim, phone_sim, address_sim)
            confidence = min(similarity + (1 - similarity) * 0.3, 1.0)  # Boost confidence slightly
            
            details = {
                'field_similarities': {
                    'email': {'score': email_sim, 'details': email_details},
                    'name': {'score': name_sim, 'details': name_details},
                    'phone': {'score': phone_sim, 'details': phone_details},
                    'address': {'score': address_sim, 'details': address_details}
                },
                'weights_used': self.weights
            }
            
            return SimilarityResult(
                similarity_score=float(similarity),
                is_same_person=is_same,
                method="rule_based",
                confidence=float(confidence),
                details=details
            )
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return SimilarityResult(
                similarity_score=0.0,
                is_same_person=False,
                method="rule_based",
                confidence=0.0,
                details={'error': str(e)}
            )
    
    def is_same_person(self, record1: IdentityRecord, record2: IdentityRecord) -> bool:
        """Simple interface to check if two records represent the same person"""
        result = self.compute_similarity(record1, record2)
        return result.is_same_person
