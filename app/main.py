import csv
from io import StringIO
from fastapi import FastAPI, HTTPException, status, Query, Response,Request
from starlette.concurrency import run_in_threadpool
from dotenv import load_dotenv
from app.schemas import ExtractRequest, ExtractionResponse, LeadFields, AssistResponse, AssistRequest
from app.providers.base import ProviderOutputError, ProviderUnavailableError
from app.providers.factory import get_provider
from app.services.assistance_flow import process_assistance
from app.agent.loop import run_agent
import uuid
import os
from google import genai
from functools import partial
from app.storage.demo_store import list_leads, DEMO_LEADS
import logging
import json
import time

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="VA-AIS",
    description="VA-AIS is a virtual AI agent system that can be used to create and manage AI agents for various tasks.",
    version="0.1.0",
)
load_dotenv()


@app.get("/health", status_code=200)
async def root():
    return {"status": "ok"}


@app.post("/extract", status_code=status.HTTP_200_OK, response_model=ExtractionResponse)
async def extractor(request: ExtractRequest) -> ExtractionResponse:
    try:
        provider = get_provider()
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Provider configuration error",
        ) from None

    try:
        # The SDK has a synchronous client; keep it off the async event loop.
        return await run_in_threadpool(provider.extract, request.text)
    except ProviderUnavailableError:
        raise HTTPException(
            status_code=502, detail="Selected AI provider is unavailable"
        ) from None
    except ProviderOutputError:
        raise HTTPException(
            status_code=502, detail="Provider returned invalid structured output"
        ) from None



@app.post(
    "/assist",
    status_code=status.HTTP_200_OK,
    response_model=AssistResponse
)
async def assist(request: AssistRequest, http_request: Request):
    try:
        provider = get_provider()
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Provider configuration error",
        ) from None

    api_key = os.getenv("GEMINI_API_KEY")
    agent_runner = None

    if api_key:
        client = genai.Client(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        agent_runner = partial(
            run_agent,
            client=client,
            model_name=model_name,
        )

    try:
        return await run_in_threadpool(
            process_assistance,
            request,
            provider,
            http_request.state.request_id,
            agent_runner,
        )
    except ProviderUnavailableError:
        http_request.state.category="provider_failed"
        raise HTTPException(
            status_code=502,
            detail="AI provider failed to process the request",
        ) from None
    except ProviderOutputError:
            http_request.state.category="provider_output_error"
            raise HTTPException(
                status_code=502,
                detail="AI provider failed to process the request",
            ) from None
    


@app.get("/leads")
async def leads_getter(limit: int = Query(default=10, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    return list_leads(limit, offset)


@app.get("/leads/export")
async def export_leads():
    file = StringIO()

    writer = csv.DictWriter(
        file,
        fieldnames=list(DEMO_LEADS[0].keys())
    )

    writer.writeheader()
    writer.writerows(DEMO_LEADS)

    return Response(
        content=file.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="leads.csv"'
        }
    )

logger = logging.getLogger("uvicorn.error")


@app.middleware("http")
async def middle_ware(request: Request, call_next):

    request.state.request_id = uuid.uuid4().hex
    request.state.error_category = "none"

    start = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code

        if status_code == 422:
            request.state.error_category = "invalid_input"

        response.headers["X-Request-ID"] = request.state.request_id

        return response

    except Exception:
        request.state.error_category = "unexpected_internal_error"
        raise

    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000

        log_event = {
            "request_id": request.state.request_id,
            "route": request.url.path,
            "status_code": status_code,
            "elapsed_ms": round(elapsed_ms, 2),
            "error_category": request.state.error_category
        }

        logger.info(json.dumps(log_event))