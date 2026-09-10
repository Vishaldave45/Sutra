from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app


@pytest.mark.asyncio
async def test_create_and_retrieve_standalone_task() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create standalone task
        create_res = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Buy milk",
                "description": "2% organic milk",
                "priority": "HIGH",
                "metadata": {"source": "manual"},
            },
        )
        assert create_res.status_code == 201
        data = create_res.json()
        task_id = data["id"]
        assert task_id is not None
        assert data["project_id"] is None
        assert data["title"] == "Buy milk"
        assert data["description"] == "2% organic milk"
        assert data["status"] == "TODO"
        assert data["priority"] == "HIGH"
        assert data["due_at"] is None
        assert data["completed_at"] is None
        assert data["metadata"] == {"source": "manual"}
        assert "created_at" in data
        assert "updated_at" in data

        # Retrieve
        get_res = await client.get(f"/api/v1/tasks/{task_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["id"] == task_id
        assert get_data["title"] == "Buy milk"


@pytest.mark.asyncio
async def test_create_task_under_project() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create project
        proj_res = await client.post(
            "/api/v1/projects",
            json={"name": "Health Project"},
        )
        assert proj_res.status_code == 201
        project_id = proj_res.json()["id"]

        # Create task linked to project
        task_res = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Gym workout",
                "project_id": project_id,
                "priority": "URGENT",
            },
        )
        assert task_res.status_code == 201
        task_data = task_res.json()
        assert task_data["project_id"] == project_id
        assert task_data["priority"] == "URGENT"


@pytest.mark.asyncio
async def test_create_task_with_nonexistent_project_fails() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Orphan task",
                "project_id": str(uuid4()),
            },
        )
        assert res.status_code == 404
        assert "Referenced project" in res.json()["error"]


@pytest.mark.asyncio
async def test_task_state_transitions_and_invariants() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create task (TODO)
        create_res = await client.post(
            "/api/v1/tasks",
            json={"title": "Lifecycle Task"},
        )
        task_id = create_res.json()["id"]
        assert create_res.json()["status"] == "TODO"
        assert create_res.json()["completed_at"] is None

        # 2. Start task (TODO -> IN_PROGRESS)
        start_res = await client.post(f"/api/v1/tasks/{task_id}/start")
        assert start_res.status_code == 200
        assert start_res.json()["status"] == "IN_PROGRESS"
        assert start_res.json()["completed_at"] is None

        # Idempotent start
        start_res2 = await client.post(f"/api/v1/tasks/{task_id}/start")
        assert start_res2.status_code == 200
        assert start_res2.json()["status"] == "IN_PROGRESS"

        # 3. Complete task (IN_PROGRESS -> DONE)
        comp_res = await client.post(f"/api/v1/tasks/{task_id}/complete")
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["status"] == "DONE"
        assert comp_data["completed_at"] is not None
        completion_time = comp_data["completed_at"]

        # Idempotent complete
        comp_res2 = await client.post(f"/api/v1/tasks/{task_id}/complete")
        assert comp_res2.status_code == 200
        assert comp_res2.json()["status"] == "DONE"
        assert comp_res2.json()["completed_at"] == completion_time

        # Terminal state protection: DONE cannot be started or cancelled
        fail_start = await client.post(f"/api/v1/tasks/{task_id}/start")
        assert fail_start.status_code == 409
        assert (
            "Cannot start task in terminal state 'DONE'" in fail_start.json()["error"]
        )

        fail_cancel = await client.post(f"/api/v1/tasks/{task_id}/cancel")
        assert fail_cancel.status_code == 409
        assert (
            "Cannot cancel task in terminal state 'DONE'" in fail_cancel.json()["error"]
        )


