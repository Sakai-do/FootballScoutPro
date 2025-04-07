#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Client Module

This module handles the integration with football APIs (RapidAPI or API-Sports),
including API requests and response caching to improve performance.
"""

import os
import json
import time
from datetime import datetime, timedelta
import random

import requests
import requests_cache
from PySide6.QtCore import QObject, Signal, Slot, QThreadPool

from utils.config import API_KEY, API_SOURCE, CACHE_DIR


class ApiClient(QObject):
    """
    Client for interacting with the football API.
    
    This class handles API requests, caching, and error handling for
    the football data API.
    """
    
    # Signals for asynchronous operations
    data_fetched = Signal(dict)
    error_occurred = Signal(str)
    request_started = Signal()
    request_finished = Signal()
    
    def __init__(self, parent=None, use_mock_data=False):  # Changed default to false to use real API
        """Initialize the API client with caching."""
        super().__init__(parent)
        
        # Flag to use mock data instead of real API calls
        self.use_mock_data = use_mock_data
        
        # Initialize cache
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.cache_file = os.path.join(CACHE_DIR, 'football_api_cache')
        
        # Configure requests-cache
        requests_cache.install_cache(
            self.cache_file,
            backend='sqlite',
            expire_after=timedelta(hours=24)
        )
        
        # Set up API base URL and headers based on API source
        if API_SOURCE == 'rapidapi':
            self.api_base_url = "https://api-football-v1.p.rapidapi.com/v3"
            self.headers = {
                'x-rapidapi-key': API_KEY,
                'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
            }
        else:  # Default to API-Sports
            self.api_base_url = "https://v3.football.api-sports.io"
            self.headers = {
                'x-apisports-key': API_KEY
            }
        
        # Initialize thread pool for async requests
        self.thread_pool = QThreadPool()
    
    @Slot(str, dict)
    def fetch_data(self, endpoint, params=None):
        """
        Fetch data from the API.
        
        Args:
            endpoint (str): API endpoint (e.g., '/players')
            params (dict, optional): Query parameters. Defaults to None.
        """
        self.request_started.emit()
        
        if self.use_mock_data:
            # Use mock data instead of real API call
            self.mock_data_response(endpoint, params)
            return
        
        try:
            url = f"{self.api_base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.data_fetched.emit(data)
            
        except requests.RequestException as e:
            self.error_occurred.emit(f"API request failed: {str(e)}")
        
        finally:
            self.request_finished.emit()
    
    def mock_data_response(self, endpoint, params=None):
        """
        Generate mock data for API endpoints.
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters. Defaults to None.
        """
        # Create mock response data based on the endpoint
        if endpoint == '/players/topscorers':
            data = self.generate_mock_top_players()
        elif endpoint == '/players':
            player_id = params.get('id') if params else None
            data = self.generate_mock_player_details(player_id)
        elif endpoint == '/players/statistics':
            player_id = params.get('player') if params else None
            data = self.generate_mock_player_statistics(player_id)
        else:
            data = {"response": []}
        
        # Simulate network delay
        time.sleep(0.5)
        
        # Emit the mock data
        self.data_fetched.emit(data)
        self.request_finished.emit()
    
    def generate_mock_top_players(self):
        """
        Generate mock data for top players.
        
        Returns:
            dict: Mock API response with top players data
        """
        # Names for mock players
        first_names = ["Lionel", "Cristiano", "Robert", "Kevin", "Mohamed", "Virgil", "Sergio", "Harry", "Kylian", "Neymar"]
        last_names = ["Messi", "Ronaldo", "Lewandowski", "De Bruyne", "Salah", "van Dijk", "Ramos", "Kane", "Mbappé", "Jr"]
        
        # Team names
        teams = ["Manchester United", "Barcelona", "Real Madrid", "Bayern Munich", "Liverpool", "Paris Saint-Germain", 
                 "Manchester City", "Chelsea", "Juventus", "Borussia Dortmund"]
        
        # Player positions
        positions = ["Forward", "Midfielder", "Defender", "Goalkeeper"]
        position_weights = [0.4, 0.3, 0.2, 0.1]  # Probability weights
        
        # Generate players
        players = []
        for i in range(20):
            # Basic player info
            player_id = 10000 + i
            position = random.choices(positions, weights=position_weights)[0]
            
            # Randomize stats based on position
            if position == "Forward":
                goals = random.randint(10, 30)
                assists = random.randint(2, 15)
                passes_accuracy = random.randint(70, 85)
                tackles = random.randint(5, 20)
            elif position == "Midfielder":
                goals = random.randint(3, 12)
                assists = random.randint(5, 20)
                passes_accuracy = random.randint(80, 92)
                tackles = random.randint(30, 70)
            elif position == "Defender":
                goals = random.randint(1, 5)
                assists = random.randint(1, 8)
                passes_accuracy = random.randint(75, 90)
                tackles = random.randint(50, 120)
            else:  # Goalkeeper
                goals = 0
                assists = random.randint(0, 2)
                passes_accuracy = random.randint(70, 85)
                tackles = random.randint(0, 5)
            
            # Generate player data
            player = {
                "player": {
                    "id": player_id,
                    "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                    "firstname": random.choice(first_names),
                    "lastname": random.choice(last_names),
                    "age": random.randint(20, 36),
                    "nationality": "Country",
                    "height": f"{random.randint(170, 195)} cm",
                    "weight": f"{random.randint(65, 90)} kg",
                    "position": position
                },
                "statistics": [{
                    "team": {
                        "id": 1000 + i % 10,
                        "name": teams[i % 10]
                    },
                    "league": {
                        "id": 39,
                        "name": "Premier League",
                        "country": "England"
                    },
                    "games": {
                        "appearances": random.randint(20, 38),
                        "minutes": random.randint(1800, 3400),
                        "rating": round(random.uniform(6.5, 8.9), 1)
                    },
                    "shots": {
                        "total": random.randint(20, 100),
                        "on": random.randint(10, 50)
                    },
                    "goals": {
                        "total": goals,
                        "assists": assists
                    },
                    "passes": {
                        "total": random.randint(500, 2000),
                        "accuracy": passes_accuracy
                    },
                    "tackles": {
                        "total": tackles,
                        "blocks": random.randint(5, 30),
                        "interceptions": random.randint(10, 50)
                    },
                    "duels": {
                        "total": random.randint(100, 300),
                        "won": random.randint(50, 200)
                    }
                }]
            }
            players.append(player)
        
        return {"response": players}
    
    def generate_mock_player_details(self, player_id):
        """
        Generate mock data for player details.
        
        Args:
            player_id (int): Player ID
        
        Returns:
            dict: Mock API response with player details
        """
        # Just return the same format as top players but with only one player
        top_players = self.generate_mock_top_players()
        
        # If we have a specific player ID, try to find it
        if player_id is not None and top_players["response"]:
            # Just use the first player but change its ID
            player = top_players["response"][0]
            player["player"]["id"] = int(player_id)
            return {"response": [player]}
        
        # Otherwise just return the first player
        return {"response": [top_players["response"][0]]} if top_players["response"] else {"response": []}
    
    def generate_mock_player_statistics(self, player_id):
        """
        Generate mock data for player statistics.
        
        Args:
            player_id (int): Player ID
        
        Returns:
            dict: Mock API response with player statistics
        """
        # Similar to player details but with more focused on statistics
        player_details = self.generate_mock_player_details(player_id)
        
        # Add more detailed statistics if we have player data
        if player_details["response"]:
            player = player_details["response"][0]
            
            # Add match-by-match statistics
            matches = []
            for i in range(10):
                match_stat = {
                    "date": f"2023-{8+i//3}-{1+i}",
                    "opponent": f"Opponent {i+1}",
                    "result": random.choice(["W", "D", "L"]),
                    "minutes": random.randint(60, 90),
                    "rating": round(random.uniform(6.0, 9.0), 1),
                    "goals": random.randint(0, 2),
                    "assists": random.randint(0, 1)
                }
                matches.append(match_stat)
            
            # Add the matches to the player data
            if "statistics" in player and player["statistics"]:
                player["statistics"][0]["matches"] = matches
        
        return player_details
    
    @Slot()
    def get_top_players(self, league_id=39, season=2023):
        """
        Get top players from a specific league and season.
        
        Args:
            league_id (int, optional): League ID. Defaults to 39 (Premier League).
            season (int, optional): Season year. Defaults to 2023.
        """
        params = {
            'league': league_id,
            'season': season
        }
        self.fetch_data('/players/topscorers', params)
    
    @Slot(int)
    def get_player_details(self, player_id):
        """
        Get detailed information about a specific player.
        
        Args:
            player_id (int): Player ID
        """
        params = {
            'id': player_id
        }
        self.fetch_data('/players', params)
    
    @Slot(int)
    def get_player_statistics(self, player_id, season=2023):
        """
        Get statistics for a specific player.
        
        Args:
            player_id (int): Player ID
            season (int, optional): Season year. Defaults to 2023.
        """
        params = {
            'player': player_id,
            'season': season
        }
        self.fetch_data('/players/statistics', params)
    
    def clear_cache(self):
        """Clear the API request cache."""
        requests_cache.clear()