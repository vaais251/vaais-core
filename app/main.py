from fastapi import FastAPI, HTTPException, status, Query
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
from app.storage.demo_store import list_leads

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
async def assist(request: AssistRequest):
    try:
        provider = get_provider()
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Provider configuration error",
        )
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
            uuid.uuid4().hex,
            agent_runner,
        )
    except (ProviderUnavailableError, ProviderOutputError):
        raise HTTPException(
            status_code=502,
            detail="AI provider failed to process the request",
        ) from None


@app.get("/leads")
async def leads_getter(limit: int = Query(default=10, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    return list_leads(limit, offset)
