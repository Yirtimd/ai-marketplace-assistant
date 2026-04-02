"""
Orchestrator Package

Central component for managing AI workflows.
"""

from orchestrator.registry import workflow_registry, WorkflowRegistry
from orchestrator.orchestrator import orchestrator, Orchestrator

# Register available workflows
from workflows.check_inventory import CheckInventoryWorkflow
from workflows.inventory_workflow import InventoryWorkflow
from workflows.sales_analysis_workflow import SalesAnalysisWorkflow
from workflows.product_creation_workflow import ProductCreationWorkflow
from workflows.review_workflow import ReviewWorkflow
from workflows.pricing_workflow import PricingWorkflow
from workflows.ai_generation_workflow import AIGenerationWorkflow
from workflows.action_execution_workflow import ActionExecutionWorkflow

workflow_registry.register(
    name="check_inventory",
    workflow_class=CheckInventoryWorkflow,
    description="Check inventory levels and generate restocking recommendations",
    category="inventory"
)

workflow_registry.register(
    name="inventory_workflow",
    workflow_class=InventoryWorkflow,
    description="Monitor inventory and build reorder recommendations",
    category="inventory"
)

workflow_registry.register(
    name="sales_analysis_workflow",
    workflow_class=SalesAnalysisWorkflow,
    description="Analyze sales dynamics and generate strategic recommendation",
    category="analytics"
)

workflow_registry.register(
    name="product_creation_workflow",
    workflow_class=ProductCreationWorkflow,
    description="Generate product card content artifacts",
    category="content"
)

workflow_registry.register(
    name="review_workflow",
    workflow_class=ReviewWorkflow,
    description="Analyze review sentiment and prepare reply payload",
    category="reviews"
)

workflow_registry.register(
    name="pricing_workflow",
    workflow_class=PricingWorkflow,
    description="Analyze pricing context and suggest target price",
    category="pricing"
)

workflow_registry.register(
    name="ai_generation_workflow",
    workflow_class=AIGenerationWorkflow,
    description="Execute direct AI generation operation through orchestrator",
    category="ai",
)

workflow_registry.register(
    name="action_execution_workflow",
    workflow_class=ActionExecutionWorkflow,
    description="Execute marketplace action through orchestrator workflow",
    category="actions",
)

# Compatibility aliases used in existing event mappings
workflow_registry.register(
    name="analyze_sales",
    workflow_class=SalesAnalysisWorkflow,
    description="Alias for sales_analysis_workflow",
    category="analytics"
)

workflow_registry.register(
    name="respond_to_review",
    workflow_class=ReviewWorkflow,
    description="Alias for review_workflow",
    category="reviews"
)

workflow_registry.register(
    name="analyze_pricing",
    workflow_class=PricingWorkflow,
    description="Alias for pricing_workflow",
    category="pricing"
)

__all__ = [
    "workflow_registry",
    "WorkflowRegistry",
    "orchestrator",
    "Orchestrator",
]
