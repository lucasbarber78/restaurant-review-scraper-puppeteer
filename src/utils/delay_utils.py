#!/usr/bin/env python3
"""
Delay Utilities Module

This module provides functions for creating human-like delays in the scraper's actions.
"""

import random
import time
import logging
import asyncio
from typing import Dict, Optional, List, Union

logger = logging.getLogger(__name__)

# Default delay base values (in seconds) for different action types
DEFAULT_DELAY_BASE_VALUES = {
    "click": 1.0,
    "scroll": 1.5,
    "navigation": 3.0,
    "typing": 0.2,
    "waiting": 2.0,
    "reading": 5.0,
    "selection": 1.2,
    "thinking": 3.5
}

# Global configuration
_config = {
    "delay_base_values": DEFAULT_DELAY_BASE_VALUES.copy(),
    "variance_factor": 0.3,  # Default variance factor (±30%)
    "use_gaussian": True,    # Use Gaussian distribution by default
}


def configure_delays(delay_base_values: Optional[Dict[str, float]] = None, 
                     variance_factor: Optional[float] = None,
                     use_gaussian: Optional[bool] = None) -> None:
    """Configure delay parameters.
    
    Args:
        delay_base_values (dict, optional): Base delay values in seconds for different actions.
        variance_factor (float, optional): Variance factor (0.3 = ±30%).
        use_gaussian (bool, optional): Whether to use Gaussian distribution (more human-like).
    """
    global _config
    
    if delay_base_values is not None:
        # Update only the provided values, keeping others
        for key, value in delay_base_values.items():
            _config["delay_base_values"][key] = value
            
    if variance_factor is not None:
        _config["variance_factor"] = max(0.0, min(1.0, variance_factor))  # Clamp to 0.0-1.0
        
    if use_gaussian is not None:
        _config["use_gaussian"] = use_gaussian


def get_random_delay(base_value: float, variance_factor: Optional[float] = None) -> float:
    """Generate a random delay value based on a base value and variance factor.
    
    Args:
        base_value (float): Base delay value in seconds.
        variance_factor (float, optional): Variance factor (0.3 = ±30%).
            Defaults to the configured global value.
            
    Returns:
        float: Random delay value in seconds.
    """
    if variance_factor is None:
        variance_factor = _config["variance_factor"]
        
    if _config["use_gaussian"]:
        # Gaussian distribution is more human-like
        # Use 3*variance_factor as the standard deviation to keep ~99.7% of values within the variance range
        std_dev = base_value * variance_factor / 3.0
        delay = random.gauss(base_value, std_dev)
        # Ensure the delay is positive (very rarely, Gaussian can give negative values)
        return max(0.1, delay)
    else:
        # Uniform distribution (simpler)
        min_val = base_value * (1 - variance_factor)
        max_val = base_value * (1 + variance_factor)
        return random.uniform(min_val, max_val)


def delay_between_actions(action_type: str = "click") -> float:
    """Add a random delay between actions to mimic human behavior.
    
    Args:
        action_type (str, optional): Type of action. Defaults to "click".
            Options: "click", "scroll", "navigation", "typing", "waiting",
            "reading", "selection", "thinking"
            
    Returns:
        float: The actual delay time used (in seconds).
    """
    # Get base value for the action type, or use click as default
    base_value = _config["delay_base_values"].get(
        action_type, _config["delay_base_values"]["click"]
    )
    
    # Get random delay
    delay = get_random_delay(base_value)
    
    # Apply the delay
    time.sleep(delay)
    
    return delay


async def async_delay_between_actions(action_type: str = "click") -> float:
    """Add an async random delay between actions to mimic human behavior.
    
    Args:
        action_type (str, optional): Type of action. Defaults to "click".
            Options: "click", "scroll", "navigation", "typing", "waiting",
            "reading", "selection", "thinking"
            
    Returns:
        float: The actual delay time used (in seconds).
    """
    # Get base value for the action type, or use click as default
    base_value = _config["delay_base_values"].get(
        action_type, _config["delay_base_values"]["click"]
    )
    
    # Get random delay
    delay = get_random_delay(base_value)
    
    # Apply the delay asynchronously
    await asyncio.sleep(delay)
    
    return delay


async def simulate_human_typing(page, selector: str, text: str) -> None:
    """Simulate human typing with variable speed and occasional pauses.
    
    Args:
        page: Puppeteer page object.
        selector (str): CSS selector for the input field.
        text (str): Text to type.
    """
    # First clear the field
    await page.click(selector, {"clickCount": 3})  # Triple click to select all
    await page.keyboard.press("Backspace")
    
    # Calculate natural timing parameters
    avg_delay = _config["delay_base_values"]["typing"]
    
    for char in text:
        # Random delay for each character
        char_delay = get_random_delay(avg_delay, 0.5)  # Higher variance for typing
        
        # Occasional longer pause (as if thinking)
        if random.random() < 0.03:  # 3% chance
            thinking_delay = get_random_delay(_config["delay_base_values"]["thinking"], 0.4)
            await asyncio.sleep(thinking_delay)
        
        # Type the character
        await page.keyboard.type(char)
        await asyncio.sleep(char_delay)
    
    # Slight pause after completing typing
    await asyncio.sleep(get_random_delay(0.5, 0.2))
