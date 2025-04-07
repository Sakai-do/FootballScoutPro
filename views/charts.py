#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Charts Module

This module implements custom chart components for visualizing player
and team statistics.
"""

import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class BarChartWidget(pg.PlotWidget):
    """
    Custom bar chart widget based on PyQtGraph.
    """
    
    def __init__(self, title=None, parent=None):
        """
        Initialize the bar chart widget.
        
        Args:
            title (str, optional): Chart title. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Set background color
        self.setBackground('w')
        
        # Configure axes
        self.getAxis('left').setPen((0, 0, 0))
        self.getAxis('bottom').setPen((0, 0, 0))
        
        # Add title if provided
        if title:
            self.setTitle(title, color=(0, 0, 0), size='14pt')
        
        # Add grid
        self.showGrid(x=False, y=True)
        
        # Add legend
        self.addLegend()
    
    def plot_bars(self, categories, values, color=None, name=None):
        """
        Plot bars for the given categories and values.
        
        Args:
            categories (list): List of category names
            values (list): List of values for each category
            color (tuple, optional): RGB color tuple. Defaults to None.
            name (str, optional): Name for legend. Defaults to None.
        """
        x = np.arange(len(categories))
        bar_item = pg.BarGraphItem(x=x, height=values, width=0.6, brush=color or (52, 152, 219), name=name)
        self.addItem(bar_item)
        
        # Set x-axis labels
        self.getAxis('bottom').setTicks([[(i, cat) for i, cat in enumerate(categories)]])
    
    def plot_grouped_bars(self, categories, data_sets, colors=None, names=None):
        """
        Plot grouped bars for multiple data sets.
        
        Args:
            categories (list): List of category names
            data_sets (list): List of value lists for each data set
            colors (list, optional): List of RGB color tuples. Defaults to None.
            names (list, optional): List of names for legend. Defaults to None.
        """
        num_sets = len(data_sets)
        bar_width = 0.8 / num_sets
        
        for i, values in enumerate(data_sets):
            # Calculate x positions for this data set
            x = np.arange(len(categories)) + (i - num_sets/2 + 0.5) * bar_width
            
            # Get color and name
            color = colors[i] if colors and i < len(colors) else (52, 152, 219)
            name = names[i] if names and i < len(names) else f"Data {i+1}"
            
            # Create and add bar item
            bar_item = pg.BarGraphItem(x=x, height=values, width=bar_width, brush=color, name=name)
            self.addItem(bar_item)
        
        # Set x-axis labels
        self.getAxis('bottom').setTicks([[(i, cat) for i, cat in enumerate(categories)]])


