import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List
from src.reddit_processor import RedditProcessor, RedditPost, RedditComment
import os


class TestRedditProcessor:
    """Test suite for RedditProcessor following TDD principles."""

    def test_reddit_processor_requires_credentials(self) -> None:
        """Test that RedditProcessor raises ValueError when credentials are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Reddit API credentials not found"):
                RedditProcessor()

    def test_reddit_processor_initializes_with_credentials(self) -> None:
        """Test that RedditProcessor initializes successfully with proper credentials."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            with patch('src.reddit_processor.praw.Reddit') as mock_reddit:
                processor = RedditProcessor()
                assert processor is not None
                mock_reddit.assert_called_once()

    @patch('src.reddit_processor.praw.Reddit')
    def test_validate_subreddit_returns_true_for_valid_subreddit(self, mock_reddit: Mock) -> None:
        """Test that validate_subreddit returns True for accessible subreddits."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            # Setup mock
            mock_subreddit = Mock()
            mock_subreddit.display_name = "python"
            mock_reddit.return_value.subreddit.return_value = mock_subreddit
            
            processor = RedditProcessor()
            result = processor.validate_subreddit("python")
            
            assert result is True
            mock_reddit.return_value.subreddit.assert_called_with("python")

    @patch('src.reddit_processor.praw.Reddit')
    def test_validate_subreddit_returns_false_for_invalid_subreddit(self, mock_reddit: Mock) -> None:
        """Test that validate_subreddit returns False for inaccessible subreddits."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            # Setup mock to raise exception
            mock_reddit.return_value.subreddit.side_effect = Exception("Subreddit not found")
            
            processor = RedditProcessor()
            result = processor.validate_subreddit("nonexistent")
            
            assert result is False

    @patch('src.reddit_processor.praw.Reddit')
    def test_fetch_posts_returns_list_of_reddit_posts(self, mock_reddit: Mock) -> None:
        """Test that fetch_posts returns a list of RedditPost objects."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            # Setup mock submission
            mock_submission = Mock()
            mock_submission.id = "test123"
            mock_submission.title = "Test Post"
            mock_submission.selftext = "Test content"
            mock_submission.url = "https://example.com"
            mock_submission.score = 100
            mock_submission.num_comments = 5
            mock_submission.created_utc = 1640995200.0
            mock_submission.subreddit.display_name = "python"
            mock_submission.author = "testuser"
            mock_submission.permalink = "/r/python/comments/test123"
            mock_submission.is_self = True
            mock_submission.link_flair_text = "Discussion"
            
            # Setup mock subreddit
            mock_subreddit = Mock()
            mock_subreddit.display_name = "python"
            mock_subreddit.hot.return_value = [mock_submission]
            
            mock_reddit.return_value.subreddit.return_value = mock_subreddit
            
            processor = RedditProcessor()
            # Mock validate_subreddit to return True
            processor.validate_subreddit = Mock(return_value=True)
            
            posts = processor.fetch_posts("python", limit=1)
            
            assert len(posts) == 1
            assert isinstance(posts[0], RedditPost)
            assert posts[0].id == "test123"
            assert posts[0].title == "Test Post"
            assert posts[0].subreddit == "python"

    @patch('src.reddit_processor.praw.Reddit')
    def test_fetch_posts_raises_error_for_invalid_subreddit(self, mock_reddit: Mock) -> None:
        """Test that fetch_posts raises ValueError for invalid subreddits."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            processor = RedditProcessor()
            # Mock validate_subreddit to return False
            processor.validate_subreddit = Mock(return_value=False)
            
            with pytest.raises(ValueError, match="Subreddit 'invalid' is invalid or inaccessible"):
                processor.fetch_posts("invalid")

    @patch('src.reddit_processor.praw.Reddit')
    def test_fetch_comments_returns_list_of_reddit_comments(self, mock_reddit: Mock) -> None:
        """Test that fetch_comments returns a list of RedditComment objects."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            # Setup mock comment
            mock_comment = Mock()
            mock_comment.id = "comment123"
            mock_comment.body = "Great post!"
            mock_comment.score = 10
            mock_comment.created_utc = 1640995200.0
            mock_comment.author = "commenter"
            mock_comment.is_submitter = False
            
            # Setup mock submission
            mock_submission = Mock()
            mock_comments_list = Mock()
            mock_comments_list.__iter__ = Mock(return_value=iter([mock_comment]))
            mock_comments_list.__getitem__ = Mock(return_value=[mock_comment])
            mock_comments_list.replace_more = Mock()
            mock_submission.comments = mock_comments_list
            
            mock_reddit.return_value.submission.return_value = mock_submission
            
            processor = RedditProcessor()
            comments = processor.fetch_comments("test123", limit=1)
            
            assert len(comments) == 1
            assert isinstance(comments[0], RedditComment)
            assert comments[0].id == "comment123"
            assert comments[0].body == "Great post!"

    def test_process_post_content_formats_post_correctly(self) -> None:
        """Test that process_post_content returns properly formatted text."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            # Create a test post using the Pydantic model
            post = RedditPost(
                id="test123",
                title="Test Post Title",
                selftext="This is the post content",
                url="https://reddit.com/r/python/comments/test123",
                score=100,
                num_comments=5,
                created_utc=1640995200.0,
                subreddit="python",
                author="testuser",
                permalink="/r/python/comments/test123",
                is_self=True,
                link_flair_text="Discussion"
            )
            
            with patch('src.reddit_processor.praw.Reddit'):
                processor = RedditProcessor()
                # Mock fetch_comments to return empty list for simplicity
                processor.fetch_comments = Mock(return_value=[])
                
                content = processor.process_post_content(post, include_comments=False)
                
                assert "Title: Test Post Title" in content
                assert "Content: This is the post content" in content
                assert "Score: 100" in content
                assert "Comments: 5" in content
                assert "Subreddit: r/python" in content
                assert "Flair: Discussion" in content

    def test_get_content_summary_returns_structured_data(self) -> None:
        """Test that get_content_summary returns properly structured summary data."""
        with patch.dict(os.environ, {
            'REDDIT_CLIENT_ID': 'test_id',
            'REDDIT_SECRET': 'test_secret'
        }):
            # Create test post
            test_post = RedditPost(
                id="test123",
                title="Test Post",
                selftext="Test content",
                url="https://reddit.com/r/python/comments/test123",
                score=100,
                num_comments=5,
                created_utc=1640995200.0,
                subreddit="python",
                author="testuser",
                permalink="/r/python/comments/test123",
                is_self=True
            )
            
            with patch('src.reddit_processor.praw.Reddit'):
                processor = RedditProcessor()
                # Mock methods
                processor.fetch_posts = Mock(return_value=[test_post])
                processor.process_post_content = Mock(return_value="Processed content")
                
                summary = processor.get_content_summary("python", limit=1)
                
                assert summary["subreddit"] == "python"
                assert summary["total_posts"] == 1
                assert len(summary["processed_content"]) == 1
                assert "timestamp" in summary
                
                content_item = summary["processed_content"][0]
                assert content_item["post_id"] == "test123"
                assert content_item["title"] == "Test Post"
                assert content_item["content"] == "Processed content"
                assert content_item["score"] == 100
                assert content_item["url"] == "https://reddit.com/r/python/comments/test123"


