"""Tests for the Reddit client module."""

from typing import TYPE_CHECKING
from datetime import datetime

import pytest
from pytest_mock import MockerFixture
import requests  # Import requests for exception testing

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
    # Use a dummy session object for testing to avoid actual network calls
    client = RedditClient(user_agent="TestBot/1.0")
    client.session = requests.Session() # Assign a session object
    return client


@pytest.fixture
def mock_post_data_base() -> dict:
    """Base data for a single mock Reddit post."""
    return {
        "title": "Test Post",
        "url": "https://external.com/test", # Original URL, client should replace this
        "score": 100,
        "created_utc": datetime.now().timestamp(),
        "author": "test_user",
        "promoted": False,
        "subreddit": "test",
        "permalink": "/r/test/comments/123/test_post",
        "thumbnail": "https://example.com/thumb.jpg",
        "selftext": "This is the body of the text post." # Add selftext
    }

@pytest.fixture
def mock_response(mock_post_data_base: dict) -> dict:
    """Create a mock Reddit API response with one post."""
    return {
        "data": {
            "children": [
                {"data": mock_post_data_base.copy()}
            ]
        }
    }

@pytest.fixture
def mock_response_multiple(mock_post_data_base: dict) -> dict:
    """Create a mock Reddit API response with multiple posts."""
    post1 = mock_post_data_base.copy()
    post2 = mock_post_data_base.copy()
    post2["title"] = "Test Post 2"
    post2["score"] = 200
    post2["permalink"] = "/r/test/comments/456/test_post_2"
    post2["selftext"] = "" # Example of a link post with no selftext
    post3 = mock_post_data_base.copy()
    post3["title"] = "Promoted Post"
    post3["promoted"] = True
    post3["permalink"] = "/r/test/comments/789/promoted_post"

    return {
        "data": {
            "children": [
                {"data": post1},
                {"data": post2},
                {"data": post3} # Include a promoted post
            ]
        }
    }


def test_get_top_weekly_posts(
    reddit_client: RedditClient,
    mock_response: dict,
    mocker: MockerFixture,
) -> None:
    """Test fetching top weekly posts from a subreddit."""
    mock_get = mocker.patch.object(reddit_client.session, "get")
    mock_get.return_value.raise_for_status.return_value = None # Mock raise_for_status
    mock_get.return_value.json.return_value = mock_response

    posts = reddit_client.get_top_weekly_posts("test", limit=1)

    # Verify API call parameters (headers are now set on the session, not passed here)
    mock_get.assert_called_once_with(
        "https://www.reddit.com/r/test/top.json",
        params={"t": "week", "limit": 1}
        # Removed headers assertion: headers={"User-Agent": "TestBot/1.0"}
    )

    assert len(posts) == 1
    post = posts[0]
    assert isinstance(post, RedditPost)
    assert post.title == "Test Post"
    # Verify URL is constructed from permalink
    assert post.url == "https://www.reddit.com/r/test/comments/123/test_post"
    assert post.score == 100
    assert post.author == "test_user"
    assert not post.is_promoted
    assert post.subreddit == "test"
    assert post.permalink == "/r/test/comments/123/test_post"
    assert post.thumbnail == "https://example.com/thumb.jpg"
    # Verify selftext is included
    assert post.selftext == "This is the body of the text post."


def test_get_top_monthly_posts(
    reddit_client: RedditClient,
    mock_response: dict,
    mocker: MockerFixture,
) -> None:
    """Test fetching top monthly posts from a subreddit."""
    mock_get = mocker.patch.object(reddit_client.session, "get")
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = mock_response

    posts = reddit_client.get_top_monthly_posts("test", limit=1)

    # Verify API call parameters (headers are now set on the session, not passed here)
    mock_get.assert_called_once_with(
        "https://www.reddit.com/r/test/top.json",
        params={"t": "month", "limit": 1} # Check timeframe 'month'
        # Removed headers assertion: headers={"User-Agent": "TestBot/1.0"}
    )

    assert len(posts) == 1
    assert isinstance(posts[0], RedditPost)
    assert posts[0].title == "Test Post"


