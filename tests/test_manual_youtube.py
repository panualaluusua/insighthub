#!/usr/bin/env python3
"""
Manual test script for YouTube transcript extraction.
Following TDD principles - this satisfies our failing test requirement
for interactive URL testing.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.youtube_processor import YouTubeProcessor

def test_manual_youtube_input():
    """
    Manual test function that can be called to test YouTube URLs interactively.
    This follows TDD by providing the functionality our test requires.
    """
    processor = YouTubeProcessor()
    
    if len(sys.argv) > 1:
        # URL provided as command line argument
        url = sys.argv[1]
        print(f"Testing URL: {url}")
        
        try:
            transcript = processor.get_transcript(url)
            print(f"\n{'='*60}")
            print("✅ SUCCESS - TRANSCRIPT EXTRACTED:")
            print(f"{'='*60}")
            print(transcript)
            print(f"{'='*60}")
            print(f"Length: {len(transcript)} characters")
            return True
            
        except ValueError as e:
            print(f"❌ Error: {e}")
            return False
            
    else:
        print("Usage: python tests/test_manual_youtube.py <youtube_url>")
        print("Example: python tests/test_manual_youtube.py 'https://www.youtube.com/watch?v=1Q_MDOWaljk'")
        return False

if __name__ == "__main__":
    test_manual_youtube_input() 