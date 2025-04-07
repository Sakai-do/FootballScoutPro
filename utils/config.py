#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Module

This module defines configuration settings for the application.
"""

import os
import json
from pathlib import Path

# Application directories
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(APP_DIR, 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

# Ensure data directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Default API settings
API_KEY = "719b4fb0c7bebee5994f4301fd8654e9"  # Your API-Sports key
API_SOURCE = "apisports"  # Options: "rapidapi", "apisports", "mock"

# Default settings
DEFAULT_CONFIG = {
    "api_key": API_KEY,
    "api_source": API_SOURCE,  # Added API source setting
    "leagues": [
        {"id": 39, "name": "Premier League", "country": "England"},
        {"id": 140, "name": "La Liga", "country": "Spain"},
        {"id": 78, "name": "Bundesliga", "country": "Germany"},
        {"id": 135, "name": "Serie A", "country": "Italy"},
        {"id": 61, "name": "Ligue 1", "country": "France"}
    ],
    "current_season": 2023,
    "theme": "light",
    "cache_expiry_hours": 24
}


def load_config():
    """
    Load configuration from file, creating default if it doesn't exist.
    
    Returns:
        dict: Configuration settings
    """
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        # Update API settings from config
        global API_KEY, API_SOURCE
        API_KEY = config.get('api_key', API_KEY)
        API_SOURCE = config.get('api_source', API_SOURCE)
        
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG


def save_config(config):
    """
    Save configuration to file.
    
    Args:
        config (dict): Configuration settings
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")


# Load config at module import
config = load_config()

# Override constants with loaded config
API_KEY = config.get('api_key', API_KEY)
API_SOURCE = config.get('api_source', API_SOURCE)
CURRENT_SEASON = config.get('current_season', DEFAULT_CONFIG['current_season'])
THEME = config.get('theme', DEFAULT_CONFIG['theme'])
CACHE_EXPIRY_HOURS = config.get('cache_expiry_hours', DEFAULT_CONFIG['cache_expiry_hours'])
LEAGUES = config.get('leagues', DEFAULT_CONFIG['leagues'])


def get_league_name(league_id):
    """
    Get league name from ID.
    
    Args:
        league_id (int): League ID
    
    Returns:
        str: League name, or None if not found
    """
    for league in LEAGUES:
        if league['id'] == league_id:
            return league['name']
    return None


def get_league_country(league_id):
    """
    Get league country from ID.
    
    Args:
        league_id (int): League ID
    
    Returns:
        str: League country, or None if not found
    """
    for league in LEAGUES:
        if league['id'] == league_id:
            return league['country']
    return None