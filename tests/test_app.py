"""Test suite for Mergington High School Activities API endpoints"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball",
            "Soccer",
            "Art Club",
            "Music Ensemble",
            "Debate Club",
            "Science Club",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has the required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newemail@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_duplicate_prevents_reregistration(self, client):
        """Test that duplicate signup attempts are prevented"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for non-existent activity returns 404"""
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup adds participant to activity's participant list"""
        # Arrange
        activity_name = "Art Club"
        email = "test_participant@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities = client.get("/activities").json()

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        activities = client.get("/activities").json()

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_registered_fails(self, client):
        """Test that unregistering a non-registered student fails"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister for non-existent activity returns 404"""
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestIntegration:
    """Integration tests combining multiple operations"""

    def test_full_signup_and_unregister_flow(self, client):
        """Test complete flow: signup, verify, unregister, verify"""
        # Arrange
        activity_name = "Music Ensemble"
        email = "integration_test@mergington.edu"

        # Act & Assert - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Act & Assert - Verify signup
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

        # Act & Assert - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200

        # Act & Assert - Verify unregistration
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
