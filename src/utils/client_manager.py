#!/usr/bin/env python3
"""
Client Manager Module

This module provides utilities for managing multiple restaurant clients
and their respective configuration settings.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ClientManager:
    def __init__(self, clients_file: str = "clients.json"):
        """
        Load client information from a JSON file.
        
        Args:
            clients_file (str): Path to the clients JSON file
        """
        try:
            with open(clients_file, 'r', encoding='utf-8') as f:
                self.clients = json.load(f)
            logger.info(f"Loaded {len(self.clients)} clients from {clients_file}")
            self.clients_file = clients_file
        except FileNotFoundError:
            logger.warning(f"Clients file {clients_file} not found. Creating default file.")
            self.clients = []
            self.clients_file = clients_file
            self._create_default_clients_file(clients_file)
        except Exception as e:
            logger.error(f"Error loading clients: {e}")
            self.clients = []
            self.clients_file = clients_file
    
    def _create_default_clients_file(self, filename: str) -> None:
        """
        Create a default clients file with example structure.
        
        Args:
            filename (str): Path to create the default clients file
        """
        default_clients = [
            {
                "name": "Bowens Island Restaurant",
                "google_url": "https://www.google.com/search?q=Bowens+Island+Restaurant+Reviews",
                "yelp_url": "https://www.yelp.com/biz/bowens-island-restaurant-charleston-3",
                "tripadvisor_url": "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html",
                "active": True
            }
        ]
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(default_clients, f, indent=2)
            logger.info(f"Created default clients file at {filename}")
            self.clients = default_clients
        except Exception as e:
            logger.error(f"Error creating default clients file: {e}")
    
    def get_active_clients(self) -> List[Dict[str, Any]]:
        """
        Return a list of active clients.
        
        Returns:
            List[Dict[str, Any]]: List of active client configurations
        """
        return [client for client in self.clients if client.get("active", True)]
    
    def get_client_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a client by name.
        
        Args:
            name (str): Name of the client to find
            
        Returns:
            Optional[Dict[str, Any]]: Client configuration or None if not found
        """
        for client in self.clients:
            if client["name"].lower() == name.lower():
                return client
        return None
    
    def add_client(self, client_data: Dict[str, Any]) -> bool:
        """
        Add a new client.
        
        Args:
            client_data (Dict[str, Any]): Client configuration data
            
        Returns:
            bool: True if client added successfully, False otherwise
        """
        # Validate required fields
        required_fields = ["name", "google_url", "yelp_url", "tripadvisor_url"]
        for field in required_fields:
            if field not in client_data:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Check if client already exists
        existing = self.get_client_by_name(client_data["name"])
        if existing:
            logger.warning(f"Client with name '{client_data['name']}' already exists")
            return False
        
        # Add client and save
        self.clients.append(client_data)
        return self._save_clients()
    
    def update_client(self, name: str, updated_data: Dict[str, Any]) -> bool:
        """
        Update an existing client.
        
        Args:
            name (str): Name of the client to update
            updated_data (Dict[str, Any]): Updated client data
            
        Returns:
            bool: True if client updated successfully, False otherwise
        """
        for i, client in enumerate(self.clients):
            if client["name"].lower() == name.lower():
                # Update client data
                for key, value in updated_data.items():
                    self.clients[i][key] = value
                return self._save_clients()
        
        logger.warning(f"Client with name '{name}' not found")
        return False
    
    def delete_client(self, name: str) -> bool:
        """
        Delete a client.
        
        Args:
            name (str): Name of the client to delete
            
        Returns:
            bool: True if client deleted successfully, False otherwise
        """
        for i, client in enumerate(self.clients):
            if client["name"].lower() == name.lower():
                del self.clients[i]
                return self._save_clients()
        
        logger.warning(f"Client with name '{name}' not found")
        return False
    
    def _save_clients(self) -> bool:
        """
        Save clients back to the file.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(self.clients_file, 'w', encoding='utf-8') as f:
                json.dump(self.clients, f, indent=2)
            logger.info(f"Saved {len(self.clients)} clients to {self.clients_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving clients: {e}")
            return False