def test_get_top_posts_filters_promoted_and_limit(
    reddit_client: RedditClient,
    mock_response_multiple: dict, # Use response with multiple posts
    mocker: MockerFixture,
) -> None:
    """Test that promoted posts are filtered out and limit is respected."""
    mock_get = mocker.patch.object(reddit_client.session, "get")
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = mock_response_multiple

    # Request 2 posts, but mock response has 2 non-promoted and 1 promoted
    posts = reddit_client.get_top_weekly_posts("test", limit=2)

    # Verify API call parameters (limit passed to API, headers set on session)
    mock_get.assert_called_once_with(
        "https://www.reddit.com/r/test/top.json",
        params={"t": "week", "limit": 2}
        # Removed headers assertion: headers={"User-Agent": "TestBot/1.0"}
    )

    # Client should filter the promoted post from the API response
    # Given mock_response_multiple has 2 non-promoted first, this works.
    assert len(posts) == 2 # Should return only the 2 non-promoted posts
    assert all(not post.is_promoted for post in posts)
    assert posts[0].title == "Test Post"
    assert posts[1].title == "Test Post 2"


def test_get_top_posts_request_failure(
    reddit_client: RedditClient,
    mocker: MockerFixture,
) -> None:
    """Test handling of API request failures."""
    # Mock requests.get to raise an exception
    mock_get = mocker.patch.object(reddit_client.session, "get")
    mock_get.side_effect = requests.exceptions.RequestException("API Error")

    # Expect RequestException to be raised by the client method
    with pytest.raises(requests.exceptions.RequestException, match="API Error"):
        reddit_client.get_top_weekly_posts("test", limit=1)

    mock_get.assert_called_once() # Ensure the request was attempted


def test_get_top_posts_http_error(
    reddit_client: RedditClient,
    mocker: MockerFixture,
) -> None:
    """Test handling of HTTP error status codes."""
    mock_get = mocker.patch.object(reddit_client.session, "get")
    # Mock the response object to simulate an HTTP error
    mock_response_obj = mocker.Mock()
    mock_response_obj.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = mock_response_obj

    with pytest.raises(requests.exceptions.HTTPError, match="404 Not Found"):
        reddit_client.get_top_weekly_posts("test", limit=1)

    mock_get.assert_called_once()
    mock_response_obj.raise_for_status.assert_called_once() # Ensure status check happened


def test_get_top_posts_empty_response(
    reddit_client: RedditClient,
    mocker: MockerFixture,
) -> None:
    """Test handling of an empty or malformed API response."""
    mock_get = mocker.patch.object(reddit_client.session, "get")
    mock_get.return_value.raise_for_status.return_value = None
    
    # Simulate empty 'children' list
    mock_get.return_value.json.return_value = {"data": {"children": []}}
    posts_empty_children = reddit_client.get_top_weekly_posts("test", limit=1)
    assert posts_empty_children == [] # Should return an empty list

    # Test malformed response (missing 'data' or 'children')
    # The refactored client now returns [] instead of raising KeyError
    mock_get.return_value.json.return_value = {} # Missing 'data'
    posts_missing_data = reddit_client.get_top_weekly_posts("test", limit=1)
    assert posts_missing_data == [] # Should return empty list

    mock_get.return_value.json.return_value = {"data": {}} # Missing 'children'
    posts_missing_children = reddit_client.get_top_weekly_posts("test", limit=1)
    assert posts_missing_children == [] # Should return empty list

    # Test malformed response (children is not a list)
    mock_get.return_value.json.return_value = {"data": {"children": "not_a_list"}}
    posts_children_not_list = reddit_client.get_top_weekly_posts("test", limit=1)
    assert posts_children_not_list == [] # Should return empty list
    
    # Test malformed response (child item is not a dict)
    mock_get.return_value.json.return_value = {"data": {"children": ["not_a_dict"]}}
    posts_child_not_dict = reddit_client.get_top_weekly_posts("test", limit=1)
    assert posts_child_not_dict == [] # Should return empty list

    # Test malformed response (child['data'] is not a dict)
    mock_get.return_value.json.return_value = {"data": {"children": [{"data": "not_a_dict"}]}}
    posts_child_data_not_dict = reddit_client.get_top_weekly_posts("test", limit=1)
    assert posts_child_data_not_dict == [] # Should return empty list
    
    # Test malformed response (missing essential key like 'permalink')
    mock_post_missing_key = {
        "title": "Test Post Missing Key",
        # "permalink": "/r/test/comments/abc/test_post_missing", # Missing permalink
        "score": 50,
        "created_utc": datetime.now().timestamp(),
        "author": "test_user_missing",
        "promoted": False,
        "subreddit": "test",
        "selftext": "Body"
    }
    mock_get.return_value.json.return_value = {"data": {"children": [{"data": mock_post_missing_key}]}}
    posts_missing_key = reddit_client.get_top_weekly_posts("test", limit=1)
    assert posts_missing_key == [] # Should return empty list because essential key is missing