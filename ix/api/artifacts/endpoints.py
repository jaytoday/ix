from uuid import UUID

from asgiref.sync import sync_to_async
from django.db.models import Q
from fastapi import HTTPException, APIRouter, Depends
from fastapi.responses import FileResponse
from typing import Optional
from ix.api.artifacts.types import (
    Artifact as ArtifactPydantic,
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactPage,
)
from ix.task_log.models import Artifact
from ix.api.auth import get_request_user


router = APIRouter()
__all__ = ["router"]


@router.post("/artifacts/", response_model=ArtifactPydantic, tags=["Artifacts"])
async def create_artifact(data: ArtifactCreate, user=Depends(get_request_user)):
    instance = Artifact(user=user, **data.model_dump())
    await instance.asave()
    return ArtifactPydantic.model_validate(instance)


@router.get(
    "/artifacts/{artifact_id}", response_model=ArtifactPydantic, tags=["Artifacts"]
)
async def get_artifact(artifact_id: str, user=Depends(get_request_user)):
    try:
        query = Artifact.objects.filter(pk=artifact_id)
        artifact = await Artifact.filter_owners(user, query).aget()
    except Artifact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactPydantic.model_validate(artifact)


@router.get("/artifacts/", response_model=ArtifactPage, tags=["Artifacts"])
async def get_artifacts(
    chat_id: Optional[UUID] = None,
    search: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    user=Depends(get_request_user),
):
    query = (
        Artifact.objects.filter(Q(name__icontains=search) | Q(key__icontains=search))
        if search
        else Artifact.objects.all()
    )
    query = Artifact.filter_owners(user, query)
    if chat_id:
        query = query.filter(task__leading_chats__id=chat_id)

    # punting on async implementation of pagination until later
    return await sync_to_async(ArtifactPage.paginate)(
        output_model=ArtifactPydantic, queryset=query, limit=limit, offset=offset
    )


@router.put(
    "/artifacts/{artifact_id}", response_model=ArtifactPydantic, tags=["Artifacts"]
)
async def update_artifact(
    artifact_id: str, data: ArtifactUpdate, user=Depends(get_request_user)
):
    try:
        query = Artifact.objects.filter(pk=artifact_id)
        instance = await Artifact.filter_owners(user, query).aget()
    except Artifact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Artifact not found")
    for attr, value in data.model_dump().items():
        setattr(instance, attr, value)
    await instance.asave()
    return ArtifactPydantic.model_validate(instance)


@router.get(
    "/artifacts/{artifact_id}/download",
    tags=["Artifacts"],
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Download the artifact",
        },
        404: {"description": "Artifact not found"},
    },
)
async def download_artifact(artifact_id: str, user=Depends(get_request_user)):
    try:
        query = Artifact.objects.filter(pk=artifact_id)
        artifact = await Artifact.filter_owners(user, query).aget()
    except Artifact.DoesNotExist:
        raise HTTPException(status_code=404, detail="Artifact not found")

    file_path = artifact.storage["id"]
    file_name = file_path.split("/")[-1]

    return FileResponse(
        file_path, media_type="application/octet-stream", filename=file_name
    )
