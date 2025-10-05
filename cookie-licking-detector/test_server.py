#!/usr/bin/env python3
"""
Test script to start the Cookie Licking Detector server with mocked database
"""
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock database before importing the main app
with patch('app.db.database.get_async_session'), \
     patch('app.db.database.create_tables'), \
     patch('app.db.database.close_db'), \
     patch('sqlalchemy.ext.asyncio.AsyncSession', new_callable=MagicMock), \
     patch('sqlalchemy.create_engine'), \
     patch('sqlalchemy.pool.QueuePool'), \
     patch('app.core.config.get_settings') as mock_settings:
    
    # Create mock settings
    from app.core.config import Settings
    mock_settings_instance = Settings()
    mock_settings_instance.DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for testing
    mock_settings_instance.ENVIRONMENT = "development"
    mock_settings_instance.DEBUG = True
    mock_settings.return_value = mock_settings_instance
    
    # Import the main app after mocking
    from app.main import app
    import uvicorn

    print("Starting Cookie Licking Detector server with mocked database...")
    print("Server will run on http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_level="info"
    )