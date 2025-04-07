#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Processor Module

This module handles data processing, transformation and normalization
of football data for visualization and analysis.
"""

import pandas as pd
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot


class DataProcessor(QObject):
    """
    Process and transform football data for analysis.
    
    This class handles the transformation of raw API data into structured
    formats suitable for visualization and machine learning.
    """
    
    # Signals
    processing_complete = Signal(object)
    processing_error = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the data processor."""
        super().__init__(parent)
        self.players_df = None
        self.teams_df = None
    
    @Slot(dict)
    def process_players_data(self, data):
        """
        Process raw player data from the API.
        
        Args:
            data (dict): Raw API response for players
        """
        try:
            # Extract player data from API response
            players = data.get('response', [])
            
            if not players:
                self.processing_error.emit("No player data found in the API response")
                return
            
            # Create a structured DataFrame
            processed_data = []
            
            for player in players:
                player_info = player.get('player', {})
                stats = player.get('statistics', [])
                
                for stat in stats:
                    team = stat.get('team', {})
                    league = stat.get('league', {})
                    games = stat.get('games', {})
                    shots = stat.get('shots', {})
                    goals = stat.get('goals', {})
                    passes = stat.get('passes', {})
                    tackles = stat.get('tackles', {})
                    duels = stat.get('duels', {})
                    
                    processed_data.append({
                        'player_id': player_info.get('id'),
                        'name': player_info.get('name'),
                        'firstname': player_info.get('firstname'),
                        'lastname': player_info.get('lastname'),
                        'age': player_info.get('age'),
                        'nationality': player_info.get('nationality'),
                        'height': player_info.get('height'),
                        'weight': player_info.get('weight'),
                        'position': player_info.get('position'),
                        'team_id': team.get('id'),
                        'team_name': team.get('name'),
                        'league_id': league.get('id'),
                        'league_name': league.get('name'),
                        'appearances': games.get('appearances'),
                        'minutes_played': games.get('minutes'),
                        'rating': games.get('rating'),
                        'shots_total': shots.get('total'),
                        'shots_on_target': shots.get('on'),
                        'goals_total': goals.get('total'),
                        'assists': goals.get('assists'),
                        'passes_total': passes.get('total'),
                        'passes_accuracy': passes.get('accuracy'),
                        'tackles_total': tackles.get('total'),
                        'tackles_blocks': tackles.get('blocks'),
                        'tackles_interceptions': tackles.get('interceptions'),
                        'duels_total': duels.get('total'),
                        'duels_won': duels.get('won')
                    })
            
            # Create DataFrame
            self.players_df = pd.DataFrame(processed_data)
            
            # Handle missing values
            self.players_df = self.handle_missing_values(self.players_df)
            
            # Emit processed data
            self.processing_complete.emit(self.players_df)
            
        except Exception as e:
            self.processing_error.emit(f"Error processing player data: {str(e)}")
    
    def handle_missing_values(self, df):
        """
        Handle missing values in the DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with possibly missing values
        
        Returns:
            pd.DataFrame: DataFrame with handled missing values
        """
        # Fill numeric columns with 0
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # Fill string columns with empty string
        string_cols = df.select_dtypes(include=['object']).columns
        df[string_cols] = df[string_cols].fillna('')
        
        return df
    
    def calculate_player_metrics(self, df=None):
        """
        Calculate additional player metrics.
        
        Args:
            df (pd.DataFrame, optional): Player DataFrame. If None, uses self.players_df.
        
        Returns:
            pd.DataFrame: DataFrame with additional metrics
        """
        if df is None:
            df = self.players_df.copy()
        
        if df is None:
            self.processing_error.emit("No player data available for metrics calculation")
            return None
        
        # Calculate additional metrics
        try:
            # Calculate minutes per appearance
            df['minutes_per_appearance'] = df['minutes_played'] / df['appearances']
            
            # Calculate pass completion rate
            df['pass_completion_rate'] = df['passes_accuracy']
            
            # Calculate shot conversion rate
            df['shot_conversion_rate'] = np.where(
                df['shots_total'] > 0,
                df['goals_total'] / df['shots_total'] * 100,
                0
            )
            
            # Calculate duels success rate
            df['duels_success_rate'] = np.where(
                df['duels_total'] > 0,
                df['duels_won'] / df['duels_total'] * 100,
                0
            )
            
            # Clean up infinite values
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df = self.handle_missing_values(df)
            
            return df
            
        except Exception as e:
            self.processing_error.emit(f"Error calculating metrics: {str(e)}")
            return df
    
    def get_player_by_id(self, player_id):
        """
        Get player data by ID.
        
        Args:
            player_id (int): Player ID
        
        Returns:
            pd.Series: Player data as a Series, or None if not found
        """
        if self.players_df is None:
            return None
        
        player = self.players_df[self.players_df['player_id'] == player_id]
        
        if len(player) == 0:
            return None
        
        return player.iloc[0]
    
    def get_players_by_position(self, position):
        """
        Get players by position.
        
        Args:
            position (str): Player position (e.g., 'Midfielder')
        
        Returns:
            pd.DataFrame: Filtered DataFrame with players of the specified position
        """
        if self.players_df is None:
            return None
        
        return self.players_df[self.players_df['position'] == position]
    
    def get_top_players_by_metric(self, metric, n=10, ascending=False):
        """
        Get top N players by a specific metric.
        
        Args:
            metric (str): Metric column name
            n (int, optional): Number of players to return. Defaults to 10.
            ascending (bool, optional): Sort order. Defaults to False (descending).
        
        Returns:
            pd.DataFrame: DataFrame with top N players
        """
        if self.players_df is None or metric not in self.players_df.columns:
            return None
        
        return self.players_df.sort_values(by=metric, ascending=ascending).head(n)