#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Recommender System Module

This module implements a machine learning-based player recommendation system.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans

from PySide6.QtCore import QObject, Signal, Slot


class PlayerRecommender(QObject):
    """
    Machine learning-based player recommendation system.
    
    This class implements algorithms to recommend similar players
    based on performance metrics.
    """
    
    # Signals
    model_trained = Signal()
    recommendation_ready = Signal(object)
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the player recommender."""
        super().__init__(parent)
        
        # Initialize models
        self.knn_model = None
        self.kmeans_model = None
        self.feature_columns = None
        self.scaler = None
        self.players_df = None
    
    @Slot(object)
    def set_data(self, players_df):
        """
        Set the player data for the recommender.
        
        Args:
            players_df (pd.DataFrame): DataFrame with player data
        """
        self.players_df = players_df
    
    def preprocess_data(self, df=None):
        """
        Preprocess player data for machine learning.
        
        Args:
            df (pd.DataFrame, optional): DataFrame to preprocess. Defaults to self.players_df.
        
        Returns:
            tuple: (X, feature_columns) where X is the preprocessed feature matrix
        """
        if df is None:
            df = self.players_df
        
        if df is None or len(df) == 0:
            self.error_occurred.emit("No data available for preprocessing")
            return None, None
        
        try:
            # Select relevant features for player similarity
            self.feature_columns = [
                'age', 'minutes_played', 'rating',
                'shots_total', 'shots_on_target', 'goals_total', 'assists',
                'passes_total', 'passes_accuracy', 'tackles_total',
                'tackles_blocks', 'tackles_interceptions',
                'duels_total', 'duels_won'
            ]
            
            # Ensure all needed columns exist
            existing_columns = [col for col in self.feature_columns if col in df.columns]
            
            if len(existing_columns) < 5:  # Arbitrary threshold for minimum features
                self.error_occurred.emit("Insufficient features for recommendation")
                return None, None
            
            # Create feature matrix
            X = df[existing_columns].copy()
            
            # Create preprocessing pipeline
            preprocessing = Pipeline([
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', StandardScaler())
            ])
            
            # Fit and transform
            X_processed = preprocessing.fit_transform(X)
            
            # Store the scaler for later use
            self.scaler = preprocessing.named_steps['scaler']
            
            return X_processed, existing_columns
            
        except Exception as e:
            self.error_occurred.emit(f"Error preprocessing data: {str(e)}")
            return None, None
    
    @Slot()
    def train_models(self):
        """Train the recommendation models."""
        try:
            # Preprocess data
            X, features = self.preprocess_data()
            
            if X is None or features is None:
                return
            
            # Train k-NN model
            self.knn_model = NearestNeighbors(
                n_neighbors=min(11, len(X)),  # Limit by dataset size
                algorithm='auto',
                metric='euclidean'
            )
            self.knn_model.fit(X)
            
            # Train k-means model for player clustering
            self.kmeans_model = KMeans(
                n_clusters=min(8, len(X)),  # Limit by dataset size
                random_state=42
            )
            cluster_labels = self.kmeans_model.fit_predict(X)
            
            # Add cluster labels to dataframe
            self.players_df['cluster'] = cluster_labels
            
            # Signal that the model is trained
            self.model_trained.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Error training recommendation models: {str(e)}")
    
    @Slot(int, int)
    def recommend_similar_players(self, player_id, n_recommendations=5):
        """
        Recommend players similar to the given player.
        
        Args:
            player_id (int): ID of the reference player
            n_recommendations (int, optional): Number of recommendations. Defaults to 5.
        """
        try:
            if self.knn_model is None:
                self.train_models()
                
            if self.knn_model is None:
                self.error_occurred.emit("Recommendation model not available")
                return
                
            # Get player data
            player_idx = self.players_df.index[self.players_df['player_id'] == player_id].tolist()
            
            if not player_idx:
                self.error_occurred.emit(f"Player with ID {player_id} not found")
                return
            
            player_idx = player_idx[0]
            
            # Preprocess data again to ensure consistency
            X, _ = self.preprocess_data()
            
            if X is None:
                return
                
            # Find similar players
            distances, indices = self.knn_model.kneighbors(
                X[player_idx].reshape(1, -1),
                n_neighbors=n_recommendations + 1  # +1 because the player itself will be included
            )
            
            # Remove the player itself (first result)
            similar_indices = indices.flatten()[1:]
            similar_distances = distances.flatten()[1:]
            
            # Get similar players data
            similar_players = self.players_df.iloc[similar_indices].copy()
            similar_players['similarity_score'] = 1 / (1 + similar_distances)
            
            # Emit recommendations
            self.recommendation_ready.emit(similar_players)
            
        except Exception as e:
            self.error_occurred.emit(f"Error generating recommendations: {str(e)}")
    
    @Slot(dict, int)
    def recommend_by_criteria(self, criteria, n_recommendations=5):
        """
        Recommend players based on specific criteria.
        
        Args:
            criteria (dict): Dictionary with criteria (e.g., {'position': 'Defender', 'min_rating': 7.5})
            n_recommendations (int, optional): Number of recommendations. Defaults to 5.
        """
        try:
            if self.players_df is None:
                self.error_occurred.emit("No player data available")
                return
            
            # Filter by position if specified
            filtered_df = self.players_df.copy()
            
            if 'position' in criteria and criteria['position']:
                filtered_df = filtered_df[filtered_df['position'] == criteria['position']]
            
            # Apply numeric filters
            for key, value in criteria.items():
                if key.startswith('min_') and value is not None:
                    col_name = key[4:]  # Remove 'min_' prefix
                    if col_name in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[col_name] >= value]
                
                elif key.startswith('max_') and value is not None:
                    col_name = key[4:]  # Remove 'max_' prefix
                    if col_name in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[col_name] <= value]
            
            # Sort by rating if available
            if 'rating' in filtered_df.columns:
                filtered_df = filtered_df.sort_values(by='rating', ascending=False)
            
            # Get top N recommendations
            recommendations = filtered_df.head(n_recommendations)
            
            self.recommendation_ready.emit(recommendations)
            
        except Exception as e:
            self.error_occurred.emit(f"Error generating criteria-based recommendations: {str(e)}")