"""Tests for DELETE /activities/{activity_name}/unregister endpoint using AAA pattern."""

import pytest
from tests.conftest import TEST_EMAIL, TEST_EMAIL_2, INVALID_ACTIVITY


class TestUnregisterFromActivity:
    """Tests for unregistering students from activities."""
    
    def test_unregister_existing_student_success(self, client, reset_activities):
        """
        Test that an existing participant can successfully unregister.
        
        AAA Pattern:
        - Arrange: activity with known participant
        - Act: send DELETE request with that participant's email
        - Assert: verify 200 response and success message
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]
        assert activity_name in response.json()["message"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """
        Test that unregistering from non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: prepare invalid activity name and email
        - Act: send DELETE to non-existent activity
        - Assert: verify 404 response and error message
        """
        # ARRANGE
        activity_name = INVALID_ACTIVITY
        email = TEST_EMAIL
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """
        Test that unregistering a non-participant returns 400.
        
        AAA Pattern:
        - Arrange: activity exists but email is not a participant
        - Act: send DELETE with non-existent email
        - Assert: verify 400 response and not registered error
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = TEST_EMAIL  # Not registered for Chess Club
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_only_target_removed(self, client, reset_activities):
        """
        Test that unregistering only removes the target participant.
        
        AAA Pattern:
        - Arrange: capture participant count before unregister
        - Act: unregister one specific participant
        - Assert: verify only target removed, others remain, count decreased by 1
        """
        # ARRANGE
        activity_name = "Chess Club"
        target_email = "michael@mergington.edu"
        other_email = "daniel@mergington.edu"
        
        # Get initial participant count
        initial_data = client.get("/activities").json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": target_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        
        # Verify counts and members
        final_data = client.get("/activities").json()
        final_participants = final_data[activity_name]["participants"]
        final_count = len(final_participants)
        
        assert final_count == initial_count - 1
        assert target_email not in final_participants
        assert other_email in final_participants
    
    def test_signup_after_unregister(self, client, reset_activities):
        """
        Test that a student can re-signup after unregistering.
        
        AAA Pattern:
        - Arrange: participant is registered
        - Act: unregister, then re-signup
        - Assert: verify re-signup succeeds, student is in list
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # ACT - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ACT - Re-signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        
        # Verify student is back in the activity
        final_data = client.get("/activities").json()
        assert email in final_data[activity_name]["participants"]
    
    def test_unregister_reduces_participant_count(self, client, reset_activities):
        """
        Test that unregistering properly updates participant count.
        
        AAA Pattern:
        - Arrange: get initial participants list
        - Act: unregister one participant
        - Assert: verify new count reflects removal
        """
        # ARRANGE
        activity_name = "Programming Class"
        email_to_remove = "emma@mergington.edu"
        
        initial_data = client.get("/activities").json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )
        
        # ASSERT
        assert response.status_code == 200
        
        final_data = client.get("/activities").json()
        final_count = len(final_data[activity_name]["participants"])
        
        assert final_count == initial_count - 1
    
    def test_unregister_response_message_format(self, client, reset_activities):
        """
        Test that unregister response message has correct format.
        
        AAA Pattern:
        - Arrange: prepare activity and email
        - Act: unregister and get response message
        - Assert: verify message includes both email and activity name
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        message = response.json()["message"]
        
        # ASSERT
        assert response.status_code == 200
        assert email in message
        assert activity_name in message
        assert "Unregistered" in message
