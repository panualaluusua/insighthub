"""Tests for the Reddit client module."""

from typing import TYPE_CHECKING
from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from reddit_weekly_top.models import RedditPost
from reddit_weekly_top.reddit_client import RedditClient

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.fixtures import FixtureRequest
    from _pytest.logging import LogCaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def reddit_client() -> RedditClient:
    """Create a Reddit client instance for testing.
    
    Returns:
        A RedditClient instance with a test user agent.
    """
    return RedditClient(user_agent="TestBot/1.0")


@pytest.fixture
def mock_response() -> dict:
    """Create a mock Reddit API response.
    
    Returns:
        A dictionary containing mock Reddit API response data.
    """
    return {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "Test Post",
                        "url": "https://reddit.com/test",
                        "score": 100,
                        "created_utc": datetime.now().timestamp(),
                        "author": "test_user",
                        "promoted": False,
                        "subreddit": "test",
                        "permalink": "/r/test/comments/123/test_post",
                        "thumbnail": "https://example.com/thumb.jpg"
                    }
                }
            ]
        }
    }


def test_get_top_weekly_posts(
    reddit_client: RedditClient,
    mock_response: dict,
    mocker: MockerFixture,
) -> None:
    """Test fetching top weekly posts from a subreddit.
    
    Args:
        reddit_client: The Reddit client fixture.
        mock_response: The mock response fixture.
        mocker: The pytest-mock fixture.
    """
    # Mock the requests session
    mock_get = mocker.patch.object(reddit_client.session, "get")
    mock_get.return_value.json.return_value = mock_response
    
    # Test fetching posts
    posts = reddit_client.get_top_weekly_posts("test", limit=1)
    
    assert len(posts) == 1
    assert isinstance(posts[0], RedditPost)
    assert posts[0].title == "Test Post"
    assert posts[0].url == "https://reddit.com/test"
    assert posts[0].score == 100
    assert posts[0].author == "test_user"
    assert not posts[0].is_promoted


def test_get_top_weekly_posts_filters_promoted(
    reddit_client: RedditClient,
    mock_response: dict,
    mocker: MockerFixture,
) -> None:
    """Test that promoted posts are filtered out.
    
    Args:
        reddit_client: The Reddit client fixture.
        mock_response: The mock response fixture.
        mocker: The pytest-mock fixture.
    """
    # Modify mock response to include a promoted post
    mock_response["data"]["children"].append({
        "data": {
            "title": "Promoted Post",
            "url": "https://reddit.com/promoted",
            "score": 1000,
            "created_utc": datetime.now().timestamp(),
            "author": "advertiser",
            "promoted": True,
            "subreddit": "test",
            "permalink": "/r/test/comments/456/promoted_post",
            "thumbnail": None
        }
    })
    
    # Mock the requests session
    mock_get = mocker.patch.object(reddit_client.session, "get")
    mock_get.return_value.json.return_value = mock_response
    
    # Test fetching posts
    posts = reddit_client.get_top_weekly_posts("test", limit=2)
    
    assert len(posts) == 1  # Only non-promoted post should be returned
    assert all(not post.is_promoted for post in posts) 