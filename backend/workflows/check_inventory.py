"""
Check Inventory Workflow

Example workflow using LangGraph for inventory management.

Workflow steps:
1. Load inventory data
2. Check stock levels
3. Identify low stock items
4. Generate recommendations
5. Return results
"""

from typing import Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from workflows.base import BaseWorkflow
from agents import InventoryAgent
from config import get_logger
from database import db_manager
from database.repositories import product_repository

logger = get_logger(__name__)


# Define workflow state
class InventoryState(TypedDict):
    """State for inventory workflow"""
    shop_id: int
    workflow_id: str
    threshold: int
    products: list
    low_stock_products: list
    recommendations: list
    result: dict


class CheckInventoryWorkflow(BaseWorkflow):
    """
    Inventory checking workflow using LangGraph
    
    This is a simple example workflow demonstrating:
    - LangGraph state management
    - Multi-step process
    - Database integration
    - Stateless design
    """
    
    def __init__(self):
        super().__init__()
        self.inventory_agent = InventoryAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build LangGraph workflow
        
        Graph structure:
        load_inventory → check_stock → generate_recommendations → format_result → END
        """
        # Create graph
        workflow = StateGraph(InventoryState)
        
        # Add nodes
        workflow.add_node("load_inventory", self._load_inventory)
        workflow.add_node("check_stock", self._check_stock)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("format_result", self._format_result)
        
        # Define edges
        workflow.set_entry_point("load_inventory")
        workflow.add_edge("load_inventory", "check_stock")
        workflow.add_edge("check_stock", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "format_result")
        workflow.add_edge("format_result", END)
        
        return workflow.compile()
    
    async def run(
        self,
        context: Dict[str, Any],
        workflow_id: str,
        user_id: Optional[int] = None,
        shop_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute inventory check workflow
        
        Args:
            context: Must contain 'shop_id' and optional 'threshold'
            workflow_id: Workflow execution ID
            user_id: Optional user ID
            shop_id: Optional shop ID (can also be in context)
            
        Returns:
            Workflow result with low stock items and recommendations
        """
        self.log_step("start", {"workflow_id": workflow_id, "shop_id": shop_id})
        
        # Prepare initial state
        initial_state: InventoryState = {
            "shop_id": shop_id or context.get("shop_id"),
            "workflow_id": workflow_id,
            "threshold": context.get("threshold", 10),
            "products": [],
            "low_stock_products": [],
            "recommendations": [],
            "result": {}
        }
        
        # Run LangGraph workflow
        final_state = await self.graph.ainvoke(initial_state)
        
        self.log_step("complete", {"workflow_id": workflow_id})
        
        return final_state["result"]
    
    async def _load_inventory(self, state: InventoryState) -> InventoryState:
        """Load inventory data from database"""
        self.log_step("load_inventory", {"shop_id": state["shop_id"]})
        
        async with db_manager.get_async_session() as db:
            products = await product_repository.get_by_shop(
                db,
                state["shop_id"],
                skip=0,
                limit=1000
            )
            
            state["products"] = [
                {
                    "id": p.id,
                    "nm_id": p.nm_id,
                    "title": p.title,
                    "vendor_code": p.vendor_code,
                    "current_stock": p.current_stock,
                    "is_active": p.is_active
                }
                for p in products
            ]
        
        logger.info(f"Loaded {len(state['products'])} products")
        return state
    
    async def _check_stock(self, state: InventoryState) -> InventoryState:
        """Check stock levels and identify low stock items"""
        self.log_step("check_stock", {"threshold": state["threshold"]})
        
        threshold = state["threshold"]
        low_stock = []
        
        for product in state["products"]:
            if product["is_active"] and product["current_stock"] <= threshold:
                low_stock.append(product)
        
        state["low_stock_products"] = low_stock
        
        logger.info(f"Found {len(low_stock)} low stock products")
        return state
    
    async def _generate_recommendations(self, state: InventoryState) -> InventoryState:
        """Generate recommendations for low stock items"""
        self.log_step("generate_recommendations")

        # Stage 6: delegate recommendation logic to stateless InventoryAgent.
        state["recommendations"] = self.inventory_agent.generate_reorder_recommendation(
            products=state["low_stock_products"],
            lead_time_days=7,
            safety_stock_days=3,
        )

        logger.info(f"Generated {len(state['recommendations'])} recommendations")
        return state
    
    async def _format_result(self, state: InventoryState) -> InventoryState:
        """Format final result"""
        self.log_step("format_result")
        
        state["result"] = {
            "workflow_id": state["workflow_id"],
            "shop_id": state["shop_id"],
            "total_products": len(state["products"]),
            "low_stock_count": len(state["low_stock_products"]),
            "critical_count": len([r for r in state["recommendations"] if r["priority"] == "critical"]),
            "high_priority_count": len([r for r in state["recommendations"] if r["priority"] == "high"]),
            "recommendations": state["recommendations"],
            "status": "completed"
        }
        
        return state
