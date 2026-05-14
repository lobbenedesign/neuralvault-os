import json
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("AgentRewards")

class AgentRewardManager:
    """
    [v9.0] Meritocratic Reward System for NeuralVault Swarm Agents.
    Tracks agent accuracy and manages execution priority tokens.
    """
    
    def __init__(self, storage_path: str = "vault_data/agent_rewards.json"):
        self.storage_path = storage_path
        self.rewards = {} # {agent_id: {"merit": float, "history": []}}
        self._load_rewards()

    def _load_rewards(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.rewards = json.load(f)
            except Exception as e:
                logger.error(f"Error loading rewards: {e}")
                self.rewards = {}

    def _save_rewards(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.rewards, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving rewards: {e}")

    def get_merit(self, agent_id: str) -> float:
        """Returns the current merit score of an agent (default 1.0)."""
        return self.rewards.get(agent_id, {}).get("merit", 1.0)

    def update_reward(self, agent_id: str, delta: float, reason: str):
        """Updates agent merit score based on performance."""
        if agent_id not in self.rewards:
            self.rewards[agent_id] = {"merit": 1.0, "history": []}
        
        old_merit = self.rewards[agent_id]["merit"]
        new_merit = max(0.1, old_merit + delta) # Merit cannot go below 0.1
        
        self.rewards[agent_id]["merit"] = round(new_merit, 3)
        self.rewards[agent_id]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "delta": delta,
            "reason": reason,
            "new_total": new_merit
        })
        
        # Keep history compact
        if len(self.rewards[agent_id]["history"]) > 50:
            self.rewards[agent_id]["history"] = self.rewards[agent_id]["history"][-50:]
            
        self._save_rewards()
        logger.info(f"🏆 Agent {agent_id} merit updated: {old_merit} -> {new_merit} ({reason})")

    def get_priority_ranking(self) -> List[Tuple[str, float]]:
        """Returns agents sorted by merit."""
        return sorted(
            [(aid, data["merit"]) for aid, data in self.rewards.items()],
            key=lambda x: x[1],
            reverse=True
        )
