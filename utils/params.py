import os
import sys
import argparse
from typing import Tuple, Optional, Any

def validate(
    base_url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Validate and get Higress API credentials from arguments or environment variables.
    
    Args:
        base_url: Base URL from command line argument
        username: Username from command line argument
        password: Password from command line argument
        
    Returns:
        Tuple of (base_url, username, password)
        
    Raises:
        SystemExit: If required parameters are missing
    """
    # Get parameters from command line args or environment variables
    base_url = base_url or os.environ.get("HIGRESS_BASE_URL", "http://localhost:8001")
    username = username or os.environ.get("HIGRESS_USERNAME")
    password = password or os.environ.get("HIGRESS_PASSWORD")
    
    # Validate required parameters
    if not username:
        print("Error: Username is required. Provide it with --username or set HIGRESS_USERNAME environment variable.")
        sys.exit(1)
    
    if not password:
        print("Error: Password is required. Provide it with --password or set HIGRESS_PASSWORD environment variable.")
        sys.exit(1)
    
    return base_url, username, password


def parse_args(description: str = "Higress MCP") -> Any:
    """Parse command line arguments.
    
    Args:
        description: Description for the argument parser
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description=description)
    
    # Add arguments for Higress client configuration
    parser.add_argument(
        "--base-url",
        help="Base URL for the Higress API (default: http://localhost:8001 or HIGRESS_BASE_URL env var)"
    )
    parser.add_argument(
        "--username",
        help="Username for Higress API authentication (required if HIGRESS_USERNAME env var not set)"
    )
    parser.add_argument(
        "--password",
        help="Password for Higress API authentication (required if HIGRESS_PASSWORD env var not set)"
    )
    
    return parser.parse_args()
