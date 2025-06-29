"""StorageNode for persisting processed content to Supabase database.

This module provides the StorageNode class for the LangGraph orchestrator,
handling database persistence operations for processed content.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from langsmith import traceable

from src.reddit_weekly_top.supabase_client import supabase_client
from src.orchestrator.state import ContentState


class StorageNode:
    """Node for persisting processed content to Supabase database.
    
    This node handles storage operations for content that has been processed
    through the orchestration pipeline, including summaries and embeddings.
    """
    
    def __init__(self):
        """Initialize the StorageNode with Supabase client.
        
        Uses lazy loading pattern to avoid connection during testing.
        
        Raises:
            ValueError: If Supabase client is not available.
        """
        self.client = supabase_client.get_client()
        if not self.client:
            raise ValueError("Supabase client not available. Check SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")
        
        self.table_name = "content"
    
    @traceable(name="content_storage")
    def store_content(self, state: ContentState) -> Dict[str, Any]:
        """Store processed content to the database.
        
        Args:
            state: ContentState containing all processed content data.
            
        Returns:
            Dict containing storage result with status and metadata.
            
        Raises:
            Exception: If storage operation fails.
            KeyError: If required fields are missing from state.
        """
        try:
            # Prepare content for database storage
            content_data = self._prepare_content_for_storage(state)
            
            # Insert into database
            response = self.client.table(self.table_name).insert(content_data).execute()
            
            if response.error:
                raise Exception(f"Failed to store content: {response.error}")
            
            # Return success response
            return {
                "status": "completed",
                "content_id": state["content_id"],
                "stored_at": datetime.now(timezone.utc).isoformat(),
                "database_id": response.data[0].get("id") if response.data else None
            }
            
        except KeyError as e:
            # Re-raise KeyError for missing required fields
            raise
        except Exception as e:
            if "Failed to store content" in str(e):
                raise
            raise Exception(f"Storage operation failed: {str(e)}")
    
    def update_status(self, content_id: str, status: str) -> Dict[str, Any]:
        """Update the status of stored content.
        
        Args:
            content_id: Unique identifier for the content.
            status: New status to set.
            
        Returns:
            Dict containing update result.
        """
        response = self.client.table(self.table_name).update({
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("content_id", content_id).execute()
        
        if response.error:
            raise Exception(f"Failed to update status: {response.error}")
        
        return {
            "content_id": content_id,
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve content from the database by content_id.
        
        Args:
            content_id: Unique identifier for the content.
            
        Returns:
            Dict containing content data, or None if not found.
        """
        response = self.client.table(self.table_name).select("*").eq("content_id", content_id).single().execute()
        
        if response.error:
            # Handle "No rows found" error gracefully
            if "No rows found" in str(response.error.get("message", "")):
                return None
            raise Exception(f"Failed to retrieve content: {response.error}")
        
        return response.data
    
    def get_content_by_source_url(self, source_url: str) -> List[Dict[str, Any]]:
        """Retrieve content by source URL.
        
        Args:
            source_url: The original source URL.
            
        Returns:
            List of content items matching the source URL.
        """
        response = self.client.table(self.table_name).select("*").eq("source_url", source_url).execute()
        
        if response.error:
            raise Exception(f"Failed to retrieve content by URL: {response.error}")
        
        return response.data or []
    
    @traceable(name="batch_content_storage")
    def batch_store(self, content_states: List[ContentState]) -> List[Dict[str, Any]]:
        """Store multiple content items in a batch operation.
        
        Args:
            content_states: List of ContentState objects to store.
            
        Returns:
            List of storage results for each content item.
        """
        # Prepare all content for storage
        content_data_list = [self._prepare_content_for_storage(state) for state in content_states]
        
        # Batch insert
        response = self.client.table(self.table_name).insert(content_data_list).execute()
        
        if response.error:
            raise Exception(f"Failed to batch store content: {response.error}")
        
        # Return results for each item
        results = []
        for i, state in enumerate(content_states):
            results.append({
                "status": "completed",
                "content_id": state["content_id"],
                "stored_at": datetime.now(timezone.utc).isoformat(),
                "database_id": response.data[i].get("id") if response.data and i < len(response.data) else None
            })
        
        return results
    
    def _prepare_content_for_storage(self, state: ContentState) -> Dict[str, Any]:
        """Prepare ContentState for database storage.
        
        Args:
            state: ContentState to prepare.
            
        Returns:
            Dict ready for database insertion.
        """
        # Convert metadata dict to JSON string
        metadata_json = json.dumps(state.get("metadata", {}))
        
        return {
            "source_type": state["source_type"],
            "source_url": state["source_url"], 
            "content_id": state["content_id"],
            "raw_content": state.get("raw_content"),
            "processed_content": state.get("processed_content"),
            "summary": state.get("summary"),
            "embeddings": state.get("embeddings"),
            "status": state.get("status", "completed"),
            "error_message": state.get("error_message"),
            "metadata": metadata_json,
            "created_at": state.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": state.get("completed_at") or datetime.now(timezone.utc).isoformat(),
            "retry_count": state.get("retry_count", 0),
            "current_node": state.get("current_node", "storage")
        } 