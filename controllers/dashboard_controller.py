#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard Controller Module

This module implements the dashboard controller for handling the dashboard view
and its interactions with the data models.
"""

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QObject, Signal, Slot, Qt

import pandas as pd
import numpy as np

from views.dashboard_view import DashboardView


class DashboardController(QObject):
    """
    Controller for the dashboard view.
    
    This class handles the interactions between the dashboard view and
    the data models, updating the view with data and processing user actions.
    """
    
    # Signals
    player_selected = Signal(int)  # Signal emitted when a player is selected, with player ID
    
    def __init__(self, parent_widget, api_client, data_processor):
        """
        Initialize the dashboard controller.
        
        Args:
            parent_widget (QWidget): Parent widget to embed the dashboard view in
            api_client (ApiClient): API client for fetching data
            data_processor (DataProcessor): Data processor for processing and analyzing data
        """
        super().__init__()
        
        # Store references to models
        self.api_client = api_client
        self.data_processor = data_processor
        
        # Create the dashboard view
        self.view = DashboardView()
        
        # Set up the view in the parent widget
        layout = QVBoxLayout(parent_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        
        # Connect signals
        self.view.player_selected.connect(self.player_selected)
    
    @Slot(object)
    def update_dashboard(self, players_df):
        """
        Update the dashboard with player data.
        
        Args:
            players_df (pd.DataFrame): DataFrame with player data
        """
        if players_df is None or len(players_df) == 0:
            return
        
        # Calculate additional metrics
        stats_df = self.data_processor.calculate_player_metrics(players_df)
        
        # Update the top players section
        self.update_top_players(stats_df)
        
        # Prepare and update chart data
        chart_data = self.prepare_chart_data(stats_df)
        self.view.update_charts(chart_data)
    
    def update_top_players(self, players_df):
        """
        Update the top players section of the dashboard.
        
        Args:
            players_df (pd.DataFrame): DataFrame with player data
        """
        # Get top 10 players by rating
        top_players = players_df.sort_values(by='rating', ascending=False).head(10)
        
        # Update the view
        self.view.update_top_players(top_players)
    
    def prepare_chart_data(self, players_df):
        """
        Prepare chart data from player data.
        
        Args:
            players_df (pd.DataFrame): DataFrame with player data
        
        Returns:
            dict: Dictionary with chart data
        """
        chart_data = {}
        
        # Position distribution
        if 'position' in players_df.columns:
            position_counts = players_df['position'].value_counts().to_dict()
            chart_data['position_distribution'] = position_counts
        
        # Goals per position
        if 'position' in players_df.columns and 'goals_total' in players_df.columns:
            goals_by_position = players_df.groupby('position')['goals_total'].sum().to_dict()
            chart_data['goals_per_position'] = goals_by_position
        
        # Additional chart data can be prepared here
        
        return chart_data
    
    @Slot(str)
    def on_league_changed(self, league_id):
        """
        Handle league selection change.
        
        Args:
            league_id (int): Selected league ID
        """
        # Fetch data for the selected league
        self.api_client.get_top_players(league_id=league_id)
    
    @Slot(int)
    def on_season_changed(self, season):
        """
        Handle season selection change.
        
        Args:
            season (int): Selected season year
        """
        # Fetch data for the selected season
        league_id = self.get_current_league_id()
        self.api_client.get_top_players(league_id=league_id, season=season)
    
    @Slot()
    def on_apply_filters(self):
        """Handle filter application."""
        # Apply filters to the current data
        # This would filter the existing data rather than fetching new data
        filtered_df = self.filter_players_data()
        self.update_dashboard(filtered_df)
    
    def get_current_league_id(self):
        """
        Get the current selected league ID.
        
        Returns:
            int: Currently selected league ID
        """
        # This would need to be implemented to get the actual selected league
        # For now, return a default league ID (Premier League)
        return 39
    
    def filter_players_data(self):
        """
        Filter the players data based on the current filters.
        
        Returns:
            pd.DataFrame: Filtered players DataFrame
        """
        # This would need to be implemented to apply actual filters
        # For now, just return the original data
        return self.data_processor.players_df