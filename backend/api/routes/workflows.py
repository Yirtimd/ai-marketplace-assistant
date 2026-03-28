"""
Workflows API routes

Endpoints for triggering and managing AI workflows via Orchestrator.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from orchestrator import orchestrator, workflow_registry

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# Request/Response models
class ExecuteWorkflowRequest(BaseModel):
    """Request to execute a workflow"""
    workflow_name: str
    context: dict
    shop_id: Optional[int] = None


class WorkflowResponse(BaseModel):
    """Workflow execution response"""
    workflow_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


class WorkflowStatusResponse(BaseModel):
    """Workflow status response"""
    workflow_id: str
    workflow_name: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error: Optional[str] = None


# === Workflow execution endpoints ===

@router.post("/execute", response_model=WorkflowResponse)
async def execute_workflow(request: ExecuteWorkflowRequest):
    """
    Execute a workflow
    
    Triggers an AI workflow execution through the Orchestrator.
    
    Example workflows:
    - check_inventory: Check inventory levels and generate recommendations
    - (Future) respond_to_review: Generate AI response to customer review
    - (Future) analyze_pricing: Analyze competitive pricing
    """
    try:
        result = await orchestrator.execute_workflow(
            workflow_name=request.workflow_name,
            context=request.context,
            shop_id=request.shop_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    Get workflow execution status
    
    Returns current status and result of a workflow execution.
    """
    try:
        status = await orchestrator.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=dict)
async def list_workflows(category: Optional[str] = Query(None, description="Filter by category")):
    """
    List all available workflows
    
    Returns:
        Dictionary of available workflows with metadata
    """
    try:
        workflows = workflow_registry.list_workflows(category=category)
        
        return {
            "total": len(workflows),
            "category": category,
            "workflows": workflows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Inventory workflow shortcuts ===

@router.post("/inventory/check")
async def check_inventory(
    shop_id: int = Query(..., description="Shop ID"),
    threshold: int = Query(10, description="Stock level threshold")
):
    """
    Quick endpoint to trigger inventory check workflow
    
    Shortcut for execute_workflow with workflow_name="check_inventory"
    """
    try:
        result = await orchestrator.execute_workflow(
            workflow_name="check_inventory",
            context={"shop_id": shop_id, "threshold": threshold},
            shop_id=shop_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales/analyze")
async def analyze_sales(
    shop_id: int = Query(..., description="Shop ID"),
    days_back: int = Query(14, description="Analysis period in days")
):
    """Shortcut to run sales_analysis_workflow."""
    try:
        return await orchestrator.execute_workflow(
            workflow_name="sales_analysis_workflow",
            context={"shop_id": shop_id, "days_back": days_back},
            shop_id=shop_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/respond")
async def respond_to_review(
    shop_id: int = Query(..., description="Shop ID"),
    review_id: Optional[int] = Query(None, description="Optional review ID"),
    execute_action: bool = Query(False, description="Execute Action Layer reply publish")
):
    """Shortcut to run review_workflow."""
    try:
        return await orchestrator.execute_workflow(
            workflow_name="review_workflow",
            context={
                "shop_id": shop_id,
                "review_id": review_id,
                "execute_action": execute_action,
            },
            shop_id=shop_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pricing/analyze")
async def analyze_pricing(
    shop_id: int = Query(..., description="Shop ID"),
    product_id: int = Query(..., description="Product ID"),
    execute_action: bool = Query(False, description="Execute Action Layer price update")
):
    """Shortcut to run pricing_workflow."""
    try:
        return await orchestrator.execute_workflow(
            workflow_name="pricing_workflow",
            context={
                "shop_id": shop_id,
                "product_id": product_id,
                "execute_action": execute_action,
            },
            shop_id=shop_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ProductCreationRequest(BaseModel):
    """Request payload for product card generation."""
    product_data: dict
    shop_id: Optional[int] = None
    execute_action: bool = False


@router.post("/content/create-card", response_model=WorkflowResponse)
async def create_product_card(request: ProductCreationRequest):
    """Shortcut to run product_creation_workflow."""
    try:
        return await orchestrator.execute_workflow(
            workflow_name="product_creation_workflow",
            context={
                "product_data": request.product_data,
                "execute_action": request.execute_action,
            },
            shop_id=request.shop_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
