"""Evaluate endpoint tests."""
import pytest


class TestEvaluate:
    def test_evaluate_returns_rankings(self, client, admin_headers, decision, criteria_and_weights, options):
        resp = client.post(f"/decisions/{decision.id}/evaluate", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "rankings" in data
        assert len(data["rankings"]) == 2
        assert "narrative" in data
        assert "trade_off_matrix" in data

    def test_evaluate_scores_in_range(self, client, admin_headers, decision, criteria_and_weights, options):
        resp = client.post(f"/decisions/{decision.id}/evaluate", headers=admin_headers)
        assert resp.status_code == 200
        for ranking in resp.json()["rankings"]:
            assert 0 <= ranking["total_score"] <= 100
            for score in ranking["scores"]:
                assert 1 <= score["raw_score"] <= 10

    def test_evaluate_good_option_ranks_first(self, client, admin_headers, decision, criteria_and_weights, options):
        """Good Option (option B with positive keywords) should rank #1."""
        resp = client.post(f"/decisions/{decision.id}/evaluate", headers=admin_headers)
        assert resp.status_code == 200
        top = resp.json()["rankings"][0]
        assert top["option_name"] == "Option Alpha"  # Alpha has positive keywords

    def test_evaluate_persists_result(self, client, admin_headers, decision, criteria_and_weights, options):
        client.post(f"/decisions/{decision.id}/evaluate", headers=admin_headers)
        resp = client.get(f"/decisions/{decision.id}/latest-evaluation", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["decision_id"] == decision.id

    def test_evaluate_no_options_returns_400(self, client, admin_headers, workspace):
        from app.models.decision import Decision
        from app.models.criteria import Criterion, DecisionCriterionWeight
        # Create decision with criteria but no options
        resp_d = client.post(
            f"/workspaces/{workspace.id}/decisions",
            json={"title": "Empty Options Decision", "problem_statement": "test"},
            headers=admin_headers
        )
        did = resp_d.json()["id"]
        resp = client.post(f"/decisions/{did}/evaluate", headers=admin_headers)
        assert resp.status_code == 400

    def test_evaluate_no_weights_returns_400(self, client, admin_headers, workspace, options):
        """Decision with options but no weights should return 400."""
        resp_d = client.post(
            f"/workspaces/{workspace.id}/decisions",
            json={"title": "No Weights Decision", "problem_statement": "test"},
            headers=admin_headers
        )
        did = resp_d.json()["id"]
        # Add an option
        client.post(
            f"/decisions/{did}/options",
            json={"label": "A", "name": "Test Option", "description": "simple"},
            headers=admin_headers
        )
        resp = client.post(f"/decisions/{did}/evaluate", headers=admin_headers)
        assert resp.status_code == 400

    def test_workspace_crud(self, client, admin_headers):
        resp = client.post("/workspaces", json={"name": "My WS", "description": "Desc"}, headers=admin_headers)
        assert resp.status_code == 201
        ws_id = resp.json()["id"]

        resp = client.get(f"/workspaces/{ws_id}", headers=admin_headers)
        assert resp.json()["name"] == "My WS"

        resp = client.put(f"/workspaces/{ws_id}", json={"name": "Updated WS"}, headers=admin_headers)
        assert resp.json()["name"] == "Updated WS"

        resp = client.delete(f"/workspaces/{ws_id}", headers=admin_headers)
        assert resp.status_code == 204

    def test_comments_crud(self, client, admin_headers, decision):
        resp = client.post(
            f"/decisions/{decision.id}/comments",
            json={"content": "Great decision!"},
            headers=admin_headers
        )
        assert resp.status_code == 201
        comment_id = resp.json()["id"]

        resp = client.get(f"/decisions/{decision.id}/comments", headers=admin_headers)
        assert len(resp.json()) >= 1

        resp = client.put(f"/comments/{comment_id}", json={"content": "Updated!"}, headers=admin_headers)
        assert resp.json()["content"] == "Updated!"

        resp = client.delete(f"/comments/{comment_id}", headers=admin_headers)
        assert resp.status_code == 204

    def test_prioritize(self, client, admin_headers, decision, criteria_and_weights, options):
        # First evaluate
        client.post(f"/decisions/{decision.id}/evaluate", headers=admin_headers)
        resp = client.post("/prioritize", json={"decision_ids": [decision.id]}, headers=admin_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["decision_id"] == decision.id
