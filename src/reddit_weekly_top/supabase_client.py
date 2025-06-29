"""Supabase client configuration and utilities."""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Client for interacting with Supabase."""
    
    def __init__(self):
        """Initialize the Supabase client."""
        self.client = self._get_client()
    
    def _get_client(self) -> Optional[Client]:
        """Get or create a Supabase client instance."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            return None
            
        return create_client(url, key)
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance."""
        return self.client

# Create a singleton instance
supabase_client = SupabaseClient() 