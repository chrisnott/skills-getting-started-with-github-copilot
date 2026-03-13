"""Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Tests for retrieving all activities."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns all activities with correct structure.
        
        AAA Pattern:
        - Arrange: client and expected activity count are ready
        - Act: make GET request to /activities
        - Assert: verify all activities returned with correct structure
        """
        # ARRANGE
        expected_activity_count = 9
        
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        assert all(isinstance(activity_name, str) for activity_name in data.keys())
    
    def test_get_activities_includes_required_fields(self, client, reset_activities):
        """
        Test that each activity contains all required fields.
        
        AAA Pattern:
        - Arrange: define required fields
        - Act: fetch activities and check structure
        - Assert: verify each activity has all required fields
        """
        # ARRANGE
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        
        # ASSERT
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert all(field in activity_data for field in required_fields), \
                f"Activity {activity_name} missing required fields"
            assert isinstance(activity_data["participants"], list), \
                f"Participants for {activity_name} must be a list"
    
    def test_get_activities_specific_activity_data(self, client, reset_activities):
        """
        Test that a specific activity has correct data.
        
        AAA Pattern:
        - Arrange: define expected data for Chess Club
        - Act: retrieve activities and find Chess Club
        - Assert: verify Chess Club data matches expectations
        """
        # ARRANGE
        expected_activity = "Chess Club"
        expected_description = "Learn strategies and compete in chess tournaments"
        expected_max = 12
        expected_participants_count = 2
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities[expected_activity]
        
        # ASSERT
        assert response.status_code == 200
        assert expected_activity in activities
        assert chess_club["description"] == expected_description
        assert chess_club["max_participants"] == expected_max
        assert len(chess_club["participants"]) == expected_participants_count
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
