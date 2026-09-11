from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.database.connection import get_db
from app.services.storage_service import storage_service
from app.services.inference_service import get_inference_provider
router=APIRouter(tags=["Health"])
@router.get("/health")
def health(): return {"status":"healthy","service":"NEZA AI Backend","version":"1.0.0"}
@router.get("/health/dependencies")
def dependencies(db=Depends(get_db)):
    result={"database":"ok","storage":"ok","ai_provider":"ok"}
    try: db.execute(text("SELECT 1"))
    except Exception as e: result["database"]="error: "+str(e)
    try: storage_service.root.mkdir(parents=True,exist_ok=True)
    except Exception as e: result["storage"]="error: "+str(e)
    try: get_inference_provider()
    except Exception as e: result["ai_provider"]="error: "+str(e)
    return result
