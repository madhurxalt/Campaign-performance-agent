"""Database models for Performance Dashboard using SQLModel."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, JSON, Column


class CampaignConfiguration(SQLModel, table=True):
    """Store campaign configurations created by the agent."""
    __tablename__ = "campaign_configurations"
    __table_args__ = {"schema": "smartify"}
    
    campaign_id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: Optional[UUID] = Field(foreign_key="smartify.agent_conversations.conversation_id")
    campaign_name: str = Field(max_length=255)
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    selected_displays: List[Dict] = Field(default=[], sa_column=Column(JSON))
    total_budget: float
    start_date: datetime
    end_date: datetime
    status: str = Field(default="draft", max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class CampaignLocation(SQLModel, table=True):
    """Association between campaigns and display locations."""
    __tablename__ = "campaign_locations"
    __table_args__ = {"schema": "smartify"}
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    campaign_id: UUID = Field(foreign_key="smartify.campaign_configurations.campaign_id")
    display_id: str = Field(foreign_key="smartify.display_master.display_id")
    is_selected: bool = Field(default=True)
    match_score: float = Field(ge=0, le=100)
    budget_allocation: float
    custom_schedule: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    impressions_delivered: int = Field(default=0)
    added_date: datetime = Field(default_factory=datetime.now)
    removed_date: Optional[datetime] = None


class CampaignMetrics(SQLModel, table=True):
    """Store campaign performance metrics."""
    __tablename__ = "campaign_metrics"
    __table_args__ = {"schema": "smartify"}
    
    metric_id: UUID = Field(default_factory=uuid4, primary_key=True)
    campaign_id: UUID = Field(foreign_key="smartify.campaign_configurations.campaign_id")
    timestamp: datetime = Field(default_factory=datetime.now)
    impressions: int = Field(default=0)
    reach: int = Field(default=0)
    frequency: float = Field(default=0.0)
    clicks: int = Field(default=0)
    view_through_rate: float = Field(default=0.0)
    attention_score: float = Field(default=0.0)
    engagement_rate: float = Field(default=0.0)
    cost_per_thousand: float = Field(default=0.0)
    spend_hourly: float = Field(default=0.0)
    pacing_percentage: float = Field(default=0.0)
    
    # Additional performance metrics
    # click_through_rate: float = Field(default=0.0)
    # cost_per_click: float = Field(default=0.0)
    # conversion_count: int = Field(default=0)
    # conversion_rate: float = Field(default=0.0)
    # cost_per_acquisition: float = Field(default=0.0)
    # return_on_ad_spend: float = Field(default=0.0)
    
    # # Location-specific metrics (aggregated)
    # location_performance: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    # audience_breakdown: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))


class DisplayMaster(SQLModel, table=True):
    """Master table for display inventory."""
    __tablename__ = "display_master"
    __table_args__ = {"schema": "smartify"}
    
    display_id: str = Field(primary_key=True, max_length=50)
    display_name: str = Field(max_length=255)
    venue_name: str = Field(max_length=255)
    venue_type: str = Field(max_length=100)
    street_address: str = Field(max_length=500)
    city: str = Field(max_length=100)
    state: str = Field(max_length=50)
    zip_code: str = Field(max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    daily_impressions: int
    weekly_impressions: int
    price_per_week: float
    primary_image_url: Optional[str] = Field(max_length=500)
    screen_type: Optional[str] = Field(max_length=50)
    screen_size: Optional[str] = Field(max_length=50)
    resolution: Optional[str] = Field(max_length=50)
    operating_hours: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    demographics_profile: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class AgentConversation(SQLModel, table=True):
    """Store agent conversation history."""
    __tablename__ = "agent_conversations"
    __table_args__ = {"schema": "smartify"}
    
    conversation_id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: Optional[str] = Field(max_length=100)
    agent_type: str = Field(max_length=50)  # 'campaign_assistant' or 'performance_dashboard'
    user_query: str
    agent_response: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    context: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.now)
    