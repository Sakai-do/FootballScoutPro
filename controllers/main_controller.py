#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Controller Module

This module implements the main controller for the Football Scout Pro application.
It coordinates between the UI views and the data models.
"""

from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QDialog, QFileDialog, QProgressDialog
)
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtUiTools import QUiLoader
import os

from models.api_client import ApiClient
from models.data_processor import DataProcessor
from models.recommender import PlayerRecommender

from controllers.dashboard_controller import DashboardController
from controllers.player_controller import PlayerController

from views.player_view import PlayerView
from views.settings_dialog import SettingsDialog


class MainController(QMainWindow):
    """
    Main controller for the Football Scout Pro application.
    
    This class coordinates between the UI views and the data models,
    handling user interactions and updating the UI accordingly.
    """
    
    def __init__(self, parent=None):
        """Initialize the main controller."""
        super().__init__(parent)
        
        # Load UI from file
        ui_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'views', 'ui', 'main_window.ui')
        loader = QUiLoader()
        self.ui = loader.load(ui_file_path, self)
        
        # Set up the main window
        self.setWindowTitle("Football Scout Pro")
        self.setCentralWidget(self.ui)
        self.resize(1200, 800)
        
        # Initialize models
        self.api_client = ApiClient()
        self.data_processor = DataProcessor()
        self.recommender = PlayerRecommender()
        
        # Initialize controllers
        self.dashboard_controller = DashboardController(
            self.ui.tab_dashboard,
            self.api_client,
            self.data_processor
        )
        self.player_controller = PlayerController(
            self.recommender
        )
        
        # Connect signals and slots
        self.connect_signals()
        
        # Set up initial UI state
        self.setup_ui()
        
        # Load initial data
        self.load_initial_data()
    
    def connect_signals(self):
        """Connect signals and slots."""
        # API client signals
        self.api_client.data_fetched.connect(self.on_data_fetched)
        self.api_client.error_occurred.connect(self.show_error)
        self.api_client.request_started.connect(self.on_request_started)
        self.api_client.request_finished.connect(self.on_request_finished)
        
        # Data processor signals
        self.data_processor.processing_complete.connect(self.on_data_processed)
        self.data_processor.processing_error.connect(self.show_error)
        
        # Recommender signals
        self.recommender.recommendation_ready.connect(self.on_recommendations_ready)
        self.recommender.error_occurred.connect(self.show_error)
        
        # Dashboard controller signals
        self.dashboard_controller.player_selected.connect(self.on_player_selected)
        
        # UI signals
        self.ui.actionSettings.triggered.connect(self.show_settings)
        self.ui.actionAbout.triggered.connect(self.show_about)
        self.ui.actionExit.triggered.connect(self.close)
        
        # Tab widget signals
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)
        
        # Player finder tab signals
        self.ui.pushButton_search.clicked.connect(self.on_search_clicked)
        self.ui.pushButton_advanced_search.clicked.connect(self.on_advanced_search_clicked)
        
        # Recommender tab signals
        self.ui.pushButton_recommend.clicked.connect(self.on_recommend_clicked)
    
    def setup_ui(self):
        """Set up the initial UI state."""
        # Populate league combobox
        self.ui.comboBox_league.addItem("Premier League", 39)
        self.ui.comboBox_league.addItem("La Liga", 140)
        self.ui.comboBox_league.addItem("Bundesliga", 78)
        self.ui.comboBox_league.addItem("Serie A", 135)
        self.ui.comboBox_league.addItem("Ligue 1", 61)
        
        # Populate season combobox
        for season in range(2023, 2019, -1):
            self.ui.comboBox_season.addItem(str(season), season)
        
        # Populate position comboboxes
        positions = ["All Positions", "Goalkeeper", "Defender", "Midfielder", "Forward"]
        for combo in [self.ui.comboBox_position, self.ui.comboBox_position_2, self.ui.comboBox_position_3]:
            for position in positions:
                combo.addItem(position)
        
        # Set status
        self.ui.label_status.setText("Ready")
    
    def load_initial_data(self):
        """Load initial data when the application starts."""
        league_id = self.ui.comboBox_league.currentData()
        season = self.ui.comboBox_season.currentData()
        
        # Fetch top players
        self.api_client.get_top_players(league_id, season)
    
    @Slot(dict)
    def on_data_fetched(self, data):
        """
        Handle fetched data from the API.
        
        Args:
            data (dict): API response data
        """
        # Process the data
        self.data_processor.process_players_data(data)
    
    @Slot(object)
    def on_data_processed(self, processed_data):
        """
        Handle processed data.
        
        Args:
            processed_data (pd.DataFrame): Processed player data
        """
        # Update dashboard with the processed data
        self.dashboard_controller.update_dashboard(processed_data)
        
        # Set data for the recommender
        self.recommender.set_data(processed_data)
        
        # Train recommender models
        QTimer.singleShot(100, self.recommender.train_models)
    
    @Slot(object)
    def on_recommendations_ready(self, recommendations):
        """
        Handle ready recommendations.
        
        Args:
            recommendations (pd.DataFrame): Recommended players dataframe
        """
        # Update the recommendations view
        self.player_controller.show_recommendations(recommendations)
    
    @Slot()
    def on_request_started(self):
        """Handle API request start."""
        self.ui.label_status.setText("Loading data...")
        # Could add a progress indicator here
    
    @Slot()
    def on_request_finished(self):
        """Handle API request completion."""
        self.ui.label_status.setText("Ready")
    
    @Slot(int)
    def on_player_selected(self, player_id):
        """
        Handle player selection.
        
        Args:
            player_id (int): Selected player ID
        """
        # Get player data from the processor
        player = self.data_processor.get_player_by_id(player_id)
        
        if player is not None:
            # Convert Series to dict
            player_data = player.to_dict()
            
            # Show player profile
            self.player_controller.show_player_profile(player_data)
    
    @Slot(int)
    def on_tab_changed(self, index):
        """
        Handle tab widget tab changes.
        
        Args:
            index (int): Index of the selected tab
        """
        # Handle specific actions when switching to different tabs
        pass
    
    @Slot()
    def on_search_clicked(self):
        """Handle search button click."""
        player_name = self.ui.lineEdit_player_name.text().strip()
        
        if not player_name:
            self.show_error("Please enter a player name.")
            return
        
        # Search logic would go here
        # For now, just show a message
        self.ui.label_status.setText(f"Searching for '{player_name}'...")
    
    @Slot()
    def on_advanced_search_clicked(self):
        """Handle advanced search button click."""
        # Get search criteria
        position = self.ui.comboBox_position_2.currentText()
        team = self.ui.comboBox_team.currentText()
        min_rating = self.ui.doubleSpinBox_min_rating.value()
        
        # Search logic would go here
        # For now, just show a message
        criteria = []
        if position != "All Positions":
            criteria.append(position)
        if team:
            criteria.append(f"Team: {team}")
        criteria.append(f"Min Rating: {min_rating}")
        
        self.ui.label_status.setText(f"Searching for players: {', '.join(criteria)}...")
    
    @Slot()
    def on_recommend_clicked(self):
        """Handle recommend button click."""
        # Get recommendation criteria
        reference_player = self.ui.lineEdit_reference_player.text().strip()
        position = self.ui.comboBox_position_3.currentText()
        min_rating = self.ui.doubleSpinBox_min_rating_2.value()
        max_age = self.ui.spinBox_max_age.value()
        
        # Advanced criteria
        passing = self.ui.checkBox_passing.isChecked()
        defensive = self.ui.checkBox_defensive.isChecked()
        finishing = self.ui.checkBox_finishing.isChecked()
        physical = self.ui.checkBox_physical.isChecked()
        
        # Create criteria dictionary
        criteria = {
            'position': position if position != "All Positions" else None,
            'min_rating': min_rating,
            'max_age': max_age
        }
        
        # Add advanced criteria
        min_pass_accuracy = 80 if passing else None
        min_tackles = 3 if defensive else None
        min_shot_conversion = 20 if finishing else None
        min_duels_success = 60 if physical else None
        
        if min_pass_accuracy:
            criteria['min_passes_accuracy'] = min_pass_accuracy
        if min_tackles:
            criteria['min_tackles_total'] = min_tackles
        if min_shot_conversion:
            criteria['min_shot_conversion_rate'] = min_shot_conversion
        if min_duels_success:
            criteria['min_duels_success_rate'] = min_duels_success
        
        # If reference player is provided, use similarity-based recommendation
        if reference_player:
            # Search for the player in the database
            # This is a simplified approach - in a real app, you'd want a more robust search
            found_players = self.data_processor.players_df[
                self.data_processor.players_df['name'].str.contains(reference_player, case=False)
            ]
            
            if len(found_players) > 0:
                # Use the first matching player
                player_id = found_players.iloc[0]['player_id']
                self.recommender.recommend_similar_players(player_id)
            else:
                self.show_error(f"Player '{reference_player}' not found.")
        else:
            # Use criteria-based recommendation
            self.recommender.recommend_by_criteria(criteria)
    
    @Slot()
    def show_settings(self):
        """Show the settings dialog."""
        settings_dialog = SettingsDialog(self)
        settings_dialog.settings_changed.connect(self.on_settings_changed)
        settings_dialog.exec()
    
    @Slot(dict)
    def on_settings_changed(self, config):
        """
        Handle settings changes.
        
        Args:
            config (dict): New configuration settings
        """
        # Recreate the API client with new settings
        old_client = self.api_client
        self.api_client = ApiClient()
        
        # Disconnect old signals and connect new ones
        old_client.data_fetched.disconnect(self.on_data_fetched)
        old_client.error_occurred.disconnect(self.show_error)
        old_client.request_started.disconnect(self.on_request_started)
        old_client.request_finished.disconnect(self.on_request_finished)
        
        self.api_client.data_fetched.connect(self.on_data_fetched)
        self.api_client.error_occurred.connect(self.show_error)
        self.api_client.request_started.connect(self.on_request_started)
        self.api_client.request_finished.connect(self.on_request_finished)
        
        # Update the dashboard controller with the new API client
        self.dashboard_controller.api_client = self.api_client
        
        # Reload data with new settings
        self.load_initial_data()
        
        # Show confirmation
        self.ui.label_status.setText("Settings updated")
    
    @Slot()
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Football Scout Pro",
            "Football Scout Pro v1.0\n\n"
            "A desktop application for football scouting and player analysis.\n\n"
            "© 2023 All rights reserved."
        )
    
    @Slot(str)
    def show_error(self, message):
        """
        Show an error message.
        
        Args:
            message (str): Error message to display
        """
        QMessageBox.critical(
            self,
            "Error",
            message
        )