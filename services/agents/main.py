"""
Agents microservice API
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import httpx
import os

from .writer_agent import WriterAgent
from .reviewer_agent import ReviewerAgent

app = FastAPI(title="Mr. Post Agents Service", version="1.0.0")

# Initialize agents
writer_agent = WriterAgent()
reviewer_agent = ReviewerAgent()

# Pydantic models
class WriteRequest(BaseModel):
    user_idea: str
    preferences: Dict[str, Any] = {}
    post_id: Optional[int] = None
    token: str

class ReviewRequest(BaseModel):
    post_content: str
    original_idea: str
    preferences: Dict[str, Any] = {}
    post_id: Optional[int] = None
    token: str

class ProcessPostRequest(BaseModel):
    user_idea: str
    preferences: Dict[str, Any] = {}
    post_id: int
    token: str

# Storage service communication
async def update_post_in_storage(post_id: int, data: Dict[str, Any], token: str):
    """Update post in storage service"""
    storage_url = os.getenv("STORAGE_SERVICE_URL", "http://localhost:8001")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{storage_url}/posts/{post_id}",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error updating post in storage: {e}")
            raise

# Single agent endpoints
@app.post("/writer/generate")
async def generate_content(request: WriteRequest):
    """Generate content using the writer agent"""
    
    input_data = {
        "user_idea": request.user_idea,
        "preferences": request.preferences
    }
    
    result = await writer_agent.process(input_data)
    
    # Update post in storage if post_id is provided
    if request.post_id and result.get("success"):
        try:
            await update_post_in_storage(
                request.post_id,
                {
                    "writer_output": result["content"],
                    "status": "written"
                },
                request.token
            )
        except Exception as e:
            print(f"Failed to update storage: {e}")
            # Continue anyway, we still have the result
    
    return result

@app.post("/reviewer/review")
async def review_content(request: ReviewRequest):
    """Review content using the reviewer agent"""
    
    input_data = {
        "post_content": request.post_content,
        "original_idea": request.original_idea,
        "preferences": request.preferences
    }
    
    result = await reviewer_agent.process(input_data)
    
    # Update post in storage if post_id is provided
    if request.post_id and result.get("success"):
        try:
            await update_post_in_storage(
                request.post_id,
                {
                    "reviewer_feedback": result["feedback"],
                    "final_content": result["improved_content"],
                    "status": "reviewed"
                },
                request.token
            )
        except Exception as e:
            print(f"Failed to update storage: {e}")
            # Continue anyway, we still have the result
    
    return result

# Multi-agent workflow endpoint
@app.post("/process-post")
async def process_post_workflow(request: ProcessPostRequest, background_tasks: BackgroundTasks):
    """
    Complete workflow: Write content, then review it
    This runs the writer and reviewer agents in sequence
    """
    
    # Start the background workflow
    background_tasks.add_task(
        run_complete_workflow,
        request.user_idea,
        request.preferences,
        request.post_id,
        request.token
    )
    
    return {
        "message": "Post processing started",
        "post_id": request.post_id,
        "status": "processing"
    }

async def run_complete_workflow(user_idea: str, preferences: Dict[str, Any], post_id: int, token: str):
    """Run the complete writer -> reviewer workflow"""
    
    try:
        # Step 1: Generate content with writer agent
        writer_input = {
            "user_idea": user_idea,
            "preferences": preferences
        }
        
        writer_result = await writer_agent.process(writer_input)
        
        if not writer_result.get("success"):
            await update_post_in_storage(
                post_id,
                {
                    "status": "error",
                    "writer_output": f"Error: {writer_result.get('error', 'Unknown error')}"
                },
                token
            )
            return
        
        # Update with writer output
        await update_post_in_storage(
            post_id,
            {
                "writer_output": writer_result["content"],
                "status": "written"
            },
            token
        )
        
        # Step 2: Review content with reviewer agent
        reviewer_input = {
            "post_content": writer_result["content"],
            "original_idea": user_idea,
            "preferences": preferences
        }
        
        reviewer_result = await reviewer_agent.process(reviewer_input)
        
        if not reviewer_result.get("success"):
            await update_post_in_storage(
                post_id,
                {
                    "status": "error",
                    "reviewer_feedback": f"Error: {reviewer_result.get('error', 'Unknown error')}"
                },
                token
            )
            return
        
        # Update with final reviewed content
        await update_post_in_storage(
            post_id,
            {
                "reviewer_feedback": reviewer_result["feedback"],
                "final_content": reviewer_result["improved_content"],
                "status": "completed"
            },
            token
        )
        
    except Exception as e:
        # Handle any unexpected errors
        try:
            await update_post_in_storage(
                post_id,
                {
                    "status": "error",
                    "reviewer_feedback": f"Workflow error: {str(e)}"
                },
                token
            )
        except:
            print(f"Failed to update post {post_id} with error status: {e}")

# Agent info endpoints
@app.get("/agents/info")
async def get_agents_info():
    """Get information about available agents"""
    return {
        "agents": [
            {
                "id": writer_agent.agent_id,
                "name": writer_agent.name,
                "description": writer_agent.description,
                "type": "writer"
            },
            {
                "id": reviewer_agent.agent_id,
                "name": reviewer_agent.name,
                "description": reviewer_agent.description,
                "type": "reviewer"
            }
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "agents",
        "agents_available": [
            writer_agent.agent_id,
            reviewer_agent.agent_id
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)