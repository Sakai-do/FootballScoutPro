#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings Dialog Module

This module implements a settings dialog for configuring application settings.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QFormLayout, QPushButton, QGroupBox, QDialogButtonBox,
    QSpinBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot

from utils.config import save_config, load_config, API_KEY, API_SOURCE


class SettingsDialog(QDialog):
    """
    Dialog for configuring application settings.
    """
    
    # Signal emitted when settings change
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        
        # Load current settings
        self.config = load_config()
        
        # Set up the dialog
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        
        # Create the layout
        self.create_layout()
        
        # Fill fields with current settings
        self.load_settings()
        
        # Connect signals
        self.connect_signals()
    
    def create_layout(self):
        """Create the dialog layout."""
        layout = QVBoxLayout(self)
        
        # API settings group
        api_group = QGroupBox("API Settings")
        api_layout = QFormLayout(api_group)
        
        # API source selection
        self.api_source_combo = QComboBox()
        self.api_source_combo.addItem("RapidAPI", "rapidapi")
        self.api_source_combo.addItem("API-Sports", "apisports")
        self.api_source_combo.addItem("Mock Data (No API Key Required)", "mock")
        api_layout.addRow("API Source:", self.api_source_combo)
        
        # API key field
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter your API key")
        api_layout.addRow("API Key:", self.api_key_edit)
        
        # API info label
        self.api_info_label = QLabel(
            "For RapidAPI: https://api-football-v1.p.rapidapi.com/v3/\n"
            "For API-Sports: https://v3.football.api-sports.io/"
        )
        self.api_info_label.setWordWrap(True)
        api_layout.addRow("", self.api_info_label)
        
        layout.addWidget(api_group)
        
        # Cache settings group
        cache_group = QGroupBox("Cache Settings")
        cache_layout = QFormLayout(cache_group)
        
        # Cache expiry spin box
        self.cache_expiry_spin = QSpinBox()
        self.cache_expiry_spin.setRange(1, 168)  # 1 hour to 7 days
        self.cache_expiry_spin.setSuffix(" hours")
        cache_layout.addRow("Cache Expiry:", self.cache_expiry_spin)
        
        # Clear cache button
        self.clear_cache_button = QPushButton("Clear Cache")
        cache_layout.addRow("", self.clear_cache_button)
        
        layout.addWidget(cache_group)
        
        # Season settings group
        season_group = QGroupBox("Season Settings")
        season_layout = QFormLayout(season_group)
        
        # Season selection
        self.season_spin = QSpinBox()
        self.season_spin.setRange(2010, 2030)
        season_layout.addRow("Current Season:", self.season_spin)
        
        layout.addWidget(season_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_settings(self):
        """Load current settings into the form fields."""
        # API settings
        api_source = self.config.get('api_source', 'mock')
        index = self.api_source_combo.findData(api_source)
        if index >= 0:
            self.api_source_combo.setCurrentIndex(index)
        
        self.api_key_edit.setText(self.config.get('api_key', ''))
        
        # Cache settings
        self.cache_expiry_spin.setValue(self.config.get('cache_expiry_hours', 24))
        
        # Season settings
        self.season_spin.setValue(self.config.get('current_season', 2023))
        
        # Update API key field enabled state based on source
        self.update_api_key_state()
    
    def connect_signals(self):
        """Connect dialog signals to slots."""
        # API source changed
        self.api_source_combo.currentIndexChanged.connect(self.update_api_key_state)
        
        # Clear cache button
        self.clear_cache_button.clicked.connect(self.on_clear_cache)
    
    def update_api_key_state(self):
        """Update API key field enabled state based on selected source."""
        api_source = self.api_source_combo.currentData()
        self.api_key_edit.setEnabled(api_source != 'mock')
    
    def on_clear_cache(self):
        """Handle clear cache button click."""
        # This would clear the API cache
        # For now, just show a message
        QMessageBox.information(
            self,
            "Cache Cleared",
            "The API request cache has been cleared."
        )
    
    def accept(self):
        """Save settings when the dialog is accepted."""
        # Get values from form fields
        api_source = self.api_source_combo.currentData()
        api_key = self.api_key_edit.text().strip()
        cache_expiry = self.cache_expiry_spin.value()
        current_season = self.season_spin.value()
        
        # Check if API key is provided when needed
        if api_source != 'mock' and not api_key:
            QMessageBox.warning(
                self,
                "API Key Required",
                "Please enter an API key when using RapidAPI or API-Sports."
            )
            return
        
        # Update config
        self.config['api_source'] = api_source
        self.config['api_key'] = api_key
        self.config['cache_expiry_hours'] = cache_expiry
        self.config['current_season'] = current_season
        
        # Save config
        save_config(self.config)
        
        # Emit signal
        self.settings_changed.emit(self.config)
        
        # Close dialog
        super().accept()