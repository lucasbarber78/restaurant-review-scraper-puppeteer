#!/usr/bin/env python3
"""
Structure Parser Module

This module provides utilities for parsing and using the structure analysis files
to dynamically determine the best selectors for web scraping.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class GoogleStructureParser:
    def __init__(self, json_path: str = "Review Site Optimization/google_search_review_structure_analysis.json"):
        """
        Load and parse the Google review structure analysis file.
        
        Args:
            json_path (str): Path to the structure analysis JSON file
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.structure = json.load(f)
            logger.info(f"Successfully loaded structure analysis from {json_path}")
            self.timestamp = self.structure.get("timestamp")
            self.search_url = self.structure.get("searchUrl")
            self.review_structure = self.structure.get("initialReviewStructure", {})
        except FileNotFoundError:
            logger.warning(f"Structure analysis file {json_path} not found")
            self.structure = {}
            self.timestamp = None
            self.search_url = None
            self.review_structure = {}
        except Exception as e:
            logger.error(f"Error loading structure analysis: {e}")
            self.structure = {}
            self.timestamp = None
            self.search_url = None
            self.review_structure = {}
    
    def get_review_selectors(self) -> Dict[str, List[str]]:
        """
        Extract and return CSS selectors for review elements.
        
        Returns:
            dict: Dictionary of selectors for different review components
        """
        selectors = {
            "review_container": [],
            "reviewer_name": [],
            "rating": [],
            "date": [],
            "review_text": []
        }
        
        # Extract selectors from review structure
        if self.review_structure and "reviews" in self.review_structure:
            for review in self.review_structure["reviews"]:
                if "elementInfo" in review and "tagPath" in review["elementInfo"]:
                    selectors["review_container"].append(review["elementInfo"]["tagPath"])
                
                if "reviewerName" in review and review["reviewerName"]:
                    path = review["reviewerName"].get("tagPath")
                    if path:
                        selectors["reviewer_name"].append(path)
                
                if "rating" in review and review["rating"]:
                    path = review["rating"].get("element")
                    if path:
                        selectors["rating"].append(path)
                
                if "date" in review and review["date"]:
                    path = review["date"].get("tagPath")
                    if path:
                        selectors["date"].append(path)
                
                if "reviewText" in review and review["reviewText"]:
                    path = review["reviewText"].get("tagPath")
                    if path:
                        selectors["review_text"].append(path)
        
        # Add default/fallback selectors
        self._add_default_selectors(selectors)
        
        # Remove duplicates and return
        for key in selectors:
            selectors[key] = list(set(selectors[key]))
        
        return selectors
    
    def _add_default_selectors(self, selectors: Dict[str, List[str]]) -> None:
        """
        Add default selectors as fallbacks.
        
        Args:
            selectors (dict): Dictionary of selectors to update
        """
        # Default review container selectors
        default_containers = [
            'div[data-review-id]',
            '.review-container',
            'div[role="listitem"]',
            'div.wDYxhc[data-attrid*="review"]'
        ]
        
        # Default reviewer name selectors
        default_names = [
            '.d4r55',
            '.info_text div',
            '.member_info .username',
            '.y3Ibjb'
        ]
        
        # Default rating selectors
        default_ratings = [
            'span[role="img"]',
            'div[aria-label*="star"]',
            'g-review-stars'
        ]
        
        # Default date selectors
        default_dates = [
            '.y3Ibjb',
            '.ratingDate',
            '.date',
            '.rsqaWe'
        ]
        
        # Default review text selectors
        default_texts = [
            '.wiI7pd',
            '.prw_reviews_text_summary_hsx p',
            '.partial_entry',
            '.review-content p'
        ]
        
        # Add defaults to selectors
        selectors["review_container"].extend(default_containers)
        selectors["reviewer_name"].extend(default_names)
        selectors["rating"].extend(default_ratings)
        selectors["date"].extend(default_dates)
        selectors["review_text"].extend(default_texts)
