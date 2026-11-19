"""
NEXUS — Analytics and Reporting Models
=======================================
Database models for reports, schedules, subscriptions, and analytics configurations.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Report(Base):
    """Report definitions and configurations."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    report_type = Column(String)  # executive_summary, supply_chain_performance, etc.
    config = Column(JSON)  # Report configuration with sections, parameters, etc.
    created_by = Column(Integer, nullable=True)  # user_id
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)

    # Relationships
    schedules = relationship("ReportSchedule", back_populates="report", cascade="all, delete-orphan")
    subscriptions = relationship("ReportSubscription", back_populates="report", cascade="all, delete-orphan")
    executions = relationship("ReportExecution", back_populates="report", cascade="all, delete-orphan")


class ReportSchedule(Base):
    """Report scheduling configurations."""
    __tablename__ = "report_schedules"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String, unique=True, index=True)
    report_id = Column(String, ForeignKey("reports.report_id"), index=True)
    schedule_type = Column(String)  # cron, interval, manual
    schedule_expression = Column(String)  # cron expression or interval specification
    timezone = Column(String, default="UTC")
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    report = relationship("Report", back_populates="schedules")


class ReportSubscription(Base):
    """Report subscriptions for distribution."""
    __tablename__ = "report_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(String, unique=True, index=True)
    report_id = Column(String, ForeignKey("reports.report_id"), index=True)
    subscriber_email = Column(String, index=True)
    subscriber_name = Column(String, nullable=True)
    format = Column(String, default="pdf")  # pdf, html, excel, csv
    delivery_method = Column(String, default="email")  # email, webhook, s3
    delivery_config = Column(JSON, nullable=True)  # Delivery-specific configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    report = relationship("Report", back_populates="subscriptions")


class ReportExecution(Base):
    """Report execution history and results."""
    __tablename__ = "report_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, unique=True, index=True)
    report_id = Column(String, ForeignKey("reports.report_id"), index=True)
    schedule_id = Column(String, ForeignKey("report_schedules.schedule_id"), nullable=True)
    status = Column(String, index=True)  # pending, running, completed, failed
    started_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    parameters = Column(JSON, nullable=True)
    result_summary = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    output_format = Column(String, nullable=True)
    output_location = Column(String, nullable=True)
    row_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # Relationships
    report = relationship("Report", back_populates="executions")


class Dashboard(Base):
    """Dashboard configurations for analytics visualization."""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    config = Column(JSON)  # Dashboard layout, widgets, filters
    created_by = Column(Integer, nullable=True)  # user_id
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)


class Widget(Base):
    """Widget definitions for dashboards."""
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(String, unique=True, index=True)
    dashboard_id = Column(String, ForeignKey("dashboards.dashboard_id"), nullable=True)
    widget_type = Column(String)  # chart, kpi, table, map, etc.
    config = Column(JSON)  # Widget-specific configuration
    data_source = Column(JSON, nullable=True)  # Data source configuration
    position = Column(JSON, nullable=True)  # Position and size on dashboard
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    is_active = Column(Boolean, default=True)


class AnalyticsConfig(Base):
    """Analytics engine configurations."""
    __tablename__ = "analytics_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(String, unique=True, index=True)
    config_name = Column(String, index=True)
    config_type = Column(String)  # trend_analysis, correlation_analysis, outlier_detection
    parameters = Column(JSON)  # Analysis parameters
    default_values = Column(JSON, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    is_active = Column(Boolean, default=True)


class DataVisualization(Base):
    """Saved visualization configurations."""
    __tablename__ = "data_visualizations"

    id = Column(Integer, primary_key=True, index=True)
    visualization_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    chart_type = Column(String)  # line, bar, scatter, heatmap, etc.
    data_query = Column(Text, nullable=True)
    config = Column(JSON)  # Chart configuration
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    is_active = Column(Boolean, default=True)


class AlertRule(Base):
    """Alert rules for automated monitoring and reporting."""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String, unique=True, index=True)
    rule_name = Column(String, index=True)
    description = Column(Text, nullable=True)
    metric = Column(String)  # KPI or metric to monitor
    condition = Column(String)  # >, <, =, !=, contains, etc.
    threshold = Column(Float)
    severity = Column(String)  # info, warning, error, critical
    notification_config = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class ReportTemplate(Base):
    """Report templates for self-service reporting."""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # executive, operational, financial, etc.
    template_config = Column(JSON)  # Template structure and default parameters
    is_system_template = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    is_active = Column(Boolean, default=True)
