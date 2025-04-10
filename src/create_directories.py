#!/usr/bin/env python3
"""
Create Directories Script

This script creates the necessary directory structure for the multi-client setup
based on the clients.json and config.yaml files.
"""

import os
import json
import yaml
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_structure(clients_path="clients.json", config_path="config.yaml"):
    """Create the necessary directory structure for multi-client setup.
    
    Args:
        clients_path (str, optional): Path to clients.json file. Defaults to "clients.json".
        config_path (str, optional): Path to config.yaml file. Defaults to "config.yaml".
    
    Returns:
        int: Number of directories created
    """
    created_dirs = 0
    
    try:
        # Load config.yaml
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Create base directories from config.yaml
        if 'results_directory' in config:
            os.makedirs(config['results_directory'], exist_ok=True)
            created_dirs += 1
            logger.info(f"Created results directory: {config['results_directory']}")
        
        if 'structure_analysis_path' in config:
            os.makedirs(os.path.dirname(config['structure_analysis_path']), exist_ok=True)
            created_dirs += 1
            logger.info(f"Created structure analysis directory: {os.path.dirname(config['structure_analysis_path'])}")
        
        if 'structure_analysis_settings' in config and 'samples_directory' in config['structure_analysis_settings']:
            os.makedirs(config['structure_analysis_settings']['samples_directory'], exist_ok=True)
            created_dirs += 1
            logger.info(f"Created samples directory: {config['structure_analysis_settings']['samples_directory']}")
        
        # Create directories for each client
        if os.path.exists(clients_path):
            with open(clients_path, 'r') as file:
                clients_data = json.load(file)
            
            for client_id, client_config in clients_data.items():
                if 'csv_file_path' in client_config:
                    client_dir = os.path.dirname(client_config['csv_file_path'])
                    os.makedirs(client_dir, exist_ok=True)
                    created_dirs += 1
                    logger.info(f"Created directory for client {client_id}: {client_dir}")
                else:
                    # Create default client directory
                    client_dir = f"data/clients/{client_id}"
                    os.makedirs(client_dir, exist_ok=True)
                    created_dirs += 1
                    logger.info(f"Created default directory for client {client_id}: {client_dir}")
        
        # Create screenshots directory
        os.makedirs("screenshots", exist_ok=True)
        created_dirs += 1
        logger.info("Created screenshots directory")
        
        # Create data directory if it doesn't exist yet
        os.makedirs("data", exist_ok=True)
        
        logger.info(f"Directory structure creation completed. Created {created_dirs} directories.")
        return created_dirs
    
    except Exception as e:
        logger.error(f"Error creating directory structure: {e}", exc_info=True)
        return 0

def main():
    """Main function to run the directory structure creation."""
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Create directory structure for multi-client setup")
    parser.add_argument("--clients", default="clients.json", help="Path to clients.json file")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml file")
    
    args = parser.parse_args()
    
    print("Creating directory structure for Restaurant Review Scraper...")
    
    # Create directories
    created_dirs = create_directory_structure(args.clients, args.config)
    
    if created_dirs > 0:
        print(f"Successfully created {created_dirs} directories.")
        print("Directory structure is ready for use.")
    else:
        print("Failed to create directory structure. Check logs for details.")

if __name__ == "__main__":
    main()
