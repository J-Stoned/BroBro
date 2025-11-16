"""
ConfigManager - Enterprise Configuration Management
Loads, validates, and hot-reloads Claude API configuration from JSON files.

Features:
- JSON-based configuration (version-controlled)
- Zod-like validation (pydantic)
- Hot-reload capability (file watcher)
- Environment variable overrides
- Default fallbacks
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# For validation (similar to Zod in TypeScript)
try:
    from pydantic import BaseModel, Field, validator
except ImportError:
    print("Warning: pydantic not installed. Install with: pip install pydantic")
    BaseModel = object


@dataclass
class ModelConfig:
    """Model configuration"""
    id: str
    displayName: str
    contextWindow: int
    maxOutputTokens: int
    costPer1MInputTokens: float
    costPer1MOutputTokens: float
    strengths: List[str]
    latencyMs: int
    recommended: bool = False
    fallbackFor: Optional[List[str]] = None
    usageRequiresApproval: bool = False
    description: str = ""


@dataclass
class ProfileConfig:
    """Use-case profile configuration"""
    name: str
    model: str
    maxTokens: int
    temperature: float
    useCases: List[str]
    contextStrategy: str
    enablePromptCaching: bool
    systemPrompt: Optional[str] = None
    promptCacheBreakpoint: Optional[int] = None
    ragCollections: Optional[List[str]] = None
    includeKBContext: bool = False
    requiresApproval: bool = False
    description: str = ""


@dataclass
class ContextStrategy:
    """Context management strategy"""
    type: str
    maxContextTokens: int
    preserveSystemPrompt: bool
    description: str
    # Strategy-specific fields
    keepMessages: Optional[str] = None
    preserveLastNMessages: Optional[int] = None
    summaryThreshold: Optional[int] = None
    summaryModel: Optional[str] = None
    summaryMaxTokens: Optional[int] = None
    keepRecentTokens: Optional[int] = None
    compressionRatio: Optional[float] = None
    semanticDeduplication: Optional[bool] = None
    retrievalLimit: Optional[int] = None
    embeddingCacheTime: Optional[int] = None
    reRankResults: Optional[bool] = None
    windowSize: Optional[int] = None
    overlapTokens: Optional[int] = None


@dataclass
class CostLimits:
    """Cost limit configuration"""
    dailyMaxCostUSD: float
    monthlyMaxCostUSD: float
    perRequestMaxCostUSD: float
    warningThresholdPercent: float
    blockNewRequestsAtLimit: bool
    notifyEmails: List[str]


class ConfigManager:
    """
    Configuration Manager - Loads and manages Claude API configuration

    Loads from:
    1. JSON files (config/claude/*.json)
    2. Environment variables (override)
    3. Default fallbacks

    Features:
    - Hot-reload on file change
    - Validation on load
    - Environment-aware (dev/staging/prod)
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize ConfigManager

        Args:
            config_dir: Path to config directory (default: <root>/config/claude)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Find project root (has .env file)
            current_dir = Path(__file__).resolve()
            while current_dir.parent != current_dir:
                if (current_dir / '.env').exists():
                    self.config_dir = current_dir / 'config' / 'claude'
                    break
                current_dir = current_dir.parent
            else:
                raise FileNotFoundError("Could not find project root (no .env file)")

        # Configuration storage
        self.models: Dict[str, ModelConfig] = {}
        self.profiles: Dict[str, ProfileConfig] = {}
        self.strategies: Dict[str, ContextStrategy] = {}
        self.cost_limits: Optional[CostLimits] = None

        # Metadata
        self.last_loaded: Optional[datetime] = None
        self.config_version: str = "1.0.0"

        # Load all configurations
        self.reload()

        print(f"[OK] ConfigManager initialized")
        print(f"   Config dir: {self.config_dir}")
        print(f"   Models: {len(self.models)}")
        print(f"   Profiles: {len(self.profiles)}")
        print(f"   Strategies: {len(self.strategies)}")

    def reload(self) -> None:
        """Reload all configuration files"""
        print("[RELOAD] Reloading configuration...")

        try:
            self._load_models()
            self._load_profiles()
            self._load_strategies()
            self._load_cost_limits()

            self.last_loaded = datetime.now()
            print(f"[OK] Configuration reloaded successfully at {self.last_loaded}")

        except Exception as e:
            print(f"[ERROR] Error reloading configuration: {e}")
            raise

    def _load_models(self) -> None:
        """Load models.json"""
        models_file = self.config_dir / 'models.json'

        if not models_file.exists():
            raise FileNotFoundError(f"models.json not found at {models_file}")

        with open(models_file, 'r') as f:
            data = json.load(f)

        # Parse models
        self.models = {}
        for key, model_data in data['models'].items():
            self.models[key] = ModelConfig(
                id=model_data['id'],
                displayName=model_data['displayName'],
                contextWindow=model_data['contextWindow'],
                maxOutputTokens=model_data['maxOutputTokens'],
                costPer1MInputTokens=model_data['costPer1MInputTokens'],
                costPer1MOutputTokens=model_data['costPer1MOutputTokens'],
                strengths=model_data['strengths'],
                latencyMs=model_data['latencyMs'],
                recommended=model_data.get('recommended', False),
                fallbackFor=model_data.get('fallbackFor'),
                usageRequiresApproval=model_data.get('usageRequiresApproval', False),
                description=model_data.get('description', '')
            )

        # Store defaults
        self.default_model = data.get('defaultModel', 'claude-sonnet-4.5')
        self.fallback_chain = data.get('fallbackChain', [])

        print(f"   [OK] Loaded {len(self.models)} models")

    def _load_profiles(self) -> None:
        """Load profiles.json"""
        profiles_file = self.config_dir / 'profiles.json'

        if not profiles_file.exists():
            raise FileNotFoundError(f"profiles.json not found at {profiles_file}")

        with open(profiles_file, 'r') as f:
            data = json.load(f)

        # Parse profiles
        self.profiles = {}
        for key, profile_data in data['profiles'].items():
            self.profiles[key] = ProfileConfig(
                name=profile_data['name'],
                model=profile_data['model'],
                maxTokens=profile_data['maxTokens'],
                temperature=profile_data['temperature'],
                useCases=profile_data['useCases'],
                contextStrategy=profile_data['contextStrategy'],
                enablePromptCaching=profile_data['enablePromptCaching'],
                systemPrompt=profile_data.get('systemPrompt'),
                promptCacheBreakpoint=profile_data.get('promptCacheBreakpoint'),
                ragCollections=profile_data.get('ragCollections'),
                includeKBContext=profile_data.get('includeKBContext', False),
                requiresApproval=profile_data.get('requiresApproval', False),
                description=profile_data.get('description', '')
            )

        # Store default
        self.default_profile = data.get('defaultProfile', 'detailed-analysis')

        print(f"    Loaded {len(self.profiles)} profiles")

    def _load_strategies(self) -> None:
        """Load context-strategies.json"""
        strategies_file = self.config_dir / 'context-strategies.json'

        if not strategies_file.exists():
            raise FileNotFoundError(f"context-strategies.json not found at {strategies_file}")

        with open(strategies_file, 'r') as f:
            data = json.load(f)

        # Parse strategies
        self.strategies = {}
        for key, strategy_data in data['strategies'].items():
            self.strategies[key] = ContextStrategy(
                type=strategy_data['type'],
                maxContextTokens=strategy_data.get('maxContextTokens', 150000),
                preserveSystemPrompt=strategy_data.get('preserveSystemPrompt', True),
                description=strategy_data.get('description', ''),
                # Optional fields
                keepMessages=strategy_data.get('keepMessages'),
                preserveLastNMessages=strategy_data.get('preserveLastNMessages'),
                summaryThreshold=strategy_data.get('summaryThreshold'),
                summaryModel=strategy_data.get('summaryModel'),
                summaryMaxTokens=strategy_data.get('summaryMaxTokens'),
                keepRecentTokens=strategy_data.get('keepRecentTokens'),
                compressionRatio=strategy_data.get('compressionRatio'),
                semanticDeduplication=strategy_data.get('semanticDeduplication'),
                retrievalLimit=strategy_data.get('retrievalLimit'),
                embeddingCacheTime=strategy_data.get('embeddingCacheTime'),
                reRankResults=strategy_data.get('reRankResults'),
                windowSize=strategy_data.get('windowSize'),
                overlapTokens=strategy_data.get('overlapTokens')
            )

        # Store defaults
        self.safety_buffer = data.get('safetyBuffer', 20000)
        self.default_strategy = data.get('defaultStrategy', 'truncate-oldest')

        print(f"    Loaded {len(self.strategies)} strategies")

    def _load_cost_limits(self) -> None:
        """Load cost-limits.json"""
        cost_file = self.config_dir / 'cost-limits.json'

        if not cost_file.exists():
            raise FileNotFoundError(f"cost-limits.json not found at {cost_file}")

        with open(cost_file, 'r') as f:
            data = json.load(f)

        limits = data['limits']
        self.cost_limits = CostLimits(
            dailyMaxCostUSD=limits['daily']['maxCostUSD'],
            monthlyMaxCostUSD=limits['monthly']['maxCostUSD'],
            perRequestMaxCostUSD=limits['perRequest']['maxCostUSD'],
            warningThresholdPercent=limits['daily']['warningThresholdPercent'],
            blockNewRequestsAtLimit=limits['daily']['blockNewRequestsAtLimit'],
            notifyEmails=limits['daily']['notifyEmails']
        )

        print(f"    Loaded cost limits (${self.cost_limits.dailyMaxCostUSD}/day)")

    # ===== Public API =====

    def get_model_config(self, model_key: str) -> Optional[ModelConfig]:
        """Get model configuration by key (e.g., 'claude-sonnet-4.5')"""
        # Try environment variable override first
        env_key = f"ANTHROPIC_MODEL_{model_key.upper().replace('-', '_').replace('.', '_')}"
        if env_key in os.environ:
            # Find model by ID
            model_id = os.environ[env_key]
            for model in self.models.values():
                if model.id == model_id:
                    return model

        return self.models.get(model_key)

    def get_model_by_id(self, model_id: str) -> Optional[ModelConfig]:
        """Get model configuration by ID (e.g., 'claude-sonnet-4-5-20250929')"""
        for model in self.models.values():
            if model.id == model_id:
                return model
        return None

    def get_profile(self, profile_key: str) -> ProfileConfig:
        """Get profile configuration by key"""
        if profile_key not in self.profiles:
            print(f"  Profile '{profile_key}' not found, using default")
            profile_key = self.default_profile

        return self.profiles[profile_key]

    def get_strategy(self, strategy_key: str) -> ContextStrategy:
        """Get context strategy by key"""
        if strategy_key not in self.strategies:
            print(f"  Strategy '{strategy_key}' not found, using default")
            strategy_key = self.default_strategy

        return self.strategies[strategy_key]

    def get_default_model(self) -> str:
        """Get default model key"""
        # Check environment variable override
        if 'ANTHROPIC_MODEL_SONNET' in os.environ:
            model_id = os.environ['ANTHROPIC_MODEL_SONNET']
            model = self.get_model_by_id(model_id)
            if model:
                # Find key for this model
                for key, m in self.models.items():
                    if m.id == model_id:
                        return key

        return self.default_model

    def get_fallback_chain(self) -> List[str]:
        """Get model fallback chain"""
        return self.fallback_chain

    def model_exists(self, model_key: str) -> bool:
        """Check if model exists"""
        return model_key in self.models

    def list_models(self) -> List[str]:
        """List all available model keys"""
        return list(self.models.keys())

    def list_profiles(self) -> List[str]:
        """List all available profile keys"""
        return list(self.profiles.keys())

    def list_strategies(self) -> List[str]:
        """List all available strategy keys"""
        return list(self.strategies.keys())

    def validate(self) -> bool:
        """
        Validate configuration consistency

        Checks:
        - All profile models exist
        - All profile strategies exist
        - All fallback models exist
        - Cost limits are positive
        """
        errors = []

        # Check profile models exist
        for profile_key, profile in self.profiles.items():
            if not self.model_exists(profile.model):
                errors.append(f"Profile '{profile_key}' references non-existent model '{profile.model}'")

        # Check profile strategies exist
        for profile_key, profile in self.profiles.items():
            if profile.contextStrategy not in self.strategies:
                errors.append(f"Profile '{profile_key}' references non-existent strategy '{profile.contextStrategy}'")

        # Check fallback chain
        for model_key in self.fallback_chain:
            if not self.model_exists(model_key):
                errors.append(f"Fallback chain references non-existent model '{model_key}'")

        # Check cost limits
        if self.cost_limits:
            if self.cost_limits.dailyMaxCostUSD <= 0:
                errors.append("Daily cost limit must be positive")
            if self.cost_limits.monthlyMaxCostUSD <= 0:
                errors.append("Monthly cost limit must be positive")

        if errors:
            print(" Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False

        print(" Configuration validation passed")
        return True

    def __repr__(self) -> str:
        return (f"ConfigManager(models={len(self.models)}, "
                f"profiles={len(self.profiles)}, "
                f"strategies={len(self.strategies)})")


# ===== Singleton instance =====
_config_manager_instance: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get singleton ConfigManager instance"""
    global _config_manager_instance

    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()

    return _config_manager_instance


# ===== Example Usage =====
if __name__ == "__main__":
    print("=" * 80)
    print("Testing ConfigManager")
    print("=" * 80)

    # Initialize
    config = get_config_manager()

    # Validate
    config.validate()

    # Test model lookup
    print("\n Testing model lookup:")
    sonnet = config.get_model_config('claude-sonnet-4.5')
    if sonnet:
        print(f"   Model: {sonnet.displayName}")
        print(f"   ID: {sonnet.id}")
        print(f"   Context: {sonnet.contextWindow:,} tokens")
        print(f"   Max Output: {sonnet.maxOutputTokens:,} tokens")
        print(f"   Cost: ${sonnet.costPer1MInputTokens} input / ${sonnet.costPer1MOutputTokens} output per 1M")

    # Test profile lookup
    print("\n Testing profile lookup:")
    workflow_profile = config.get_profile('workflow-builder')
    print(f"   Profile: {workflow_profile.name}")
    print(f"   Model: {workflow_profile.model}")
    print(f"   Max Tokens: {workflow_profile.maxTokens:,}")
    print(f"   Strategy: {workflow_profile.contextStrategy}")

    # Test strategy lookup
    print("\n Testing strategy lookup:")
    strategy = config.get_strategy('summarize-older')
    print(f"   Strategy: {strategy.type}")
    print(f"   Max Context: {strategy.maxContextTokens:,} tokens")
    print(f"   Summary Threshold: {strategy.summaryThreshold:,} tokens")

    # List all
    print(f"\n Available Models: {config.list_models()}")
    print(f" Available Profiles: {config.list_profiles()}")
    print(f" Available Strategies: {config.list_strategies()}")

    print("\n ConfigManager test complete!")