class TestRedditPostModel:
    """Test suite for RedditPost Pydantic model."""
    
    def test_reddit_post_model_validation(self) -> None:
        """Test that RedditPost model validates data correctly."""
        post_data = {
            "id": "test123",
            "title": "Test Title",
            "selftext": "Test content",
            "url": "https://example.com",
            "score": 100,
            "num_comments": 5,
            "created_utc": 1640995200.0,
            "subreddit": "python",
            "author": "testuser",
            "permalink": "/r/python/comments/test123",
            "is_self": True,
            "link_flair_text": "Discussion"
        }
        
        post = RedditPost(**post_data)
        assert post.id == "test123"
        assert post.title == "Test Title"
        assert post.link_flair_text == "Discussion"

    def test_reddit_post_model_optional_fields(self) -> None:
        """Test that RedditPost model handles optional fields correctly."""
        post_data = {
            "id": "test123",
            "title": "Test Title",
            "selftext": "",
            "url": "https://example.com",
            "score": 100,
            "num_comments": 5,
            "created_utc": 1640995200.0,
            "subreddit": "python",
            "author": "testuser",
            "permalink": "/r/python/comments/test123",
            "is_self": False
            # link_flair_text is optional
        }
        
        post = RedditPost(**post_data)
        assert post.link_flair_text is None


class TestRedditCommentModel:
    """Test suite for RedditComment Pydantic model."""
    
    def test_reddit_comment_model_validation(self) -> None:
        """Test that RedditComment model validates data correctly."""
        comment_data = {
            "id": "comment123",
            "body": "Great post!",
            "score": 10,
            "created_utc": 1640995200.0,
            "author": "commenter",
            "is_submitter": False
        }
        
        comment = RedditComment(**comment_data)
        assert comment.id == "comment123"
        assert comment.body == "Great post!"
        assert comment.is_submitter is False 