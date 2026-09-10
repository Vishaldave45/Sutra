from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app


@pytest.mark.asyncio
async def test_create_and_retrieve_project() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        create_res = await client.post(
            "/api/v1/projects",
            json={
                "name": "Personal OS",
                "description": "Building Sutra",
                "metadata": {"category": "core"},
            },
        )
        assert create_res.status_code == 201
        data = create_res.json()
        project_id = data["id"]
        assert project_id is not None
        assert data["name"] == "Personal OS"
        assert data["description"] == "Building Sutra"
        assert data["status"] == "ACTIVE"
        assert data["completed_at"] is None
        assert data["metadata"] == {"category": "core"}
        assert "created_at" in data
        assert "updated_at" in data

        # Retrieve
        get_res = await client.get(f"/api/v1/projects/{project_id}")
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["id"] == project_id
        assert get_data["name"] == "Personal OS"


@pytest.mark.asyncio
async def test_create_project_validation() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Empty name
        res = await client.post(
            "/api/v1/projects",
            json={"name": "   "},
        )
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_get_nonexistent_project_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/api/v1/projects/{uuid4()}")
        assert res.status_code == 404
        assert res.json()["error"] is not None


@pytest.mark.asyncio
async def test_list_projects_filtering_and_pagination() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res1 = await client.post(
            "/api/v1/projects",
            json={"name": "Project Alpha"},
        )
        res2 = await client.post(
            "/api/v1/projects",
            json={"name": "Project Beta"},
        )
        assert res1.status_code == 201
        assert res2.status_code == 201

        # List all
        list_res = await client.get("/api/v1/projects?limit=50&offset=0")
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) >= 2
        names = [p["name"] for p in items]
        assert "Project Alpha" in names
        assert "Project Beta" in names

        # Filter by status
        filter_res = await client.get("/api/v1/projects?status=ACTIVE")
        assert filter_res.status_code == 200
        for p in filter_res.json():
            assert p["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_update_project() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_res = await client.post(
            "/api/v1/projects",
            json={"name": "Initial Name"},
        )
        assert create_res.status_code == 201
        project_id = create_res.json()["id"]

        patch_res = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={
                "name": "Updated Name",
                "description": "Updated Description",
                "metadata": {"v": 2},
            },
        )
        assert patch_res.status_code == 200
        updated = patch_res.json()
        assert updated["name"] == "Updated Name"
        assert updated["description"] == "Updated Description"
        assert updated["metadata"] == {"v": 2}


@pytest.mark.asyncio
async def test_complete_and_archive_project_invariants() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        res = await client.post(
            "/api/v1/projects",
            json={"name": "Lifecycle Project"},
        )
        project_id = res.json()["id"]
        assert res.json()["status"] == "ACTIVE"
        assert res.json()["completed_at"] is None

        # Complete
        comp_res = await client.post(f"/api/v1/projects/{project_id}/complete")
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["status"] == "COMPLETED"
        assert comp_data["completed_at"] is not None

        # Idempotent complete
        comp_res2 = await client.post(f"/api/v1/projects/{project_id}/complete")
        assert comp_res2.status_code == 200
        assert comp_res2.json()["status"] == "COMPLETED"

        # Archive from completed
        arch_res = await client.post(f"/api/v1/projects/{project_id}/archive")
        assert arch_res.status_code == 200
        arch_data = arch_res.json()
        assert arch_data["status"] == "ARCHIVED"
        assert arch_data["completed_at"] is None

        # Cannot complete archived project
        comp_arch = await client.post(f"/api/v1/projects/{project_id}/complete")
        assert comp_arch.status_code == 409
        assert (
            "Cannot complete project in 'ARCHIVED' status" in comp_arch.json()["error"]
        )
