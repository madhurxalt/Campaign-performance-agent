"""Performance analytics tools for querying and analyzing campaign metrics."""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from sqlmodel import select, func, and_, or_, desc, asc
from crewai.tools import tool

from .db import DatabaseManager, CampaignMetrics, CampaignConfiguration, CampaignLocation, DisplayMaster


db_manager = DatabaseManager()

@tool("Query Campaign Metrics")
def query_campaign_metrics(
    campaign_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    metrics: Optional[List[str]] = None
) -> str:
    """
    Query performance metrics for a specific campaign or all campaigns.
    
    Args:
        campaign_id: UUID of specific campaign (optional)
        start_date: Start date for metrics in YYYY-MM-DD format (optional)
        end_date: End date for metrics in YYYY-MM-DD format (optional)
        metrics: List of specific metrics to retrieve (optional)
    
    Returns:
        JSON string with campaign metrics data
    """
    with db_manager.get_session() as session:
        # Build base query
        query = select(CampaignMetrics, CampaignConfiguration).join(
            CampaignConfiguration,
            CampaignMetrics.campaign_id == CampaignConfiguration.campaign_id
        )
        
        # Apply filters
        filters = []
        
        if campaign_id:
            filters.append(CampaignMetrics.campaign_id == campaign_id)
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            filters.append(CampaignMetrics.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            filters.append(CampaignMetrics.timestamp <= end_dt)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Execute query
        results = session.exec(query).all()
        
        # Format results
        metrics_data = []
        for metric, config in results:
            data = {
                "campaign_id": str(metric.campaign_id),
                "campaign_name": config.campaign_name,
                "timestamp": metric.timestamp.isoformat(),
                "impressions": metric.impressions,
                "clicks": metric.clicks,
                "reach": metric.reach,
                "frequency": metric.frequency,
                # "ctr": metric.click_through_rate,
                "engagement_rate": metric.engagement_rate,
                "spend": metric.spend_hourly,
                "cpm": metric.cost_per_thousand,
                # "conversions": metric.conversion_count,
                # "conversion_rate": metric.conversion_rate,
                # "cpa": metric.cost_per_acquisition,
                # "roas": metric.return_on_ad_spend
            }
            
            # Filter metrics if specified
            if metrics:
                data = {k: v for k, v in data.items() if k in metrics or k in ["campaign_id", "campaign_name", "timestamp"]}
            
            metrics_data.append(data)
        
        return json.dumps({"metrics": metrics_data, "count": len(metrics_data)}, indent=2)



@tool("Aggregate Performance Data")
def aggregate_performance_data(
    aggregation_type: str = "top_n",
    metric: str = "impressions",
    limit: int = 10,
    time_period: str = "last_7_days"
) -> str:
    """
    Get aggregated performance data for multiple campaigns.
    
    Args:
        aggregation_type: Type of aggregation (top_n, bottom_n, average, sum)
        metric: Metric to aggregate by (impressions, clicks, ctr, spend, roas, etc.)
        limit: Number of results to return
        time_period: Time period for analysis (today, yesterday, last_7_days, last_30_days, etc.)
    
    Returns:
        JSON string with aggregated campaign performance data
    """
    with db_manager.get_session() as session:
        # Calculate date range
        end_date = datetime.now()
        if time_period == "today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == "yesterday":
            start_date = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == "last_7_days":
            start_date = datetime.now() - timedelta(days=7)
        elif time_period == "last_30_days":
            start_date = datetime.now() - timedelta(days=30)
        elif time_period == "month_to_date":
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.now() - timedelta(days=7)
        
        # Build aggregation query
        metric_column_map = {
            "impressions": func.sum(CampaignMetrics.impressions),
            "clicks": func.sum(CampaignMetrics.clicks),
            "spend": func.sum(CampaignMetrics.spend_hourly),
            # "conversions": func.sum(CampaignMetrics.conversion_count),
            # "ctr": func.avg(CampaignMetrics.click_through_rate),
            "engagement_rate": func.avg(CampaignMetrics.engagement_rate),
            "cpm": func.avg(CampaignMetrics.cost_per_thousand),
            # "cpa": func.avg(CampaignMetrics.cost_per_acquisition),
            # "roas": func.avg(CampaignMetrics.return_on_ad_spend)
        }
        
        metric_column = metric_column_map.get(metric, func.sum(CampaignMetrics.impressions))
        
        query = (
            select(
                CampaignConfiguration.campaign_id,
                CampaignConfiguration.campaign_name,
                CampaignConfiguration.total_budget,
                metric_column.label(metric),
                func.sum(CampaignMetrics.impressions).label("total_impressions"),
                func.sum(CampaignMetrics.clicks).label("total_clicks"),
                func.sum(CampaignMetrics.spend_hourly).label("total_spend")
            )
            .join(CampaignMetrics, CampaignConfiguration.campaign_id == CampaignMetrics.campaign_id)
            .where(and_(
                CampaignMetrics.timestamp >= start_date,
                CampaignMetrics.timestamp <= end_date
            ))
            .group_by(
                CampaignConfiguration.campaign_id,
                CampaignConfiguration.campaign_name,
                CampaignConfiguration.total_budget
            )
        )
        
        # Apply sorting based on aggregation type
        if aggregation_type == "top_n":
            query = query.order_by(desc(metric_column))
        elif aggregation_type == "bottom_n":
            query = query.order_by(asc(metric_column))
        
        query = query.limit(limit)
        
        # Execute query
        results = session.exec(query).all()
        
        # Format results
        campaigns = []
        for row in results:
            campaign_data = {
                "campaign_id": str(row.campaign_id),
                "campaign_name": row.campaign_name,
                "total_budget": row.total_budget,
                metric: getattr(row, metric),
                "total_impressions": row.total_impressions,
                "total_clicks": row.total_clicks,
                "total_spend": row.total_spend,
                "ctr": (row.total_clicks / row.total_impressions * 100) if row.total_impressions > 0 else 0
            }
            campaigns.append(campaign_data)
        
        # Calculate overall aggregates
        if results:
            total_impressions = sum(c["total_impressions"] for c in campaigns)
            total_clicks = sum(c["total_clicks"] for c in campaigns)
            total_spend = sum(c["total_spend"] for c in campaigns)
            
            aggregated_metrics = {
                "total_campaigns": len(campaigns),
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_spend": total_spend,
                "avg_ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                "time_period": time_period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            }
        else:
            aggregated_metrics = {
                "total_campaigns": 0,
                "message": "No data found for the specified period"
            }
        
        return json.dumps({
            "campaigns": campaigns,
            "aggregated_metrics": aggregated_metrics,
            "aggregation_type": aggregation_type,
            "sorted_by": metric
        }, indent=2, default=str)


@tool("Calculate ROI Metrics")
def calculate_roi_metrics(
    campaign_ids: Optional[List[str]] = None,
    include_location_breakdown: bool = False
) -> str:
    """
    Calculate detailed ROI metrics for campaigns.
    
    Args:
        campaign_ids: List of campaign IDs to analyze (optional, analyzes all if not provided)
        include_location_breakdown: Whether to include location-level ROI breakdown
    
    Returns:
        JSON string with ROI analysis including ROAS, CPA, and profitability metrics
    """
    with db_manager.get_session() as session:
        # Build query for campaign metrics
        query = select(
            CampaignConfiguration,
            func.sum(CampaignMetrics.impressions).label("total_impressions"),
            func.sum(CampaignMetrics.clicks).label("total_clicks"),
            # func.sum(CampaignMetrics.conversion_count).label("total_conversions"),
            func.sum(CampaignMetrics.spend_hourly).label("total_spend"),
            # func.avg(CampaignMetrics.return_on_ad_spend).label("avg_roas"),
            # func.avg(CampaignMetrics.cost_per_acquisition).label("avg_cpa")
        ).join(
            CampaignMetrics,
            CampaignConfiguration.campaign_id == CampaignMetrics.campaign_id
        ).group_by(CampaignConfiguration.campaign_id)
        
        if campaign_ids:
            query = query.where(CampaignConfiguration.campaign_id.in_(campaign_ids))
        
        results = session.exec(query).all()
        
        roi_analysis = []
        for config, impressions, clicks, conversions, spend, roas, cpa in results:
            roi_data = {
                "campaign_id": str(config.campaign_id),
                "campaign_name": config.campaign_name,
                "budget": config.total_budget,
                "spend": spend or 0,
                "budget_utilization": ((spend or 0) / config.total_budget * 100) if config.total_budget > 0 else 0,
                "impressions": impressions or 0,
                "clicks": clicks or 0,
                "conversions": conversions or 0,
                "roas": roas or 0,
                "cpa": cpa or 0,
                "cpm": ((spend or 0) / (impressions or 1) * 1000) if impressions else 0,
                "ctr": ((clicks or 0) / (impressions or 1) * 100) if impressions else 0,
                "conversion_rate": ((conversions or 0) / (clicks or 1) * 100) if clicks else 0,
                "roi_percentage": ((roas or 0) - 1) * 100 if roas else -100,
                "profitability": "Profitable" if (roas or 0) > 1 else "Not Profitable"
            }
            
            # Add location breakdown if requested
            if include_location_breakdown:
                location_query = select(
                    CampaignLocation,
                    DisplayMaster
                ).join(
                    DisplayMaster,
                    CampaignLocation.display_id == DisplayMaster.display_id
                ).where(
                    CampaignLocation.campaign_id == config.campaign_id
                )
                
                # locations = session.exec(location_query).all()
            #     roi_data["location_performance"] = [
            #         {
            #             "display_id": loc.display_id,
            #             "venue_name": display.venue_name,
            #             "city": display.city,
            #             "budget_allocation": loc.budget_allocation,
            #             "impressions_delivered": loc.impressions_delivered
            #         }
            #         for loc, display in locations
            #     ]
            
            # roi_analysis.append(roi_data)
        
        # Calculate portfolio-level metrics
        if roi_analysis:
            total_spend = sum(c["spend"] for c in roi_analysis)
            total_budget = sum(c["budget"] for c in roi_analysis)
            avg_roas = sum(c["roas"] * c["spend"] for c in roi_analysis) / total_spend if total_spend > 0 else 0
            
            portfolio_metrics = {
                "total_campaigns": len(roi_analysis),
                "total_budget": total_budget,
                "total_spend": total_spend,
                "portfolio_roas": avg_roas,
                "portfolio_roi": (avg_roas - 1) * 100,
                "budget_efficiency": (total_spend / total_budget * 100) if total_budget > 0 else 0
            }
        else:
            portfolio_metrics = {"message": "No campaigns found for ROI analysis"}
        
        return json.dumps({
            "roi_analysis": roi_analysis,
            "portfolio_metrics": portfolio_metrics
        }, indent=2, default=str)


@tool("Compare Campaigns")
def compare_campaigns(
    campaign_ids: List[str],
    metrics: Optional[List[str]] = None
) -> str:
    """
    Compare performance metrics between multiple campaigns.
    
    Args:
        campaign_ids: List of campaign IDs to compare
        metrics: Specific metrics to compare (optional, uses default set if not provided)
    
    Returns:
        JSON string with side-by-side campaign comparison
    """
    if not metrics:
        metrics = ["impressions", "clicks", "ctr", "spend", "conversions", "cpa", "roas"]
    
    with db_manager.get_session() as session:
        comparison_data = []
        
        for campaign_id in campaign_ids:
            # Get campaign configuration
            config = session.exec(
                select(CampaignConfiguration).where(
                    CampaignConfiguration.campaign_id == campaign_id
                )
            ).first()
            
            if not config:
                continue
            
            # Get aggregated metrics
            metrics_result = session.exec(
                select(
                    func.sum(CampaignMetrics.impressions).label("impressions"),
                    func.sum(CampaignMetrics.clicks).label("clicks"),
                    # func.avg(CampaignMetrics.click_through_rate).label("ctr"),
                    func.sum(CampaignMetrics.spend_hourly).label("spend"),
                    # func.sum(CampaignMetrics.conversion_count).label("conversions"),
                    # func.avg(CampaignMetrics.cost_per_acquisition).label("cpa"),
                    # func.avg(CampaignMetrics.return_on_ad_spend).label("roas"),
                    func.avg(CampaignMetrics.engagement_rate).label("engagement_rate")
                ).where(
                    CampaignMetrics.campaign_id == campaign_id
                )
            ).first()
            
            campaign_data = {
                "campaign_id": str(campaign_id),
                "campaign_name": config.campaign_name,
                "budget": config.total_budget,
                "start_date": config.start_date.isoformat(),
                "end_date": config.end_date.isoformat()
            }
            
            # Add requested metrics
            for metric in metrics:
                campaign_data[metric] = getattr(metrics_result, metric, 0) or 0
            
            comparison_data.append(campaign_data)
        
        # Calculate relative performance
        if len(comparison_data) > 1:
            # Find best performer for each metric
            best_performers = {}
            for metric in metrics:
                if metric in ["cpa"]:  # Lower is better
                    best_value = min(c[metric] for c in comparison_data if c[metric] > 0)
                    best_campaign = next((c["campaign_name"] for c in comparison_data if c[metric] == best_value), None)
                else:  # Higher is better
                    best_value = max(c[metric] for c in comparison_data)
                    best_campaign = next((c["campaign_name"] for c in comparison_data if c[metric] == best_value), None)
                
                best_performers[metric] = {
                    "campaign": best_campaign,
                    "value": best_value
                }
        else:
            best_performers = {}
        
        return json.dumps({
            "comparison": comparison_data,
            "best_performers": best_performers,
            "metrics_compared": metrics
        }, indent=2, default=str)


@tool("Get Time Series Data")
def get_time_series_data(
    campaign_id: str,
    metric: str = "impressions",
    granularity: str = "daily"
) -> str:
    """
    Get performance metrics over time for trend analysis.
    
    Args:
        campaign_id: Campaign ID to analyze
        metric: Metric to track over time
        granularity: Time granularity (hourly, daily, weekly)
    
    Returns:
        JSON string with time series data for the specified metric
    """
    with db_manager.get_session() as session:
        # Determine grouping based on granularity
        if granularity == "hourly":
            date_group = func.date_trunc("hour", CampaignMetrics.timestamp)
        elif granularity == "weekly":
            date_group = func.date_trunc("week", CampaignMetrics.timestamp)
        else:  # daily
            date_group = func.date_trunc("day", CampaignMetrics.timestamp)
        
        # Map metric to column
        metric_columns = {
            "impressions": func.sum(CampaignMetrics.impressions),
            "clicks": func.sum(CampaignMetrics.clicks),
            "spend": func.sum(CampaignMetrics.spend_hourly),
            # "conversions": func.sum(CampaignMetrics.conversion_count),
            # "ctr": func.avg(CampaignMetrics.click_through_rate),
            "engagement_rate": func.avg(CampaignMetrics.engagement_rate),
            # "roas": func.avg(CampaignMetrics.return_on_ad_spend)
        }
        
        metric_column = metric_columns.get(metric, func.sum(CampaignMetrics.impressions))
        
        # Build and execute query
        query = (
            select(
                date_group.label("period"),
                metric_column.label("value")
            )
            .where(CampaignMetrics.campaign_id == campaign_id)
            .group_by(date_group)
            .order_by(date_group)
        )
        
        results = session.exec(query).all()
        
        # Format time series data
        time_series = [
            {
                "period": period.isoformat() if period else None,
                "value": value or 0
            }
            for period, value in results
        ]
        
        # Calculate trend
        if len(time_series) > 1:
            first_value = time_series[0]["value"]
            last_value = time_series[-1]["value"]
            if first_value > 0:
                trend_percentage = ((last_value - first_value) / first_value) * 100
                trend_direction = "increasing" if trend_percentage > 0 else "decreasing"
            else:
                trend_percentage = 0
                trend_direction = "stable"
        else:
            trend_percentage = 0
            trend_direction = "insufficient data"
        
        # Get campaign name
        config = session.exec(
            select(CampaignConfiguration).where(
                CampaignConfiguration.campaign_id == campaign_id
            )
        ).first()
        
        return json.dumps({
            "campaign_id": str(campaign_id),
            "campaign_name": config.campaign_name if config else "Unknown",
            "metric": metric,
            "granularity": granularity,
            "time_series": time_series,
            "trend": {
                "direction": trend_direction,
                "percentage_change": trend_percentage
            }
        }, indent=2, default=str)