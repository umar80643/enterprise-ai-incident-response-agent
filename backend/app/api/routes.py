import asyncio, json
from fastapi import APIRouter, Depends, Request, Header, HTTPException
from fastapi.responses import StreamingResponse
from app.security.auth import require_api_key
from app.schemas.domain import RepositoryIndexRequest, InvestigationCreate, ApprovalInput, RequestChangesInput
from app.services.repository_service import repository_service
from app.services.investigation_service import investigation_service
from app.integrations.github import verify_webhook

router=APIRouter()

@router.get("/health")
async def health(): return {"status":"ok","service":"enterprise-ai-incident-agent"}

@router.post("/api/v1/repositories/index",dependencies=[Depends(require_api_key)])
async def index_repository(body:RepositoryIndexRequest):
    return await repository_service.index(body.name,body.path,body.branch)

@router.get("/api/v1/repositories/{repo_id}/status",dependencies=[Depends(require_api_key)])
async def repository_status(repo_id:str): return repository_service.status(repo_id)

@router.post("/api/v1/investigations",dependencies=[Depends(require_api_key)])
async def create_investigation(body:InvestigationCreate):
    return await investigation_service.create(body.repository_id,body.title,body.description,body.branch)

@router.get("/api/v1/investigations/{iid}",dependencies=[Depends(require_api_key)])
async def get_investigation(iid:str): return investigation_service.get(iid)

@router.get("/api/v1/investigations/{iid}/events",dependencies=[Depends(require_api_key)])
async def events(iid:str): return investigation_service.events(iid)

@router.get("/api/v1/investigations/{iid}/evidence",dependencies=[Depends(require_api_key)])
async def evidence(iid:str): return investigation_service.evidence(iid)

@router.get("/api/v1/investigations/{iid}/usage",dependencies=[Depends(require_api_key)])
async def usage(iid:str): return investigation_service.usage(iid)

@router.get("/api/v1/investigations/{iid}/stream")
async def stream(iid:str, api_key:str):
    if api_key != __import__("app.core.config",fromlist=["get_settings"]).get_settings().api_key:
        raise HTTPException(401,"Invalid API key")
    async def gen():
        sent=0
        while True:
            events=investigation_service.events(iid)
            while sent < len(events):
                yield "data: "+json.dumps(events[sent])+"\n\n"; sent+=1
            status=investigation_service.get(iid)["status"]
            if status in {"SUCCESS","FAILED","WAITING_APPROVAL","REJECTED"}: break
            await asyncio.sleep(.5)
    return StreamingResponse(gen(),media_type="text/event-stream")

@router.post("/api/v1/investigations/{iid}/approve",dependencies=[Depends(require_api_key)])
async def approve(iid:str,body:ApprovalInput): return await investigation_service.approve(iid,body.comment)

@router.post("/api/v1/investigations/{iid}/reject",dependencies=[Depends(require_api_key)])
async def reject(iid:str,body:ApprovalInput): return await investigation_service.reject(iid,body.comment)

@router.post("/api/v1/investigations/{iid}/request-changes",dependencies=[Depends(require_api_key)])
async def request_changes(iid:str,body:RequestChangesInput): return await investigation_service.request_changes(iid,body.comment)

@router.post("/api/v1/github/webhook")
async def github_webhook(request:Request,x_hub_signature_256:str|None=Header(default=None)):
    body=await request.body()
    if not verify_webhook(body,x_hub_signature_256): raise HTTPException(401,"Invalid webhook signature")
    return {"accepted":True}
