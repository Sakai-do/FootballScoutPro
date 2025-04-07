#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dashboard View Module

This module implements the dashboard view for displaying player statistics
and visualizations.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QPixmap, QColor

import pyqtgraph as pg
import numpy as np


class StatCard(QFrame):
    """
    Widget for displaying a single statistic in a card format.
    """
    
    clicked = Signal(str)  # Signal emitted when card is clicked, with card's title
    
    def __init__(self, title, value, subtitle=None, parent=None):
        """Initialize the stat card."""
        super().__init__(parent)
        
        # Set card style
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            StatCard {
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
            StatCard:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Make the card clickable
        self.setMouseTracking(True)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Subtitle (optional)
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.subtitle_label)
    
    def mousePressEvent(self, event):
        """Handle mouse press events to emit clicked signal."""
        self.clicked.emit(self.title_label.text())
        super().mousePressEvent(event)


class PlayerRow(QFrame):
    """
    Widget for displaying a player row with basic info and stats.
    """
    
    player_clicked = Signal(int)  # Signal emitted when player is clicked, with player ID
    
    def __init__(self, player_data, parent=None):
        """Initialize the player row."""
        super().__init__(parent)
        
        # Set frame style
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            PlayerRow {
                background-color: #ffffff;
                border-radius: 5px;
                border: 1px solid #dee2e6;
                padding: 5px;
                margin: 2px;
            }
            PlayerRow:hover {
                background-color: #f8f9fa;
            }
        """)
        
        # Store player ID
        self.player_id = player_data.get('player_id')
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Player rank/position
        self.rank_label = QLabel(f"#{player_data.get('rank', '')}")
        self.rank_label.setFixedWidth(30)
        layout.addWidget(self.rank_label)
        
        # Player name and team
        player_info = QVBoxLayout()
        self.name_label = QLabel(player_data.get('name', 'Unknown Player'))
        self.name_label.setFont(QFont("Arial", 11, QFont.Bold))
        player_info.addWidget(self.name_label)
        
        self.team_label = QLabel(player_data.get('team_name', ''))
        player_info.addWidget(self.team_label)
        layout.addLayout(player_info)
        
        # Add spacer
        layout.addStretch()
        
        # Player stats (customizable depending on the view)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Create stat fields (example - customize as needed)
        for stat, label in [
            ('rating', 'Rating'),
            ('goals_total', 'Goals'),
            ('assists', 'Assists'),
            ('minutes_played', 'Minutes')
        ]:
            if stat in player_data:
                stat_layout = QVBoxLayout()
                stat_label = QLabel(label)
                stat_label.setFont(QFont("Arial", 8))
                stat_layout.addWidget(stat_label)
                
                value_label = QLabel(str(player_data.get(stat, '')))
                value_label.setFont(QFont("Arial", 11, QFont.Bold))
                value_label.setAlignment(Qt.AlignCenter)
                stat_layout.addWidget(value_label)
                
                stats_layout.addLayout(stat_layout)
        
        layout.addLayout(stats_layout)
        
        # Make the row clickable
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event):
        """Handle mouse press events to emit player_clicked signal."""
        self.player_clicked.emit(self.player_id)
        super().mousePressEvent(event)


class DashboardView(QWidget):
    """
    Widget for displaying the main dashboard.
    """
    
    player_selected = Signal(int)  # Signal emitted when a player is selected
    
    def __init__(self, parent=None):
        """Initialize the dashboard view."""
        super().__init__(parent)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create top stats section
        self.create_top_stats_section()
        
        # Create top players section
        self.create_top_players_section()
        
        # Create charts section
        self.create_charts_section()
    
    def create_top_stats_section(self):
        """Create the top stats section with cards."""
        # Section title
        stats_title = QLabel("League Statistics")
        stats_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.main_layout.addWidget(stats_title)
        
        # Stats cards grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        
        # Sample stats cards (will be populated with real data)
        stats = [
            {"title": "Total Players", "value": "500", "subtitle": "Active in the league"},
            {"title": "Average Goals", "value": "2.7", "subtitle": "Per match"},
            {"title": "Top Scorer", "value": "Player Name", "subtitle": "15 goals"},
            {"title": "Clean Sheets", "value": "45", "subtitle": "This season"}
        ]
        
        for i, stat in enumerate(stats):
            card = StatCard(stat["title"], stat["value"], stat["subtitle"])
            stats_grid.addWidget(card, i // 4, i % 4)
        
        self.main_layout.addLayout(stats_grid)
    
    def create_top_players_section(self):
        """Create the top players section with scrollable list."""
        # Section title
        players_title = QLabel("Top Players")
        players_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.main_layout.addWidget(players_title)
        
        # Player list container
        self.players_container = QWidget()
        self.players_layout = QVBoxLayout(self.players_container)
        
        # Scrollable area for players
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.players_container)
        scroll_area.setFrameShape(QFrame.NoFrame)
        self.main_layout.addWidget(scroll_area)
        
        # This will be populated with actual player data
        self.clear_players()
    
    def create_charts_section(self):
        """Create the charts section with visualizations."""
        # Section title
        charts_title = QLabel("Visualizations")
        charts_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.main_layout.addWidget(charts_title)
        
        # Charts grid
        charts_layout = QHBoxLayout()
        
        # Add sample charts (will be replaced with actual data)
        # Position distribution pie chart
        self.position_chart = self.create_position_distribution_chart()
        charts_layout.addWidget(self.position_chart)
        
        # Goals per position bar chart
        self.goals_chart = self.create_goals_per_position_chart()
        charts_layout.addWidget(self.goals_chart)
        
        self.main_layout.addLayout(charts_layout)
    
    def create_position_distribution_chart(self):
        """Create a pie chart showing player position distribution."""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        
        # Title
        title = QLabel("Position Distribution")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Since PyQtGraph doesn't have a built-in pie chart,
        # we'll create a placeholder that will be replaced with
        # Matplotlib in a more complete implementation
        placeholder = QLabel("Position Distribution Chart")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setMinimumHeight(200)
        placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        layout.addWidget(placeholder)
        
        return chart_widget
    
    def create_goals_per_position_chart(self):
        """Create a bar chart showing goals per position."""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        
        # Title
        title = QLabel("Goals per Position")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Simple bar chart with PyQtGraph
        plot = pg.PlotWidget()
        plot.setBackground('w')
        
        # Will be updated with actual data
        # For now, just placeholder data
        positions = ["Defender", "Midfielder", "Forward"]
        goals = [15, 45, 75]
        x = range(len(positions))
        
        # Create a bar graph using BarGraphItem
        bar_graph = pg.BarGraphItem(x=x, height=goals, width=0.6, brush='b')
        plot.addItem(bar_graph)
        
        # Set axis labels
        axis = plot.getAxis('bottom')
        axis.setTicks([[(i, positions[i]) for i in range(len(positions))]])
        
        layout.addWidget(plot)
        
        return chart_widget
    
    @Slot(object)
    def update_top_players(self, players_df):
        """
        Update the top players section with actual player data.
        
        Args:
            players_df (pd.DataFrame): DataFrame with player data
        """
        self.clear_players()
        
        for i, (_, player) in enumerate(players_df.iterrows()):
            # Add rank to player data
            player_data = player.to_dict()
            player_data['rank'] = i + 1
            
            # Create player row
            player_row = PlayerRow(player_data)
            player_row.player_clicked.connect(self.player_selected)
            
            self.players_layout.addWidget(player_row)
    
    def clear_players(self):
        """Clear the players list."""
        # Remove all existing player rows
        while self.players_layout.count():
            item = self.players_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    @Slot(object)
    def update_charts(self, data):
        """
        Update the charts with actual data.
        
        Args:
            data (dict): Dictionary with chart data
        """
        # Update position distribution chart
        if 'position_distribution' in data:
            positions = data['position_distribution']
            # Update the chart here...
        
        # Update goals per position chart
        if 'goals_per_position' in data:
            goals_data = data['goals_per_position']
            # Update the chart here...