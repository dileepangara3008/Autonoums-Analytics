from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class AgentState(BaseModel):
    # Data
    dataset: Any = None
    cleaned_data: Any = None
    
    # Analysis
    summary_stats: Dict = {}
    eda_results: Dict = {}
    statistical_results: Dict = {}
    
    # Outputs
    charts: List = []
    insights: str = ""
    
    # RAG
    query: str = ""
    query_type: str = ""
    retrieved_docs: List = []
    final_response: str = ""
    
    # Control
    current_stage: str = ""
    waiting_for_input: bool = False
    
    # HITL
    hitl_responses: Dict = {}
    
    # Debug
    logs: List = []
    errors: List = []