class PieChartWidget(QWidget):
    """
    Custom pie chart widget based on Matplotlib.
    """
    
    def __init__(self, title=None, parent=None):
        """
        Initialize the pie chart widget.
        
        Args:
            title (str, optional): Chart title. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
        
        # Create matplotlib figure and canvas
        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        # Create subplot
        self.ax = self.fig.add_subplot(111)
    
    def plot_pie(self, labels, values, colors=None, explode=None):
        """
        Plot a pie chart.
        
        Args:
            labels (list): List of slice labels
            values (list): List of slice values
            colors (list, optional): List of colors. Defaults to None.
            explode (list, optional): List of explosion values. Defaults to None.
        """
        # Clear previous plot
        self.ax.clear()
        
        # Create pie chart
        self.ax.pie(
            values,
            labels=labels,
            colors=colors,
            explode=explode,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        self.ax.axis('equal')
        
        # Redraw canvas
        self.canvas.draw()


class RadarChartWidget(QWidget):
    """
    Custom radar chart widget based on Matplotlib.
    """
    
    def __init__(self, title=None, parent=None):
        """
        Initialize the radar chart widget.
        
        Args:
            title (str, optional): Chart title. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
        
        # Create matplotlib figure and canvas
        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        # Create subplot (polar projection for radar chart)
        self.ax = self.fig.add_subplot(111, polar=True)
    
    def plot_radar(self, labels, values, max_values=None, color=None, fill=True, alpha=0.3):
        """
        Plot a radar chart.
        
        Args:
            labels (list): List of attribute names
            values (list): List of attribute values
            max_values (list, optional): List of maximum values for scaling. Defaults to None.
            color (str, optional): Line and fill color. Defaults to None.
            fill (bool, optional): Whether to fill the radar. Defaults to True.
            alpha (float, optional): Fill transparency. Defaults to 0.3.
        """
        # Clear previous plot
        self.ax.clear()
        
        # Number of variables
        N = len(labels)
        
        # Set default max_values if not provided
        if max_values is None:
            max_values = [100] * N
        
        # Compute angle for each variable
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Normalize values
        normalized_values = [v / m for v, m in zip(values, max_values)]
        normalized_values += normalized_values[:1]  # Close the loop
        
        # Set default color
        color = color or '#3498db'
        
        # Draw the radar
        self.ax.plot(angles, normalized_values, linewidth=2, linestyle='solid', color=color)
        
        if fill:
            self.ax.fill(angles, normalized_values, alpha=alpha, color=color)
        
        # Add labels
        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(labels)
        
        # Set y-ticks
        self.ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        self.ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        
        # Add grid
        self.ax.grid(True)
        
        # Redraw canvas
        self.canvas.draw()
    
    def compare_radar(self, labels, values_list, labels_list, max_values=None, colors=None, alpha=0.3):
        """
        Plot multiple radar charts for comparison.
        
        Args:
            labels (list): List of attribute names
            values_list (list): List of value lists for each radar
            labels_list (list): List of names for each radar
            max_values (list, optional): List of maximum values for scaling. Defaults to None.
            colors (list, optional): List of colors for each radar. Defaults to None.
            alpha (float, optional): Fill transparency. Defaults to 0.3.
        """
        # Clear previous plot
        self.ax.clear()
        
        # Number of variables
        N = len(labels)
        
        # Set default max_values if not provided
        if max_values is None:
            max_values = [100] * N
        
        # Compute angle for each variable
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Default colors
        if colors is None:
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        
        # Plot each radar
        for i, values in enumerate(values_list):
            # Normalize values
            normalized_values = [v / m for v, m in zip(values, max_values)]
            normalized_values += normalized_values[:1]  # Close the loop
            
            # Get color
            color = colors[i % len(colors)]
            
            # Draw the radar
            self.ax.plot(angles, normalized_values, linewidth=2, linestyle='solid', color=color, label=labels_list[i])
            self.ax.fill(angles, normalized_values, alpha=alpha, color=color)
        
        # Add labels
        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(labels)
        
        # Set y-ticks
        self.ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        self.ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        
        # Add grid
        self.ax.grid(True)
        
        # Add legend
        self.ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        # Redraw canvas
        self.canvas.draw()


