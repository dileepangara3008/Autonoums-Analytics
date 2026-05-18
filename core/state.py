from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional


class AgentState(BaseModel):

    # -----------------------------
    # 📂 INPUT
    # -----------------------------
    file: Optional[Any] = None
    query: Optional[str] = None

    # -----------------------------
    # 📊 DATA
    # -----------------------------
    dataset: Optional[Any] = None
    cleaned_data: Optional[Any] = None

    # -----------------------------
    # 📈 RESULTS
    # -----------------------------
    eda_results: Optional[Dict] = None
    statistical_results: Optional[Dict] = None
    charts: List = Field(default_factory=list)

    # 🔥 FIXED HERE
    insights: Optional[Dict[str, Any]] = None

    # -----------------------------
    # 🔁 FLOW CONTROL
    # -----------------------------
    current_stage: str = "START"
    waiting_for_input: bool = False

    # -----------------------------
    # 🧠 HITL
    # -----------------------------
    hitl_responses: Dict = Field(default_factory=dict)

    # -----------------------------
    # 🪵 DEBUG
    # -----------------------------
    logs: List = Field(default_factory=list)
    errors: List = Field(default_factory=list)

    chat_history: list = Field(default_factory=list)