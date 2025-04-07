#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Player View Module

This module implements the player view for displaying detailed player profiles
and statistics.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QPushButton, QTableView, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont, QPixmap, QStandardItemModel, QStandardItem

import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtUiTools import QUiLoader


class RadarChart(FigureCanvas):
    """
    Matplotlib-based radar chart for visualizing player attributes.
    """
    
    def __init__(self, labels, values, max_values=None, title=None, parent=None):
        """
        Initialize the radar chart.
        
        Args:
            labels (list): List of attribute names
            values (list): List of attribute values
            max_values (list, optional): List of maximum values for scaling. Defaults to None.
            title (str, optional): Chart title. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        # Create figure and add subplot
        self.fig = plt.figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111, polar=True)
        super().__init__(self.fig)
        
        self.setParent(parent)
        
        # Scale the figure
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        # Set properties
        self.labels = labels
        self.values = values
        self.max_values = max_values or [100] * len(labels)
        self.title = title
        
        # Draw the chart
        self.draw_chart()
    
    def draw_chart(self):
        """Draw the radar chart."""
        # Clear the axes
        self.ax.clear()
        
        # Number of variables
        N = len(self.labels)
        
        # Compute angle for each variable
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Normalize values
        normalized_values = [v / m for v, m in zip(self.values, self.max_values)]
        normalized_values += normalized_values[:1]  # Close the loop
        
        # Draw the chart
        self.ax.plot(angles, normalized_values, linewidth=2, linestyle='solid', color='#3498db')
        self.ax.fill(angles, normalized_values, alpha=0.3, color='#3498db')
        
        # Add labels
        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(self.labels)
        
        # Set y-ticks
        self.ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        self.ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        
        # Add grid
        self.ax.grid(True)
        
        # Add title if provided
        if self.title:
            self.ax.set_title(self.title, pad=20, fontsize=15)
        
        # Redraw
        self.fig.canvas.draw()
    
    def update_values(self, values, max_values=None):
        """
        Update the chart with new values.
        
        Args:
            values (list): New attribute values
            max_values (list, optional): New maximum values for scaling. Defaults to None.
        """
        self.values = values
        if max_values:
            self.max_values = max_values
        self.draw_chart()


class LineChartWidget(pg.PlotWidget):
    """
    PyQtGraph-based line chart for visualizing performance trends.
    """
    
    def __init__(self, parent=None):
        """Initialize the line chart."""
        super().__init__(parent)
        
        # Set background color
        self.setBackground('w')
        
        # Configure axes
        self.getAxis('left').setPen((0, 0, 0))
        self.getAxis('bottom').setPen((0, 0, 0))
        
        # Add legend
        self.addLegend()
    
    def plot_trend(self, x_data, y_data, name=None, color=None):
        """
        Plot a trend line with the given data.
        
        Args:
            x_data (list): X-axis data (e.g., match dates)
            y_data (list): Y-axis data (e.g., ratings)
            name (str, optional): Line name for legend. Defaults to None.
            color (tuple, optional): RGB color tuple. Defaults to None.
        """
        pen = pg.mkPen(color=color or (30, 144, 255), width=2)
        self.plot(x_data, y_data, name=name, pen=pen, symbol='o', symbolSize=6)


class PlayerView(QDialog):
    """
    Dialog for displaying detailed player profile and statistics.
    """
    
    find_similar_requested = Signal(int)  # Signal emitted when 'Find Similar Players' is clicked
    
    def __init__(self, player_data=None, parent=None):
        """
        Initialize the player view.
        
        Args:
            player_data (dict, optional): Player data dictionary. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Load UI from file
        loader = QUiLoader()
        ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'player_profile.ui')
        self.ui = loader.load(ui_file_path, self)
        
        # Set window properties
        self.setWindowTitle("Player Profile")
        self.resize(900, 700)
        
        # Set up the main layout to contain the loaded UI
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Connect signals
        self.ui.pushButton_find_similar.clicked.connect(self.on_find_similar_clicked)
        
        # Initialize charts
        self.initialize_charts()
        
        # Set up data models for tables
        self.setup_tables()
        
        # Update UI if player data is provided
        if player_data:
            self.update_player_data(player_data)
    
    def initialize_charts(self):
        """Initialize charts for player visualization."""
        # Create radar chart for overview tab
        radar_layout = QVBoxLayout(self.ui.widget_radar_chart)
        radar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sample labels and values (will be updated with actual data)
        labels = ["Pace", "Shooting", "Passing", "Dribbling", "Defending", "Physical"]
        values = [70, 65, 80, 75, 60, 70]
        
        self.radar_chart = RadarChart(labels, values)
        radar_layout.addWidget(self.radar_chart)
        
        # Create trend chart for form tab
        trend_layout = QVBoxLayout(self.ui.widget_trend_chart)
        trend_layout.setContentsMargins(0, 0, 0, 0)
        
        self.trend_chart = LineChartWidget()
        trend_layout.addWidget(self.trend_chart)
        
        # Create charts for detailed stats tabs
        self.setup_detailed_charts()
    
    def setup_detailed_charts(self):
        """Set up charts for detailed statistics tabs."""
        # Attacking chart
        attacking_layout = QVBoxLayout(self.ui.widget_attacking_chart)
        attacking_layout.setContentsMargins(0, 0, 0, 0)
        
        self.attacking_chart = pg.PlotWidget()
        self.attacking_chart.setBackground('w')
        attacking_layout.addWidget(self.attacking_chart)
        
        # Passing chart
        passing_layout = QVBoxLayout(self.ui.widget_passing_chart)
        passing_layout.setContentsMargins(0, 0, 0, 0)
        
        self.passing_chart = pg.PlotWidget()
        self.passing_chart.setBackground('w')
        passing_layout.addWidget(self.passing_chart)
        
        # Defending chart
        defending_layout = QVBoxLayout(self.ui.widget_defending_chart)
        defending_layout.setContentsMargins(0, 0, 0, 0)
        
        self.defending_chart = pg.PlotWidget()
        self.defending_chart.setBackground('w')
        defending_layout.addWidget(self.defending_chart)
    
    def setup_tables(self):
        """Set up data models for tables."""
        # Attacking stats table
        self.attacking_model = QStandardItemModel()
        self.attacking_model.setHorizontalHeaderLabels(["Statistic", "Value", "Per 90"])
        self.ui.tableView_attacking.setModel(self.attacking_model)
        self.ui.tableView_attacking.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView_attacking.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Passing stats table
        self.passing_model = QStandardItemModel()
        self.passing_model.setHorizontalHeaderLabels(["Statistic", "Value", "Per 90"])
        self.ui.tableView_passing.setModel(self.passing_model)
        self.ui.tableView_passing.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView_passing.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Defending stats table
        self.defending_model = QStandardItemModel()
        self.defending_model.setHorizontalHeaderLabels(["Statistic", "Value", "Per 90"])
        self.ui.tableView_defending.setModel(self.defending_model)
        self.ui.tableView_defending.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView_defending.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Form history table
        self.history_model = QStandardItemModel()
        self.history_model.setHorizontalHeaderLabels(["Date", "Opponent", "Result", "Minutes", "Rating", "Goals", "Assists"])
        self.ui.tableView_history.setModel(self.history_model)
        self.ui.tableView_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableView_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    @Slot(dict)
    def update_player_data(self, player_data):
        """
        Update the player profile with new data.
        
        Args:
            player_data (dict): Player data dictionary
        """
        if not player_data:
            return
        
        # Update player info
        self.player_id = player_data.get('player_id')
        self.ui.label_player_name.setText(player_data.get('name', 'Unknown Player'))
        self.ui.label_player_info.setText(f"{player_data.get('position', 'Unknown')}, {player_data.get('team_name', 'Unknown Team')}")
        self.ui.label_player_nationality.setText(player_data.get('nationality', 'Unknown'))
        
        # Physical attributes
        self.ui.label_player_age.setText(f"Age: {player_data.get('age', 'Unknown')}")
        self.ui.label_player_height.setText(f"Height: {player_data.get('height', 'Unknown')}")
        self.ui.label_player_weight.setText(f"Weight: {player_data.get('weight', 'Unknown')}")
        
        # Rating
        self.ui.label_player_rating.setText(str(player_data.get('rating', 'N/A')))
        
        # Update stats
        self.update_overview_stats(player_data)
        self.update_detailed_stats(player_data)
        self.update_form_history(player_data)
        
        # Update radar chart
        self.update_radar_chart(player_data)
        
        # Update trend chart
        self.update_trend_chart(player_data)
    
    def update_overview_stats(self, player_data):
        """
        Update the overview statistics.
        
        Args:
            player_data (dict): Player data dictionary
        """
        # Update key stats
        self.ui.label_appearances_value.setText(str(player_data.get('appearances', 'N/A')))
        self.ui.label_minutes_value.setText(str(player_data.get('minutes_played', 'N/A')))
        self.ui.label_goals_value.setText(str(player_data.get('goals_total', 'N/A')))
        self.ui.label_assists_value.setText(str(player_data.get('assists', 'N/A')))
        
        # Shots
        shots_total = player_data.get('shots_total', 0)
        shots_on = player_data.get('shots_on_target', 0)
        self.ui.label_shots_value.setText(f"{shots_total} ({shots_on})")
        
        # Pass completion
        pass_accuracy = player_data.get('passes_accuracy', 'N/A')
        if pass_accuracy != 'N/A':
            self.ui.label_passes_value.setText(f"{pass_accuracy}%")
        else:
            self.ui.label_passes_value.setText("N/A")
        
        # Tackles
        self.ui.label_tackles_value.setText(str(player_data.get('tackles_total', 'N/A')))
        
        # Duels
        duels_total = player_data.get('duels_total', 0)
        duels_won = player_data.get('duels_won', 0)
        if duels_total > 0:
            duels_success = (duels_won / duels_total) * 100
            self.ui.label_duels_value.setText(f"{duels_success:.1f}%")
        else:
            self.ui.label_duels_value.setText("N/A")
    
    def update_detailed_stats(self, player_data):
        """
        Update the detailed statistics tables.
        
        Args:
            player_data (dict): Player data dictionary
        """
        # Clear existing data
        self.attacking_model.setRowCount(0)
        self.passing_model.setRowCount(0)
        self.defending_model.setRowCount(0)
        
        # Minutes per 90 calculation
        minutes = player_data.get('minutes_played', 0)
        per90_factor = 90 / minutes if minutes > 0 else 0
        
        # Attacking stats
        attacking_stats = [
            ("Goals", player_data.get('goals_total', 0), player_data.get('goals_total', 0) * per90_factor),
            ("Shots", player_data.get('shots_total', 0), player_data.get('shots_total', 0) * per90_factor),
            ("Shots on Target", player_data.get('shots_on_target', 0), player_data.get('shots_on_target', 0) * per90_factor),
            ("Shot Accuracy", f"{player_data.get('shot_accuracy', 0):.1f}%", "-"),
            ("Shot Conversion", f"{player_data.get('shot_conversion_rate', 0):.1f}%", "-"),
        ]
        
        for stat in attacking_stats:
            self.add_table_row(self.attacking_model, stat)
        
        # Passing stats
        passing_stats = [
            ("Passes", player_data.get('passes_total', 0), player_data.get('passes_total', 0) * per90_factor),
            ("Pass Accuracy", f"{player_data.get('passes_accuracy', 0):.1f}%", "-"),
            ("Key Passes", player_data.get('key_passes', 0), player_data.get('key_passes', 0) * per90_factor),
            ("Assists", player_data.get('assists', 0), player_data.get('assists', 0) * per90_factor),
        ]
        
        for stat in passing_stats:
            self.add_table_row(self.passing_model, stat)
        
        # Defending stats
        defending_stats = [
            ("Tackles", player_data.get('tackles_total', 0), player_data.get('tackles_total', 0) * per90_factor),
            ("Interceptions", player_data.get('tackles_interceptions', 0), player_data.get('tackles_interceptions', 0) * per90_factor),
            ("Blocks", player_data.get('tackles_blocks', 0), player_data.get('tackles_blocks', 0) * per90_factor),
            ("Duels Won", player_data.get('duels_won', 0), player_data.get('duels_won', 0) * per90_factor),
            ("Duels Success", f"{player_data.get('duels_success_rate', 0):.1f}%", "-"),
        ]
        
        for stat in defending_stats:
            self.add_table_row(self.defending_model, stat)
        
        # Update charts
        self.update_detailed_charts(player_data)
    
    def add_table_row(self, model, data):
        """
        Add a row to a table model.
        
        Args:
            model (QStandardItemModel): Table model
            data (tuple): Row data (stat name, value, per 90 value)
        """
        row = []
        for item in data:
            if isinstance(item, float):
                row.append(QStandardItem(f"{item:.2f}"))
            else:
                row.append(QStandardItem(str(item)))
        
        model.appendRow(row)
    
    def update_form_history(self, player_data):
        """
        Update the form history table.
        
        Args:
            player_data (dict): Player data dictionary
        """
        # Clear existing data
        self.history_model.setRowCount(0)
        
        # Form history data (this would typically come from an API call or nested data)
        # For demonstration, we'll create some sample data
        history = player_data.get('history', [])
        
        if not history:
            # Generate some placeholder data if not available
            matches = min(player_data.get('appearances', 5), 10)  # Limit to 10 matches
            history = []
            
            for i in range(matches):
                rating = max(5.0, min(9.0, float(player_data.get('rating', 7.0)) + (np.random.random() - 0.5)))
                
                match = {
                    'date': f"2023-{10-i:02d}-{(30-i)%31:02d}",
                    'opponent': f"Opponent {i+1}",
                    'result': np.random.choice(['W', 'D', 'L'], p=[0.5, 0.3, 0.2]),
                    'minutes': min(90, player_data.get('minutes_played', 90) // matches),
                    'rating': f"{rating:.1f}",
                    'goals': np.random.randint(0, 2) if player_data.get('position') in ['Forward', 'Midfielder'] else 0,
                    'assists': np.random.randint(0, 2) if player_data.get('position') in ['Forward', 'Midfielder'] else 0,
                }
                history.append(match)
        
        # Add data to table
        for match in history:
            row = [
                QStandardItem(str(match.get('date', ''))),
                QStandardItem(str(match.get('opponent', ''))),
                QStandardItem(str(match.get('result', ''))),
                QStandardItem(str(match.get('minutes', ''))),
                QStandardItem(str(match.get('rating', ''))),
                QStandardItem(str(match.get('goals', ''))),
                QStandardItem(str(match.get('assists', ''))),
            ]
            self.history_model.appendRow(row)
    
    def update_radar_chart(self, player_data):
        """
        Update the radar chart with player attributes.
        
        Args:
            player_data (dict): Player data dictionary
        """
        # Define attributes based on position
        position = player_data.get('position', '')
        
        if 'Forward' in position:
            labels = ["Finishing", "Shot Power", "Speed", "Dribbling", "Passing", "Physical"]
            values = [
                player_data.get('shot_conversion_rate', 0) * 1.2,  # Finishing
                min(100, player_data.get('shots_on_target', 0) / max(1, player_data.get('shots_total', 1)) * 130),  # Shot Power
                85,  # Speed (placeholder)
                min(100, player_data.get('passes_accuracy', 0) * 1.1),  # Dribbling (using pass accuracy as proxy)
                min(100, player_data.get('passes_accuracy', 0)),  # Passing
                min(100, player_data.get('duels_success_rate', 0) * 1.1),  # Physical
            ]
        
        elif 'Midfielder' in position:
            labels = ["Passing", "Vision", "Ball Control", "Stamina", "Tackling", "Shooting"]
            values = [
                min(100, player_data.get('passes_accuracy', 0) * 1.1),  # Passing
                min(100, player_data.get('assists', 0) * 10),  # Vision
                min(100, player_data.get('passes_accuracy', 0) * 1.05),  # Ball Control
                90,  # Stamina (placeholder)
                min(100, player_data.get('tackles_total', 0) * 2),  # Tackling
                min(100, player_data.get('shot_conversion_rate', 0) * 1.1),  # Shooting
            ]
        
        elif 'Defender' in position:
            labels = ["Tackling", "Marking", "Heading", "Strength", "Positioning", "Passing"]
            values = [
                min(100, player_data.get('tackles_total', 0) * 2),  # Tackling
                min(100, player_data.get('tackles_interceptions', 0) * 3),  # Marking
                min(100, player_data.get('duels_success_rate', 0) * 1.1),  # Heading
                min(100, player_data.get('duels_success_rate', 0) * 1.05),  # Strength
                min(100, player_data.get('tackles_blocks', 0) * 5),  # Positioning
                min(100, player_data.get('passes_accuracy', 0)),  # Passing
            ]
        
        else:  # Default or Goalkeeper
            labels = ["Reflexes", "Handling", "Positioning", "Kicking", "Speed", "Leadership"]
            values = [80, 75, 85, 70, 60, 80]  # Placeholder values
        
        # Update the radar chart
        if hasattr(self, 'radar_chart'):
            self.radar_chart.labels = labels
            self.radar_chart.update_values(values)
    
    def update_trend_chart(self, player_data):
        """
        Update the trend chart with player form history.
        
        Args:
            player_data (dict): Player data dictionary
        """
        # Clear existing plots
        self.trend_chart.clear()
        
        # Form history data
        history = player_data.get('history', [])
        
        if not history:
            # Generate some placeholder data if not available
            matches = min(player_data.get('appearances', 5), 10)  # Limit to 10 matches
            
            # X-axis: match numbers
            x_data = list(range(1, matches + 1))
            
            # Rating trend: slightly random around the player's overall rating
            base_rating = float(player_data.get('rating', 7.0))
            rating_trend = [max(5.0, min(9.0, base_rating + (np.random.random() - 0.5))) for _ in range(matches)]
            
            # Plot the trend
            self.trend_chart.plot_trend(x_data, rating_trend, name="Rating", color=(52, 152, 219))
            
            # Set axis labels
            self.trend_chart.setLabel('left', 'Rating')
            self.trend_chart.setLabel('bottom', 'Match')
        else:
            # Use actual history data
            # This would require parsing the history data correctly
            pass
    
    def update_detailed_charts(self, player_data):
        """
        Update the detailed charts for each stat category.
        
        Args:
            player_data (dict): Player data dictionary
        """
        # Attacking chart (e.g., shots and goals distribution)
        self.attacking_chart.clear()
        
        # Placeholder data for demonstration
        categories = ['Inside Box', 'Outside Box', 'Headers', 'Free Kicks', 'Penalties']
        goals = [3, 1, 1, 0, 0]  # Placeholder
        shots = [8, 7, 3, 1, 1]  # Placeholder
        
        # Create bar graph for shots and goals
        x = np.arange(len(categories))
        bar_width = 0.35
        
        shots_bar = pg.BarGraphItem(x=x - bar_width/2, height=shots, width=bar_width, brush=(70, 130, 180))
        goals_bar = pg.BarGraphItem(x=x + bar_width/2, height=goals, width=bar_width, brush=(255, 99, 71))
        
        self.attacking_chart.addItem(shots_bar)
        self.attacking_chart.addItem(goals_bar)
        
        # Add legend manually
        legend = pg.LegendItem()
        legend.setParentItem(self.attacking_chart.graphicsItem())
        legend.addItem(pg.PlotDataItem(pen=pg.mkPen(color=(70, 130, 180), width=10)), 'Shots')
        legend.addItem(pg.PlotDataItem(pen=pg.mkPen(color=(255, 99, 71), width=10)), 'Goals')
        
        # Similar approach for passing and defending charts
        # ...
    
    @Slot()
    def on_find_similar_clicked(self):
        """Handle click on 'Find Similar Players' button."""
        if hasattr(self, 'player_id'):
            self.find_similar_requested.emit(self.player_id)