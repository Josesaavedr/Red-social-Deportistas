# /services/social/tests/test_main.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from auth import get_current_user_id
from models import PostDB, FollowerDB

# --- Test for Post Endpoints ---

def test_create_post(test_client: TestClient, db_session: Session):
    """
    Test creating a new post successfully.
    """
    # Override the authentication dependency to simulate a logged-in user
    def get_current_user_id_override():
        return 1  # Simulate user with ID 1

    app.dependency_overrides[get_current_user_id] = get_current_user_id_override

    response = test_client.post(
        "/api/v1/posts/",
        json={"content": "This is my first post!"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "This is my first post!"
    assert data["author_id"] == 1

    # Verify the post was saved to the database
    post_in_db = db_session.query(PostDB).filter(PostDB.id == data["id"]).first()
    assert post_in_db is not None
    assert post_in_db.content == "This is my first post!"

    # Clean up the override
    app.dependency_overrides.clear()

def test_create_post_unauthenticated(test_client: TestClient):
    """
    Test that creating a post fails without authentication.
    """
    response = test_client.post(
        "/api/v1/posts/",
        json={"content": "This should fail"}
    )
    assert response.status_code == 401 # Unauthorized

# --- Test for Follower Endpoints ---

def test_follow_user(test_client: TestClient, db_session: Session):
    """
    Test following another user successfully.
    """
    # User 1 wants to follow user 2
    def get_current_user_id_override():
        return 1

    app.dependency_overrides[get_current_user_id] = get_current_user_id_override

    response = test_client.post("/api/v1/users/2/follow")

    assert response.status_code == 204

    # Verify the follow relationship was saved to the database
    follow_in_db = db_session.query(FollowerDB).filter_by(follower_id=1, followed_id=2).first()
    assert follow_in_db is not None

    # Test that following the same user again results in a conflict
    response_again = test_client.post("/api/v1/users/2/follow")
    assert response_again.status_code == 409 # Conflict

    # Clean up the override
    app.dependency_overrides.clear()