@pytest.mark.asyncio
async def test_task_direct_completion_and_cancellation() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # TODO -> DONE direct transition
        t1 = await client.post("/api/v1/tasks", json={"title": "Direct complete"})
        t1_id = t1.json()["id"]
        c1 = await client.post(f"/api/v1/tasks/{t1_id}/complete")
        assert c1.status_code == 200
        assert c1.json()["status"] == "DONE"
        assert c1.json()["completed_at"] is not None

        # TODO -> CANCELLED direct transition
        t2 = await client.post("/api/v1/tasks", json={"title": "Direct cancel"})
        t2_id = t2.json()["id"]
        c2 = await client.post(f"/api/v1/tasks/{t2_id}/cancel")
        assert c2.status_code == 200
        assert c2.json()["status"] == "CANCELLED"
        assert c2.json()["completed_at"] is None

        # Terminal state protection: CANCELLED cannot be started or completed
        fail_start = await client.post(f"/api/v1/tasks/{t2_id}/start")
        assert fail_start.status_code == 409
        assert "terminal state 'CANCELLED'" in fail_start.json()["error"]

        fail_comp = await client.post(f"/api/v1/tasks/{t2_id}/complete")
        assert fail_comp.status_code == 409
        assert "terminal state 'CANCELLED'" in fail_comp.json()["error"]


@pytest.mark.asyncio
async def test_task_patch_cannot_mutate_status() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_res = await client.post(
            "/api/v1/tasks",
            json={"title": "Patch Protection"},
        )
        task_id = create_res.json()["id"]
        # Attempt to pass status to PATCH
        # (should be ignored by schema / not modify status)
        patch_res = await client.patch(
            f"/api/v1/tasks/{task_id}",
            json={
                "title": "Updated Title",
                "status": "DONE",
                "priority": "LOW",
            },
        )
        assert patch_res.status_code == 200
        data = patch_res.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "LOW"
        assert data["status"] == "TODO"  # Still TODO!
        assert data["completed_at"] is None


@pytest.mark.asyncio
async def test_list_tasks_deterministic_ordering_and_filters() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create project
        proj = await client.post(
            "/api/v1/projects", json={"name": "Order Test Project"}
        )
        proj_id = proj.json()["id"]

        # Task 1 with future due date
        due1 = datetime(2026, 12, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        t1 = await client.post(
            "/api/v1/tasks",
            json={"title": "Later task", "project_id": proj_id, "due_at": due1},
        )
        # Task 2 with earlier due date
        due2 = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        t2 = await client.post(
            "/api/v1/tasks",
            json={"title": "Earlier task", "project_id": proj_id, "due_at": due2},
        )
        # Task 3 with no due date (nulls last)
        t3 = await client.post(
            "/api/v1/tasks",
            json={"title": "No due task", "project_id": proj_id},
        )

        list_res = await client.get(f"/api/v1/tasks?project_id={proj_id}")
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) == 3
        # Should be ordered by due_at asc (nulls last), so: Earlier -> Later -> No due
        assert items[0]["id"] == t2.json()["id"]
        assert items[1]["id"] == t1.json()["id"]
        assert items[2]["id"] == t3.json()["id"]


@pytest.mark.asyncio
async def test_project_task_relationship_preservation() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create project
        proj = await client.post("/api/v1/projects", json={"name": "Parent Project"})
        proj_id = proj.json()["id"]

        # Create two tasks under project
        t1 = await client.post(
            "/api/v1/tasks", json={"title": "Subtask 1", "project_id": proj_id}
        )
        t2 = await client.post(
            "/api/v1/tasks", json={"title": "Subtask 2", "project_id": proj_id}
        )
        assert t1.status_code == 201
        assert t2.status_code == 201

        # Retrieve tasks by project_id filter
        list_res = await client.get(f"/api/v1/tasks?project_id={proj_id}")
        assert list_res.status_code == 200
        assert len(list_res.json()) == 2

        # Verify no hard DELETE endpoint exists on projects
        del_res = await client.delete(f"/api/v1/projects/{proj_id}")
        assert del_res.status_code == 405  # Method Not Allowed
