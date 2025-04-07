#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Football Scout Pro - Main Application Entry Point

This module initializes and runs the Football Scout Pro desktop application.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

# Import application controllers
from controllers.main_controller import MainController


def configure_application():
    """Configure global application settings."""
    # Set application metadata
    QCoreApplication.setOrganizationName("FootballScoutPro")
    QCoreApplication.setApplicationName("Football Scout Pro")
    
    # Enable High DPI scaling - using proper attributes to avoid deprecation warnings
    if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):  
        # For newer versions of PySide6
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    else:
        # Fallback for older versions
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)


def main():
    """Initialize and run the application."""
    # Create the application
    app = QApplication(sys.argv)
    configure_application()
    
    # Create and show the main controller
    main_controller = MainController()
    main_controller.show()
    
    # Run the application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())