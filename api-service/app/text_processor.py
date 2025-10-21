"""
Text processing utilities for improving search quality
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """Text processor for query expansion and normalization"""
    
    # Default Vietnamese synonyms for common business terms
    # Users can extend this by providing custom synonyms file
    DEFAULT_SYNONYMS = {
        "công ty": ["cty", "ct", "công ty tnhh", "công ty cổ phần", "ctcp", "tnhh", "doanh nghiệp", "dn"],
        "cty": ["công ty", "ct", "công ty tnhh", "công ty cổ phần", "ctcp", "tnhh"],
        "nước": ["cấp nước", "nước sạch", "thuỷ", "thủy"],
        "điện": ["điện lực", "điện năng", "cấp điện", "năng lượng"],
        "bưu điện": ["bưu chính", "bưu điện viễn thông", "bđvt", "vnpost"],
        "bảo hiểm": ["bhxh", "bảo hiểm xã hội", "bhyt", "bh"],
        "ngân hàng": ["nh", "bank", "banking", "nhnn"],
        "viễn thông": ["vt", "telecom", "通信", "viễn thông"],
        "xây dựng": ["xd", "thi công", "xây lắp"],
        "thương mại": ["tm", "buôn bán", "kinh doanh"],
        "dịch vụ": ["dv", "service"],
        "sản xuất": ["sx", "chế tạo", "manufacturing"],
    }
    
    # Default common abbreviations
    DEFAULT_ABBREVIATIONS = {
        "ctcp": "công ty cổ phần",
        "tnhh": "trách nhiệm hữu hạn",
        "bhxh": "bảo hiểm xã hội",
        "bhyt": "bảo hiểm y tế",
        "ubnd": "ủy ban nhân dân",
        "vt": "viễn thông",
        "nh": "ngân hàng",
        "cn": "chi nhánh",
        "pgs": "phó giáo sư",
        "ts": "tiến sĩ",
        "dn": "doanh nghiệp",
        "xd": "xây dựng",
        "tm": "thương mại",
        "dv": "dịch vụ",
        "sx": "sản xuất",
        "bđvt": "bưu điện viễn thông",
        "tphcm": "thành phố hồ chí minh",
        "hcm": "hồ chí minh",
        "hn": "hà nội",
    }
    
    # Class-level storage for custom synonyms and abbreviations
    _custom_synonyms: Optional[Dict[str, List[str]]] = None
    _custom_abbreviations: Optional[Dict[str, str]] = None
    
    @classmethod
    def load_custom_synonyms(cls, file_path: str) -> None:
        """
        Load custom synonyms from JSON file
        
        Args:
            file_path: Path to JSON file with synonyms
            
        Format:
        {
            "word": ["synonym1", "synonym2", ...]
        }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cls._custom_synonyms = json.load(f)
            logger.info(f"Loaded {len(cls._custom_synonyms)} custom synonym groups from {file_path}")
        except Exception as e:
            logger.warning(f"Failed to load custom synonyms from {file_path}: {e}")
    
    @classmethod
    def load_custom_abbreviations(cls, file_path: str) -> None:
        """
        Load custom abbreviations from JSON file
        
        Args:
            file_path: Path to JSON file with abbreviations
            
        Format:
        {
            "abbr": "full form"
        }
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cls._custom_abbreviations = json.load(f)
            logger.info(f"Loaded {len(cls._custom_abbreviations)} custom abbreviations from {file_path}")
        except Exception as e:
            logger.warning(f"Failed to load custom abbreviations from {file_path}: {e}")
    
    @classmethod
    def get_synonyms(cls) -> Dict[str, List[str]]:
        """Get merged synonyms (default + custom)"""
        synonyms = cls.DEFAULT_SYNONYMS.copy()
        if cls._custom_synonyms:
            synonyms.update(cls._custom_synonyms)
        return synonyms
    
    @classmethod
    def get_abbreviations(cls) -> Dict[str, str]:
        """Get merged abbreviations (default + custom)"""
        abbreviations = cls.DEFAULT_ABBREVIATIONS.copy()
        if cls._custom_abbreviations:
            abbreviations.update(cls._custom_abbreviations)
        return abbreviations
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize Vietnamese text
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Vietnamese
        # Keep: letters, numbers, spaces, Vietnamese characters
        text = re.sub(r'[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', ' ', text)
        
        # Remove extra whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @classmethod
    def expand_query(cls, query: str, max_expansions: int = 5) -> List[str]:
        """
        Expand query with synonyms and variations
        
        Args:
            query: Original query
            max_expansions: Maximum number of query variations to generate
            
        Returns:
            List of query variations
        """
        queries = [query]
        normalized = cls.normalize_text(query)
        
        if normalized != query:
            queries.append(normalized)
        
        # Get current synonyms and abbreviations
        synonyms = cls.get_synonyms()
        abbreviations = cls.get_abbreviations()
        
        # Add synonym expansions
        words = normalized.split()
        for word in words:
            if word in synonyms:
                for synonym in synonyms[word][:3]:  # Limit to top 3 synonyms per word
                    # Replace word with synonym
                    expanded = normalized.replace(word, synonym)
                    if expanded not in queries and len(queries) < max_expansions:
                        queries.append(expanded)
        
        # Expand abbreviations
        for abbr, full in abbreviations.items():
            if abbr in normalized:
                expanded = normalized.replace(abbr, full)
                if expanded not in queries and len(queries) < max_expansions:
                    queries.append(expanded)
        
        logger.debug(f"Query expanded from '{query}' to {len(queries)} variations")
        return queries
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (Jaccard similarity)
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize both texts
        text1 = TextProcessor.normalize_text(text1)
        text2 = TextProcessor.normalize_text(text2)
        
        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    @staticmethod
    def boost_score(
        original_score: float,
        query: str,
        result_name: str,
        result_code: str = ""
    ) -> float:
        """
        Boost score based on text similarity
        
        Args:
            original_score: Original embedding similarity score
            query: Search query
            result_name: Result name
            result_code: Result code (optional)
            
        Returns:
            Boosted score
        """
        # Calculate text similarity
        name_similarity = TextProcessor.calculate_text_similarity(query, result_name)
        code_similarity = 0.0
        
        if result_code:
            code_similarity = TextProcessor.calculate_text_similarity(query, result_code)
        
        # Combine scores with weights
        # 60% embedding similarity, 30% name similarity, 10% code similarity
        boosted = (
            original_score * 0.6 +
            name_similarity * 0.3 +
            code_similarity * 0.1
        )
        
        # Ensure score is between 0 and 1
        return min(max(boosted, 0.0), 1.0)


class SearchEnhancer:
    """Enhance search results with re-ranking and filtering"""
    
    @staticmethod
    def rerank_results(
        results: List[Dict],
        query: str,
        boost_text_match: bool = True
    ) -> List[Dict]:
        """
        Re-rank search results
        
        Args:
            results: Original search results
            query: Search query
            boost_text_match: Whether to boost based on text similarity
            
        Returns:
            Re-ranked results
        """
        if not results:
            return results
        
        if boost_text_match:
            for result in results:
                metadata = result.get("metadata", {})
                name = metadata.get("accounting_object_name", "")
                code = metadata.get("accounting_object_code", "")
                
                # Calculate boosted score
                original_score = result.get("score", 0.0)
                boosted_score = TextProcessor.boost_score(
                    original_score,
                    query,
                    name,
                    code
                )
                
                # Store both scores
                result["original_score"] = original_score
                result["score"] = boosted_score
        
        # Sort by boosted score
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        return results
    
    @staticmethod
    def filter_low_scores(
        results: List[Dict],
        min_score: float = 0.2
    ) -> List[Dict]:
        """
        Filter out results with low scores
        
        Args:
            results: Search results
            min_score: Minimum score threshold
            
        Returns:
            Filtered results
        """
        return [r for r in results if r.get("score", 0.0) >= min_score]

