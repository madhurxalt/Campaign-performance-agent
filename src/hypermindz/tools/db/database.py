"""Database connection and session management."""

import os
from typing import Optional, Generator
from contextlib import contextmanager
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import NullPool
import logging
from sqlalchemy import text
from dotenv import load_dotenv
# from .models import (
#     CampaignConfiguration,
#     CampaignLocation, 
#     CampaignMetrics,
#     DisplayMaster,
#     AgentConversation
# )

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database connections and sessions."""
    
    def __init__(self, database_url: Optional[str] = None):
        load_dotenv()
        # print(f"Database URL: {database_url or os.getenv('DATABASE_URL')}")
        """Initialize database manager."""
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://localhost/smartify_campaign"
        )
        
        print(f"Using Database URL: {self.database_url}")
        # Create engine with NullPool for better connection management
        self.engine = create_engine(
            self.database_url,
            poolclass=NullPool,
            echo=False,
            # connect_args={
            #     "options": "-c search_path=smartify,public"
            # }
        )
        
    def create_tables(self):
        """Create all tables if they don't exist."""
        try:
            SQLModel.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
            
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session as a context manager."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
            print("its wokrinig now !")
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
            
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_session() as session:
                session.exec(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False


# # Global database manager instance
# db_manager = DatabaseManager()
# # db_manager.get_session()  # Initialize session to test connection
# # db_manager.create_tables()  # Ensure tables are created
# from typing import List
# from datetime import datetime
# from sqlmodel import select, and_
# import json
# from models import CampaignMetrics, CampaignConfiguration

# def query_campaign_metrics(
#     campaign_id: Optional[str] = None,
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     metrics: Optional[List[str]] = None
# ) -> str:
#     """
#     Query performance metrics for a specific campaign or all campaigns.
    
#     Args:
#         campaign_id: UUID of specific campaign (optional)
#         start_date: Start date for metrics in YYYY-MM-DD format (optional)
#         end_date: End date for metrics in YYYY-MM-DD format (optional)
#         metrics: List of specific metrics to retrieve (optional)
    
#     Returns:
#         JSON string with campaign metrics data
#     """
#     with db_manager.get_session() as session:
#         # Build base query
#         query = select(CampaignMetrics, CampaignConfiguration).join(
#             CampaignConfiguration,
#             CampaignMetrics.campaign_id == CampaignConfiguration.campaign_id
#         )
        
#         # Apply filters
#         filters = []
        
#         if campaign_id:
#             filters.append(CampaignMetrics.campaign_id == campaign_id)
        
#         if start_date:
#             start_dt = datetime.strptime(start_date, "%Y-%m-%d")
#             filters.append(CampaignMetrics.timestamp >= start_dt)
        
#         if end_date:
#             end_dt = datetime.strptime(end_date, "%Y-%m-%d")
#             filters.append(CampaignMetrics.timestamp <= end_dt)
        
#         if filters:
#             query = query.where(and_(*filters))
        
#         # Execute query
#         results = session.exec(query).all()
        
#         # Format results
#         metrics_data = []
#         for metric, config in results:
#             data = {
#                 "campaign_id": str(metric.campaign_id),
#                 "campaign_name": config.campaign_name,
#                 "timestamp": metric.timestamp.isoformat(),
#                 "impressions": metric.impressions,
#                 "clicks": metric.clicks,
#                 "reach": metric.reach,
#                 "frequency": metric.frequency,
#                 # "ctr": metric.click_through_rate,
#                 "engagement_rate": metric.engagement_rate,
#                 "spend": metric.spend_hourly,
#                 "cpm": metric.cost_per_thousand,
#                 # "conversions": metric.conversion_count,
#                 # "conversion_rate": metric.conversion_rate,
#                 # "cpa": metric.cost_per_acquisition,
#                 # "roas": metric.return_on_ad_spend
#             }
            
#             # Filter metrics if specified
#             if metrics:
#                 data = {k: v for k, v in data.items() if k in metrics or k in ["campaign_id", "campaign_name", "timestamp"]}
            
#             metrics_data.append(data)
        
#         return json.dumps({"metrics": metrics_data, "count": len(metrics_data)}, indent=2)

# result = query_campaign_metrics(campaign_id="123e4567-e89b-12d3-a456-426614174000", start_date="2023-01-01", end_date="2023-12-31", metrics=["impressions", "clicks"])
# print(result)