class ScatterPlotWidget(pg.PlotWidget):
    """
    Custom scatter plot widget based on PyQtGraph.
    """
    
    def __init__(self, title=None, parent=None):
        """
        Initialize the scatter plot widget.
        
        Args:
            title (str, optional): Chart title. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Set background color
        self.setBackground('w')
        
        # Configure axes
        self.getAxis('left').setPen((0, 0, 0))
        self.getAxis('bottom').setPen((0, 0, 0))
        
        # Add title if provided
        if title:
            self.setTitle(title, color=(0, 0, 0), size='14pt')
        
        # Add grid
        self.showGrid(x=True, y=True)
        
        # Add legend
        self.addLegend()
    
    def plot_scatter(self, x_data, y_data, labels=None, color=None, size=10, name=None, symbol='o'):
        """
        Plot a scatter plot.
        
        Args:
            x_data (list): X-axis data
            y_data (list): Y-axis data
            labels (list, optional): Point labels for tooltips. Defaults to None.
            color (tuple, optional): RGB color tuple. Defaults to None.
            size (int, optional): Point size. Defaults to 10.
            name (str, optional): Name for legend. Defaults to None.
            symbol (str, optional): Point symbol. Defaults to 'o'.
        """
        # Create scatter plot item
        scatter = pg.ScatterPlotItem(
            size=size,
            pen=pg.mkPen(None),
            brush=pg.mkBrush(color or (52, 152, 219)),
            symbol=symbol
        )
        
        # Create data points
        spots = []
        for i in range(len(x_data)):
            spot = {
                'pos': (x_data[i], y_data[i]),
                'size': size,
                'brush': pg.mkBrush(color or (52, 152, 219))
            }
            
            if labels and i < len(labels):
                spot['data'] = labels[i]
            
            spots.append(spot)
        
        scatter.addPoints(spots)
        self.addItem(scatter)
        
        # Add legend item if name is provided
        if name:
            self.plot([0], [0], pen=None, symbol=symbol, symbolSize=size, 
                     symbolBrush=pg.mkBrush(color or (52, 152, 219)), name=name)
    
    def add_regression_line(self, x_data, y_data, color=None, width=2, name=None):
        """
        Add a regression line to the scatter plot.
        
        Args:
            x_data (list): X-axis data
            y_data (list): Y-axis data
            color (tuple, optional): RGB color tuple. Defaults to None.
            width (int, optional): Line width. Defaults to 2.
            name (str, optional): Name for legend. Defaults to None.
        """
        # Convert to numpy arrays
        x = np.array(x_data)
        y = np.array(y_data)
        
        # Compute the linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Create line points
        x_line = np.array([min(x), max(x)])
        y_line = slope * x_line + intercept
        
        # Create line
        pen = pg.mkPen(color=color or (255, 0, 0), width=width)
        self.plot(x_line, y_line, pen=pen, name=name)


class HeatMapWidget(pg.PlotWidget):
    """
    Custom heat map widget based on PyQtGraph.
    """
    
    def __init__(self, title=None, parent=None):
        """
        Initialize the heat map widget.
        
        Args:
            title (str, optional): Chart title. Defaults to None.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        
        # Set background color
        self.setBackground('w')
        
        # Configure axes
        self.getAxis('left').setPen((0, 0, 0))
        self.getAxis('bottom').setPen((0, 0, 0))
        
        # Add title if provided
        if title:
            self.setTitle(title, color=(0, 0, 0), size='14pt')
        
        # Disable mouse interaction for ViewBox
        self.getViewBox().setMouseEnabled(x=False, y=False)
        
        # Store the color map
        self.colormap = pg.colormap.get('viridis')
    
    def plot_heatmap(self, data, row_labels=None, col_labels=None, colormap=None, min_value=None, max_value=None):
        """
        Plot a heat map.
        
        Args:
            data (2D array): Heat map data
            row_labels (list, optional): Row labels. Defaults to None.
            col_labels (list, optional): Column labels. Defaults to None.
            colormap (str, optional): Colormap name. Defaults to None.
            min_value (float, optional): Minimum value for color scaling. Defaults to None.
            max_value (float, optional): Maximum value for color scaling. Defaults to None.
        """
        # Clear previous items
        self.clear()
        
        # Convert data to numpy array if it's not already
        data = np.array(data)
        
        # Set colormap
        if colormap:
            self.colormap = pg.colormap.get(colormap)
        
        # Create image item
        heatmap = pg.ImageItem()
        self.addItem(heatmap)
        
        # Set min and max values for scaling
        if min_value is None:
            min_value = np.min(data)
        if max_value is None:
            max_value = np.max(data)
        
        # Set color map on the image
        heatmap.setLookupTable(self.colormap.getLookupTable(min_value, max_value, 256))
        
        # Set data
        heatmap.setImage(data)
        
        # Position the heatmap correctly
        heatmap.scale(1, 1)
        
        # Set axis labels
        if row_labels:
            self.getAxis('left').setTicks([[(i, row_labels[i]) for i in range(len(row_labels))]])
        
        if col_labels:
            self.getAxis('bottom').setTicks([[(i, col_labels[i]) for i in range(len(col_labels))]])
        
        # Add color bar
        bar = pg.ColorBarItem(
            values=(min_value, max_value),
            colorMap=self.colormap,
            orientation='h',
            width=15
        )
        bar.setImageItem(heatmap)
        self.addItem(bar)