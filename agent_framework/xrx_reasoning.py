from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Callable, Awaitable
import redis
import logging
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Message(BaseModel):
    role: str
    content: str

class AgentRequest(BaseModel):
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    session: Dict[str, Any] = Field(default_factory=dict, description="Session information for the conversation")
    action: Optional[Dict[str, Any]] = Field({}, description="Optional action to be performed by the agent")

class CancelResponse(BaseModel):
    detail: str

class xrx_reasoning:
    def __init__(self, run_agent: Callable[[dict], Awaitable[str]]):
        self.app = FastAPI()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_client = redis.asyncio.Redis(host=redis_host, port=6379, db=0)
        self.run_agent = run_agent
        self.setup_routes()

    def __call__(self):
        return self.app

    def setup_routes(self):
        @self.app.post("/run-reasoning-agent", response_class=StreamingResponse)
        async def execute_agent(request: Request, agent_request: AgentRequest):
            """
            Execute the reasoning agent and stream the results.

            This endpoint starts a new task for the reasoning agent and returns
            a streaming response with the agent's output.

            The task ID is returned in the 'X-Task-ID' header of the response.

            Args:
                request (Request): The request object containing headers and client information.
                agent_request (AgentRequest): The input for the reasoning agent, including messages, session information, and an optional action.

            Returns:
                StreamingResponse: A streaming response containing the agent's output.

            Raises:
                HTTPException: If an error occurs during processing.
            """
            try:
                body = agent_request.model_dump()
                self.logger.info(f"Received request body: {body}")
                self.logger.info(f"Request headers: {request.headers}")
                self.logger.info(f"Request client: {request.client}")

                task_id = str(uuid.uuid4())
                self.logger.info(f"Created task with task ID: {task_id}")
                body['task_id'] = task_id

                await self.redis_client.set('task-' + task_id, 'running')
                self.logger.info(f"Stored task ID {task_id} in Redis with status 'running'")

                headers = {"X-Task-ID": task_id}

                return StreamingResponse(self.stream_run_agent(body), media_type="text/event-stream", headers=headers)
            except HTTPException as e:
                self.logger.error(f"HTTPException occurred: {str(e)}")
                raise e
            except Exception as e:
                self.logger.error(f"An error occurred while processing the request: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/cancel-reasoning-agent/{task_id}", response_model=CancelResponse)
        async def cancel_agent(task_id: str = Path(..., description="The ID of the task to cancel")):
            """
            Cancel a running reasoning agent task.

            This endpoint attempts to cancel a task identified by the given task_id.
            It sets the task status to 'cancelled' in Redis.

            Args:
                task_id (str): The ID of the task to cancel.

            Returns:
                CancelResponse: A response indicating the result of the cancellation attempt.

            Raises:
                HTTPException: If an error occurs during the cancellation process.
            """
            try:
                await self.redis_client.set('task-' + task_id, 'cancelled')
                self.logger.info(f"Task {task_id} set to cancelled")
                return JSONResponse(content={"detail": f"Task {task_id} cancelled"}, status_code=200)
            except Exception as e:
                self.logger.error(f"An error occurred while cancelling the task: {str(e)}")
                return JSONResponse(content={"detail": f"An error occurred: {str(e)}"}, status_code=500)

    async def stream_run_agent(self, body):
        try:
            self.logger.info("Starting run_agent")
            task_id = body.get("task_id")
            async for result in self.run_agent(body):
                self.logger.info(f"Yielding result: {result}")
                yield f"data: {result}\n\n"

                if 'error' in result:
                    return
            self.logger.info("Finished run_agent")
        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")
            yield f"data: An error occurred: {str(e)}\n\n"
            return
