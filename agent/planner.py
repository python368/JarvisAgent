"""Task planning module for the Jarvis agent.

This module provides task decomposition and planning capabilities
for breaking down complex tasks into executable steps.
"""

from __future__ import annotations

import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    """Status of a planned step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """Represents a single step in a plan."""
    step_id: int
    description: str
    action_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass 
class Plan:
    """Represents a complete plan for a task."""
    task: str
    steps: List[PlanStep] = field(default_factory=list)
    current_step: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_complete(self) -> bool:
        return all(s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED) for s in self.steps)
    
    @property
    def is_failed(self) -> bool:
        return any(s.status == StepStatus.FAILED for s in self.steps)
    
    @property
    def current_step_obj(self) -> Optional[PlanStep]:
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def next_step(self) -> Optional[PlanStep]:
        """Move to and return the next step."""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            step.status = StepStatus.IN_PROGRESS
            self.current_step += 1
            return step
        return None


class Planner:
    """Task planner for decomposing complex tasks into steps.
    
    The planner uses LLM to:
    1. Understand the user's task
    2. Break it down into actionable steps
    3. Identify required tools for each step
    4. Handle step dependencies
    """
    
    PLANNING_PROMPT = """You are a task planning assistant. Break down the following task into specific, executable steps.

For each step, specify:
1. A clear description of what to do
2. The action type (click, type, key_press, scroll, wait, open_app)
3. The parameters needed

Output format (JSON):
{
    "steps": [
        {"description": "...", "action_type": "...", "params": {...}},
        ...
    ],
    "estimated_time": "X minutes",
    "notes": "any important considerations"
}

Task: {task}
"""
    
    def __init__(self, llm_client=None):
        """Initialize the planner.
        
        Args:
            llm_client: Optional LLM client for AI-assisted planning.
        """
        self.llm_client = llm_client
    
    async def create_plan(self, task: str) -> Plan:
        """Create a plan for the given task.
        
        Args:
            task: The task description.
            
        Returns:
            Plan object with steps.
        """
        plan = Plan(task=task)
        
        if self.llm_client:
            # Use LLM for planning
            try:
                response = await self._llm_plan(task)
                steps = self._parse_steps(response)
                for i, step_data in enumerate(steps):
                    plan.steps.append(PlanStep(
                        step_id=i + 1,
                        description=step_data.get("description", ""),
                        action_type=step_data.get("action_type", "unknown"),
                        params=step_data.get("params", {}),
                    ))
            except Exception as e:
                # Fallback: create a simple single-step plan
                plan.steps.append(PlanStep(
                    step_id=1,
                    description=task,
                    action_type="unknown",
                ))
        else:
            # Simple single-step plan
            plan.steps.append(PlanStep(
                step_id=1,
                description=task,
                action_type="unknown",
            ))
        
        return plan
    
    async def _llm_plan(self, task: str) -> str:
        """Use LLM to generate a plan."""
        if self.llm_client is None:
            return "{\"steps\": [], \"estimated_time\": \"unknown\", \"notes\": \"No LLM client\"}"
        
        prompt = self.PLANNING_PROMPT.format(task=task)
        messages = [{"role": "user", "content": prompt}]
        return self.llm_client.chat(messages)
    
    def _parse_steps(self, response: str) -> List[Dict]:
        """Parse steps from LLM response."""
        # Try to extract JSON from response
        json_pattern = r"\{[\s\S]*\"steps\"\s*:\s*\[[\s\S]*?\][\s\S]*\}"
        match = re.search(json_pattern, response)
        
        if match:
            try:
                data = json.loads(match.group(0))
                return data.get("steps", [])
            except json.JSONDecodeError:
                pass
        
        # Fallback: simple text parsing
        return [{"description": response, "action_type": "unknown", "params": {}}]
    
    def refine_plan(self, plan: Plan, feedback: str) -> Plan:
        """Refine a plan based on execution feedback.
        
        Args:
            plan: The current plan.
            feedback: Feedback about what went wrong or needs adjustment.
            
        Returns:
            Updated plan.
        """
        # Simple refinement: add a retry or alternative step
        failed_steps = [s for s in plan.steps if s.status == StepStatus.FAILED]
        
        for step in failed_steps:
            # Mark as skipped for now
            step.status = StepStatus.SKIPPED
            # Add an alternative step
            alt_step = PlanStep(
                step_id=len(plan.steps) + 1,
                description=f"Retry: {step.description} (alternative approach suggested by feedback)",
                action_type=step.action_type,
                params=step.params,
            )
            plan.steps.append(alt_step)
        
        return plan


def create_simple_plan(task: str) -> Plan:
    """Create a simple single-step plan.
    
    Args:
        task: Task description.
        
    Returns:
        Plan with single step.
    """
    return Plan(task=task, steps=[
        PlanStep(step_id=1, description=task, action_type="unknown")
    ])