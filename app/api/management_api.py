from fastapi import APIRouter
from pathlib import Path
from pydantic import BaseModel
import toml
from loguru import logger


router = APIRouter(prefix="/v1", tags=["management"])


#### Health Check ##############
class HealthResponse(BaseModel):
    status: str = "ok"


@router.get("/management/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint, returns 200 if the system is running
    """
    return HealthResponse()


#### Version ####################
__version__ = None


def _load_version():
    global __version__
    if __version__ is not None:
        return __version__

    current_dir = Path(__file__).resolve().parent.parent.parent
    for i in range(3):
        pyproject_path = current_dir / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "r") as f:
                config = toml.load(f)
                __version__ = config["project"]["version"]
                logger.info(f"API Version: {__version__}")
                return __version__

    __version__ = "unknown"
    logger.warning(f"App Version is not found in pyproject.toml path: {pyproject_path}")
    return __version__


@router.get("/version")
@router.get("/management/version")
async def version_api():
    """
    Version endpoint, returns the version of the system
    """
    return {"version": _load_version()}
