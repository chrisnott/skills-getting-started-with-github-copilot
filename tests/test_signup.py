"""Tests for POST /activities/{activity_name}/signup endpoint using AAA pattern."""

import pytest
from tests.conftest import TEST_EMAIL, TEST_EMAIL_2, TEST_EMAIL_3, INVALID_ACTIVITY


class TestSignupForActivity:
    """Tests for signing up students for activities."""
    
    def test_signup_new_student_success(self, client, reset_activities):
        """
        Test that a new student can successfully sign up for an activity.
        
        AAA Pattern:
        - Arrange: prepare activity name and new email
        - Act: send POST request to signup endpoint
        - Assert: verify 200 response and student added to participants
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = TEST_EMAIL
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """
        Test that signup to non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: prepare invalid activity name and email
        - Act: send POST to non-existent activity
        - Assert: verify 404 response and error message
        """
        # ARRANGE
        activity_name = INVALID_ACTIVITY
        email = TEST_EMAIL
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_student_already_registered(self, client, reset_activities):
        """
        Test that signing up twice for the same activity returns 400.
        
        AAA Pattern:
        - Arrange: activity has existing participants
        - Act: attempt to signup with an already-registered email
        - Assert: verify 400 response and duplicate error message
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """
        Test that multiple different students can sign up for the same activity.
        
        AAA Pattern:
        - Arrange: prepare list of emails and activity name
        - Act: signup each email sequentially
        - Assert: verify all signups successful, all added to participants
        """
        # ARRANGE
        activity_name = "Programming Class"
        emails = [TEST_EMAIL, TEST_EMAIL_2, TEST_EMAIL_3]
        
        # ACT
        responses = []
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            responses.append(response)
        
        # ASSERT
        for response in responses:
            assert response.status_code == 200
        
        # Verify all emails were added
        final_activities = client.get("/activities").json()
        final_participants = final_activities[activity_name]["participants"]
        for email in emails:
            assert email in final_participants
    
    def test_signup_same_student_different_activities(self, client, reset_activities):
        """
        Test that the same student can sign up for multiple different activities.
        
        AAA Pattern:
        - Arrange: prepare one email and multiple activity names
        - Act: signup to each activity sequentially
        - Assert: verify all signups succeed, student appears in each activity
        """
        # ARRANGE
        email = TEST_EMAIL
        activities = ["Chess Club", "Programming Class", "Art Club"]
        
        # ACT
        responses = []
        for activity_name in activities:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            responses.append(response)
        
        # ASSERT
        for response in responses:
            assert response.status_code == 200
        
        # Verify student is in all activities
        final_data = client.get("/activities").json()
        for activity_name in activities:
            assert email in final_data[activity_name]["participants"]
    
    def test_signup_response_message_format(self, client, reset_activities):
        """
        Test that signup response message has correct format.
        
        AAA Pattern:
        - Arrange: prepare activity and email
        - Act: signup and get response message
        - Assert: verify message includes both email and activity name
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = TEST_EMAIL
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        message = response.json()["message"]
        
        # ASSERT
        assert response.status_code == 200
        assert email in message
        assert activity_name in message
        assert "Signed up" in message
