#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Player Controller Module

This module implements the player controller for handling player profiles
and recommendations.
"""

import os
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QObject, Signal, Slot, Qt
from PySide6.QtUiTools import QUiLoader

from views.player_view import PlayerView


class RecommendationPanel(QDialog):
    """
    Dialog for displaying player recommendations.
    """
    
    # Signals
    player_selected = Signal(int)  # Signal emitted when a player is selected
    
    def __init__(self, recommendations, reference_player=None, parent=None):
        """
        Initialize the recommendation panel.
        
        Args:
            recommendations (pd.DataFrame): DataFrame with recommended players
            reference_player (dict, optional): Reference player data. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Load UI from file
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'views', 'ui', 'recommendation_panel.ui')
        self.ui = loader.load(ui_file_path, self)
        
        # Set window properties
        self.setWindowTitle("Player Recommendations")
        self.resize(800, 600)
        
        # Store data
        self.recommendations = recommendations
        self.reference_player = reference_player
        
        # Update UI with recommendations
        self.update_ui()
        
        # Connect signals
        self.ui.pushButton_view_player.clicked.connect(self.on_view_player_clicked)
        self.ui.tableView_recommendations.doubleClicked.connect(self.on_player_double_clicked)
    
    def update_ui(self):
        """Update the UI with recommendation data."""
        # Update title and subtitle
        if self.reference_player:
            self.ui.label_subtitle.setText(f"Based on {self.reference_player.get('name', 'Selected Player')}")
        else:
            self.ui.label_subtitle.setText(f"Based on your criteria")
        
        # Set up table model
        from PySide6.QtGui import QStandardItemModel, QStandardItem
        model = QStandardItemModel()
        
        # Set up headers
        headers = ['Name', 'Team', 'Position', 'Age', 'Rating', 'Similarity']
        model.setHorizontalHeaderLabels(headers)
        
        # Add recommendation data
        for _, player in self.recommendations.iterrows():
            row = []
            for col in ['name', 'team_name', 'position', 'age', 'rating']:
                value = player.get(col, '')
                item = QStandardItem(str(value))
                row.append(item)
            
            # Add similarity score if available
            if 'similarity_score' in player:
                similarity = f"{player['similarity_score'] * 100:.1f}%"
            else:
                similarity = "N/A"
            row.append(QStandardItem(similarity))
            
            model.appendRow(row)
        
        # Set the model to the table view
        self.ui.tableView_recommendations.setModel(model)
        
        # Set column widths
        self.ui.tableView_recommendations.setColumnWidth(0, 150)  # Name
        self.ui.tableView_recommendations.setColumnWidth(1, 150)  # Team
        self.ui.tableView_recommendations.setColumnWidth(2, 100)  # Position
        self.ui.tableView_recommendations.setColumnWidth(3, 60)   # Age
        self.ui.tableView_recommendations.setColumnWidth(4, 80)   # Rating
        self.ui.tableView_recommendations.setColumnWidth(5, 100)  # Similarity
        
        # Create comparison chart if reference player is available
        if self.reference_player and hasattr(self, 'create_comparison_chart'):
            self.create_comparison_chart()
    
    def on_view_player_clicked(self):
        """Handle view player button click."""
        # Get selected player
        index = self.ui.tableView_recommendations.currentIndex()
        if not index.isValid():
            return
        
        # Get player ID from the recommendations DataFrame
        player_id = self.recommendations.iloc[index.row()]['player_id']
        
        # Emit signal to view the player
        self.player_selected.emit(player_id)
    
    def on_player_double_clicked(self, index):
        """
        Handle player double-click.
        
        Args:
            index (QModelIndex): Index of the clicked item
        """
        if not index.isValid():
            return
        
        # Get player ID from the recommendations DataFrame
        player_id = self.recommendations.iloc[index.row()]['player_id']
        
        # Emit signal to view the player
        self.player_selected.emit(player_id)


class PlayerController(QObject):
    """
    Controller for player profiles and recommendations.
    
    This class handles the display and interaction with player profiles
    and recommendation dialogs.
    """
    
    def __init__(self, recommender):
        """
        Initialize the player controller.
        
        Args:
            recommender (PlayerRecommender): Recommender model for player recommendations
        """
        super().__init__()
        
        # Store reference to the recommender model
        self.recommender = recommender
        
        # Keep reference to open dialogs to prevent garbage collection
        self.open_dialogs = []
    
    @Slot(dict)
    def show_player_profile(self, player_data):
        """
        Show a player profile dialog.
        
        Args:
            player_data (dict): Player data dictionary
        """
        # Create player view
        player_view = PlayerView(player_data)
        
        # Connect signals
        player_view.find_similar_requested.connect(self.on_find_similar_clicked)
        
        # Show the dialog
        player_view.exec()
        
        # Store reference to the dialog
        self.open_dialogs.append(player_view)
    
    @Slot(object)
    def show_recommendations(self, recommendations, reference_player=None):
        """
        Show a recommendations dialog.
        
        Args:
            recommendations (pd.DataFrame): DataFrame with recommended players
            reference_player (dict, optional): Reference player data. Defaults to None.
        """
        # Create recommendation panel
        recommendation_panel = RecommendationPanel(recommendations, reference_player)
        
        # Connect signals
        recommendation_panel.player_selected.connect(self.on_recommendation_player_selected)
        
        # Show the dialog
        recommendation_panel.exec()
        
        # Store reference to the dialog
        self.open_dialogs.append(recommendation_panel)
    
    @Slot(int)
    def on_find_similar_clicked(self, player_id):
        """
        Handle find similar players request.
        
        Args:
            player_id (int): Reference player ID
        """
        # Request recommendations from the recommender model
        self.recommender.recommend_similar_players(player_id)
    
    @Slot(int)
    def on_recommendation_player_selected(self, player_id):
        """
        Handle recommendation player selection.
        
        Args:
            player_id (int): Selected player ID
        """
        # This would typically fetch the player data and show the profile
        # For now, just print the player ID
        print(f"Selected player ID: {player_id}")
        
        # In a real implementation, you would fetch the player data and call show_player_profile