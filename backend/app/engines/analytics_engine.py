"""
NEXUS — Advanced Analytics and Reporting Engine
================================================
Comprehensive analytics framework with trend analysis, correlation analysis,
self-service reporting, scheduled reports, and advanced visualization.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from scipy import stats
from scipy.signal import find_peaks
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json

logger_analytics = logging.getLogger("nexus.analytics_engine")


class AnalyticsEngine:
    """
    Enterprise analytics engine with advanced statistical analysis,
    reporting framework, and self-service capabilities.
    """

    def __init__(self):
        self.report_templates = {}
        self.scheduled_reports = {}
        self.report_subscriptions = {}
        self._initialised = False

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize the analytics engine with configuration.
        
        Args:
            config: Configuration dict with reporting settings
        """
        try:
            default_config = {
                "reporting": {
                    "default_format": "pdf",
                    "max_report_size_mb": 50,
                    "retention_days": 90,
                    "enable_scheduling": True,
                    "enable_subscriptions": True
                },
                "analytics": {
                    "trend_window_days": 30,
                    "correlation_threshold": 0.7,
                    "outlier_detection_method": "isolation_forest",
                    "confidence_level": 0.95
                },
                "visualization": {
                    "default_chart_type": "line",
                    "color_palette": "viridis",
                    "enable_interactive": True
                }
            }
            
            self.config = config or default_config
            self._initialised = True
            
            # Load default report templates
            self._load_default_templates()
            
            return {
                "status": "success",
                "templates_loaded": len(self.report_templates),
                "initialised_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_analytics.error(f"Error initializing analytics engine: {e}")
            return {"error": str(e), "initialised": False}

    def _load_default_templates(self):
        """Load default report templates."""
        self.report_templates = {
            "executive_summary": {
                "name": "Executive Summary",
                "description": "High-level KPI dashboard for executives",
                "sections": ["kpi_overview", "trend_analysis", "risk_summary"],
                "default_schedule": "weekly",
                "formats": ["pdf", "html"]
            },
            "supply_chain_performance": {
                "name": "Supply Chain Performance",
                "description": "Detailed supply chain metrics and analysis",
                "sections": ["otif_analysis", "inventory_metrics", "supplier_performance"],
                "default_schedule": "monthly",
                "formats": ["pdf", "excel", "html"]
            },
            "demand_forecast_accuracy": {
                "name": "Demand Forecast Accuracy",
                "description": "Forecast accuracy analysis and improvement recommendations",
                "sections": ["accuracy_metrics", "bias_analysis", "mape_trends"],
                "default_schedule": "weekly",
                "formats": ["pdf", "excel"]
            },
            "inventory_optimization": {
                "name": "Inventory Optimization Report",
                "description": "Inventory levels, turnover, and optimization recommendations",
                "sections": ["inventory_levels", "turnover_analysis", "optimization_opportunities"],
                "default_schedule": "monthly",
                "formats": ["pdf", "excel"]
            }
        }

    def trend_analysis(self, data: pd.DataFrame, 
                      date_column: str,
                      value_columns: List[str],
                      window_size: int = 7) -> Dict[str, Any]:
        """
        Perform advanced trend analysis with multiple statistical methods.
        
        Args:
            data: Input data with date and value columns
            date_column: Name of date column
            value_columns: List of value columns to analyze
            window_size: Window size for moving averages
        """
        try:
            if date_column not in data.columns:
                return {"error": f"Date column '{date_column}' not found"}
            
            # Ensure date column is datetime
            data[date_column] = pd.to_datetime(data[date_column])
            data = data.sort_values(date_column)
            
            trend_results = {}
            
            for column in value_columns:
                if column not in data.columns:
                    continue
                
                values = data[column].dropna()
                if len(values) < 3:
                    trend_results[column] = {"error": "Insufficient data points"}
                    continue
                
                # Linear trend analysis
                x = np.arange(len(values))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                
                # Moving averages
                ma_short = values.rolling(window=min(window_size, len(values))).mean()
                ma_long = values.rolling(window=min(window_size*2, len(values))).mean()
                
                # Exponential smoothing
                alpha = 0.3
                exp_smooth = values.ewm(alpha=alpha).mean()
                
                # Seasonal decomposition (simplified)
                if len(values) >= 12:
                    # Simple seasonal detection using autocorrelation
                    seasonal_strength = self._detect_seasonality(values)
                else:
                    seasonal_strength = 0.0
                
                # Trend strength classification
                trend_strength = self._classify_trend(slope, p_value, r_value)
                
                # Change point detection
                change_points = self._detect_change_points(values)
                
                # Forecast next period (simple linear projection)
                next_period_forecast = intercept + slope * (len(values) + 1)
                
                trend_results[column] = {
                    "trend_slope": round(slope, 4),
                    "trend_intercept": round(intercept, 4),
                    "r_squared": round(r_value**2, 4),
                    "p_value": round(p_value, 6),
                    "trend_strength": trend_strength,
                    "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                    "seasonal_strength": round(seasonal_strength, 3),
                    "moving_average_short": ma_short.iloc[-1] if len(ma_short) > 0 else None,
                    "moving_average_long": ma_long.iloc[-1] if len(ma_long) > 0 else None,
                    "exponential_smooth": exp_smooth.iloc[-1] if len(exp_smooth) > 0 else None,
                    "change_points": change_points,
                    "next_period_forecast": round(next_period_forecast, 2),
                    "current_value": round(values.iloc[-1], 2),
                    "percent_change": round(((values.iloc[-1] - values.iloc[0]) / values.iloc[0] * 100) if values.iloc[0] != 0 else 0, 2),
                    "volatility": round(values.std() / (values.mean() + 1e-8), 3)
                }
            
            return {
                "status": "success",
                "trend_analysis": trend_results,
                "analyzed_columns": list(trend_results.keys()),
                "analysis_period": {
                    "start": data[date_column].min().isoformat(),
                    "end": data[date_column].max().isoformat(),
                    "total_periods": len(data)
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_analytics.error(f"Error in trend analysis: {e}")
            return {"error": str(e)}

    def _detect_seasonality(self, values: pd.Series) -> float:
        """Detect seasonal patterns using autocorrelation."""
        try:
            if len(values) < 12:
                return 0.0
            
            # Calculate autocorrelation at different lags
            max_correlation = 0
            for lag in [7, 30, 90]:  # Weekly, monthly, quarterly
                if len(values) > lag * 2:
                    correlation = abs(values.autocorr(lag=lag))
                    if correlation > max_correlation:
                        max_correlation = correlation
            
            return max_correlation
        except:
            return 0.0

    def _classify_trend(self, slope: float, p_value: float, r_squared: float) -> str:
        """Classify trend strength based on statistical significance."""
        if p_value > 0.05:
            return "not_significant"
        elif abs(slope) < 0.01:
            return "weak"
        elif abs(slope) < 0.1:
            return "moderate"
        else:
            return "strong"

    def _detect_change_points(self, values: pd.Series) -> List[Dict[str, Any]]:
        """Detect significant change points in the data."""
        try:
            change_points = []
            if len(values) < 10:
                return change_points
            
            # Simple change point detection using mean shifts
            values_array = values.values
            mean_overall = np.mean(values_array)
            std_overall = np.std(values_array)
            
            for i in range(5, len(values_array) - 5):
                window_before = values_array[i-5:i]
                window_after = values_array[i:i+5]
                
                mean_before = np.mean(window_before)
                mean_after = np.mean(window_after)
                
                # If the means differ by more than 1 standard deviation
                if abs(mean_after - mean_before) > std_overall:
                    change_points.append({
                        "index": i,
                        "value": round(values_array[i], 2),
                        "mean_before": round(mean_before, 2),
                        "mean_after": round(mean_after, 2),
                        "change_magnitude": round(abs(mean_after - mean_before), 2)
                    })
            
            # Return top 5 most significant change points
            change_points.sort(key=lambda x: x["change_magnitude"], reverse=True)
            return change_points[:5]
            
        except Exception as e:
            logger_analytics.error(f"Error detecting change points: {e}")
            return []

    def correlation_analysis(self, data: pd.DataFrame,
                           method: str = "pearson",
                           threshold: float = 0.7) -> Dict[str, Any]:
        """
        Perform correlation analysis with statistical significance testing.
        
        Args:
            data: Input data with numeric columns
            method: Correlation method (pearson, spearman, kendall)
            threshold: Minimum correlation coefficient to report
        """
        try:
            # Select only numeric columns
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return {"error": "No numeric columns found"}
            
            # Calculate correlation matrix
            if method == "pearson":
                corr_matrix = numeric_data.corr(method='pearson')
            elif method == "spearman":
                corr_matrix = numeric_data.corr(method='spearman')
            elif method == "kendall":
                corr_matrix = numeric_data.corr(method='kendall')
            else:
                return {"error": f"Unknown correlation method: {method}"}
            
            # Find significant correlations
            significant_correlations = []
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    
                    if abs(corr_value) >= threshold and not pd.isna(corr_value):
                        # Calculate p-value for Pearson correlation
                        if method == "pearson" and len(numeric_data) > 3:
                            n = len(numeric_data)
                            t_stat = corr_value * np.sqrt((n-2) / (1 - corr_value**2))
                            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n-2))
                        else:
                            p_value = None
                        
                        significant_correlations.append({
                            "variable_1": col1,
                            "variable_2": col2,
                            "correlation_coefficient": round(corr_value, 4),
                            "correlation_strength": self._classify_correlation(abs(corr_value)),
                            "p_value": round(p_value, 6) if p_value else None,
                            "significant": p_value < 0.05 if p_value else None
                        })
            
            # Sort by absolute correlation value
            significant_correlations.sort(key=lambda x: abs(x["correlation_coefficient"]), reverse=True)
            
            return {
                "status": "success",
                "correlation_method": method,
                "threshold": threshold,
                "significant_correlations": significant_correlations,
                "total_correlations_found": len(significant_correlations),
                "correlation_matrix": corr_matrix.round(4).to_dict(),
                "analyzed_columns": list(numeric_data.columns),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_analytics.error(f"Error in correlation analysis: {e}")
            return {"error": str(e)}

    def _classify_correlation(self, corr_value: float) -> str:
        """Classify correlation strength."""
        if corr_value >= 0.9:
            return "very_strong"
        elif corr_value >= 0.7:
            return "strong"
        elif corr_value >= 0.5:
            return "moderate"
        elif corr_value >= 0.3:
            return "weak"
        else:
            return "very_weak"

    def outlier_detection(self, data: pd.DataFrame,
                         columns: List[str],
                         method: str = "isolation_forest",
                         contamination: float = 0.1) -> Dict[str, Any]:
        """
        Detect outliers using multiple statistical methods.
        
        Args:
            data: Input data
            columns: Columns to analyze for outliers
            method: Detection method (isolation_forest, zscore, iqr)
            contamination: Expected proportion of outliers
        """
        try:
            outlier_results = {}
            
            for column in columns:
                if column not in data.columns:
                    continue
                
                values = data[column].dropna()
                if len(values) < 10:
                    outlier_results[column] = {"error": "Insufficient data"}
                    continue
                
                outliers = []
                outlier_indices = []
                
                if method == "isolation_forest":
                    # Use Isolation Forest for outlier detection
                    clf = IsolationForest(contamination=contamination, random_state=42)
                    values_reshaped = values.values.reshape(-1, 1)
                    outlier_labels = clf.fit_predict(values_reshaped)
                    
                    outlier_indices = [i for i, label in enumerate(outlier_labels) if label == -1]
                    outlier_values = values.iloc[outlier_indices]
                    
                    for idx, val in zip(outlier_indices, outlier_values):
                        outliers.append({
                            "index": int(idx),
                            "value": round(val, 2),
                            "outlier_score": round(clf.score_samples([[val]])[0], 4)
                        })
                
                elif method == "zscore":
                    # Z-score method
                    z_scores = np.abs(stats.zscore(values))
                    threshold = 3
                    outlier_indices = np.where(z_scores > threshold)[0]
                    
                    for idx in outlier_indices:
                        outliers.append({
                            "index": int(idx),
                            "value": round(values.iloc[idx], 2),
                            "z_score": round(z_scores[idx], 4)
                        })
                
                elif method == "iqr":
                    # Interquartile Range method
                    Q1 = values.quantile(0.25)
                    Q3 = values.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outlier_mask = (values < lower_bound) | (values > upper_bound)
                    outlier_indices = np.where(outlier_mask)[0]
                    
                    for idx in outlier_indices:
                        outliers.append({
                            "index": int(idx),
                            "value": round(values.iloc[idx], 2),
                            "lower_bound": round(lower_bound, 2),
                            "upper_bound": round(upper_bound, 2)
                        })
                
                outlier_results[column] = {
                    "method": method,
                    "total_outliers": len(outliers),
                    "outlier_percentage": round(len(outliers) / len(values) * 100, 2),
                    "outliers": outliers[:20],  # Limit to top 20
                    "statistics": {
                        "mean": round(values.mean(), 2),
                        "std": round(values.std(), 2),
                        "min": round(values.min(), 2),
                        "max": round(values.max(), 2),
                        "median": round(values.median(), 2)
                    }
                }
            
            return {
                "status": "success",
                "outlier_analysis": outlier_results,
                "method_used": method,
                "analyzed_columns": list(outlier_results.keys()),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_analytics.error(f"Error in outlier detection: {e}")
            return {"error": str(e)}

    def create_report(self, report_config: Dict[str, Any],
                     data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create a comprehensive report based on configuration.
        
        Args:
            report_config: Report configuration with sections, format, etc.
            data: Data to analyze for the report
        """
        try:
            report_id = f"RPT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            report_sections = []
            
            # Process each section in the report
            for section in report_config.get("sections", []):
                section_type = section.get("type")
                section_result = self._generate_report_section(section_type, section, data)
                report_sections.append(section_result)
            
            # Generate report metadata
            report_metadata = {
                "report_id": report_id,
                "title": report_config.get("title", "Analytics Report"),
                "description": report_config.get("description", ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "data_summary": {
                    "total_rows": len(data),
                    "total_columns": len(data.columns),
                    "date_range": self._get_date_range(data)
                },
                "sections": report_sections
            }
            
            return {
                "status": "success",
                "report": report_metadata,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger_analytics.error(f"Error creating report: {e}")
            return {"error": str(e)}

    def _generate_report_section(self, section_type: str, 
                               section_config: Dict[str, Any],
                               data: pd.DataFrame) -> Dict[str, Any]:
        """Generate a specific section of the report."""
        try:
            if section_type == "kpi_overview":
                return self._generate_kpi_section(section_config, data)
            elif section_type == "trend_analysis":
                return self._generate_trend_section(section_config, data)
            elif section_type == "correlation_analysis":
                return self._generate_correlation_section(section_config, data)
            elif section_type == "outlier_analysis":
                return self._generate_outlier_section(section_config, data)
            elif section_type == "summary_statistics":
                return self._generate_summary_section(section_config, data)
            else:
                return {"error": f"Unknown section type: {section_type}"}
        except Exception as e:
            logger_analytics.error(f"Error generating section {section_type}: {e}")
            return {"error": str(e)}

    def _generate_kpi_section(self, config: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Generate KPI overview section."""
        kpis = []
        
        for kpi_config in config.get("kpis", []):
            column = kpi_config.get("column")
            aggregation = kpi_config.get("aggregation", "sum")
            
            if column not in data.columns:
                continue
            
            if aggregation == "sum":
                value = data[column].sum()
            elif aggregation == "mean":
                value = data[column].mean()
            elif aggregation == "count":
                value = data[column].count()
            elif aggregation == "min":
                value = data[column].min()
            elif aggregation == "max":
                value = data[column].max()
            else:
                value = data[column].sum()
            
            kpis.append({
                "name": kpi_config.get("name", column),
                "value": round(value, 2),
                "unit": kpi_config.get("unit", ""),
                "target": kpi_config.get("target"),
                "format": kpi_config.get("format", "number")
            })
        
        return {
            "type": "kpi_overview",
            "title": config.get("title", "KPI Overview"),
            "kpis": kpis
        }

    def _generate_trend_section(self, config: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Generate trend analysis section."""
        date_column = config.get("date_column")
        value_columns = config.get("value_columns", [])
        
        if not date_column or date_column not in data.columns:
            return {"error": "Invalid date column"}
        
        trend_result = self.trend_analysis(data, date_column, value_columns)
        
        return {
            "type": "trend_analysis",
            "title": config.get("title", "Trend Analysis"),
            "analysis": trend_result
        }

    def _generate_correlation_section(self, config: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Generate correlation analysis section."""
        method = config.get("method", "pearson")
        threshold = config.get("threshold", 0.7)
        
        correlation_result = self.correlation_analysis(data, method, threshold)
        
        return {
            "type": "correlation_analysis",
            "title": config.get("title", "Correlation Analysis"),
            "analysis": correlation_result
        }

    def _generate_outlier_section(self, config: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Generate outlier analysis section."""
        columns = config.get("columns", [])
        method = config.get("method", "isolation_forest")
        
        outlier_result = self.outlier_detection(data, columns, method)
        
        return {
            "type": "outlier_analysis",
            "title": config.get("title", "Outlier Analysis"),
            "analysis": outlier_result
        }

    def _generate_summary_section(self, config: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics section."""
        numeric_data = data.select_dtypes(include=[np.number])
        
        summary = {}
        for column in numeric_data.columns:
            summary[column] = {
                "count": int(numeric_data[column].count()),
                "mean": round(numeric_data[column].mean(), 2),
                "std": round(numeric_data[column].std(), 2),
                "min": round(numeric_data[column].min(), 2),
                "25%": round(numeric_data[column].quantile(0.25), 2),
                "50%": round(numeric_data[column].quantile(0.50), 2),
                "75%": round(numeric_data[column].quantile(0.75), 2),
                "max": round(numeric_data[column].max(), 2)
            }
        
        return {
            "type": "summary_statistics",
            "title": config.get("title", "Summary Statistics"),
            "statistics": summary
        }

    def _get_date_range(self, data: pd.DataFrame) -> Dict[str, str]:
        """Get date range from data if available."""
        date_columns = data.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            date_col = date_columns[0]
            return {
                "start": data[date_col].min().isoformat(),
                "end": data[date_col].max().isoformat()
            }
        return {}

    def schedule_report(self, report_config: Dict[str, Any],
                       schedule: str) -> Dict[str, Any]:
        """
        Schedule a report for automatic generation.
        
        Args:
            report_config: Report configuration
            schedule: Cron expression or schedule string
        """
        try:
            schedule_id = f"SCH-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            self.scheduled_reports[schedule_id] = {
                "schedule_id": schedule_id,
                "report_config": report_config,
                "schedule": schedule,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "next_run": self._calculate_next_run(schedule),
                "active": True
            }
            
            return {
                "status": "success",
                "schedule_id": schedule_id,
                "next_run": self.scheduled_reports[schedule_id]["next_run"],
                "message": "Report scheduled successfully"
            }
            
        except Exception as e:
            logger_analytics.error(f"Error scheduling report: {e}")
            return {"error": str(e)}

    def _calculate_next_run(self, schedule: str) -> str:
        """Calculate next run time based on schedule (simplified)."""
        # This is a simplified implementation
        # In production, use a proper cron parser
        if schedule == "daily":
            next_run = datetime.now(timezone.utc) + timedelta(days=1)
        elif schedule == "weekly":
            next_run = datetime.now(timezone.utc) + timedelta(weeks=1)
        elif schedule == "monthly":
            next_run = datetime.now(timezone.utc) + timedelta(days=30)
        else:
            next_run = datetime.now(timezone.utc) + timedelta(hours=1)
        
        return next_run.isoformat()

    def subscribe_to_report(self, report_id: str,
                          subscriber_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subscribe a user to receive report notifications.
        
        Args:
            report_id: ID of the report to subscribe to
            subscriber_config: Subscriber configuration (email, format, etc.)
        """
        try:
            subscription_id = f"SUB-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            if report_id not in self.report_subscriptions:
                self.report_subscriptions[report_id] = []
            
            subscription = {
                "subscription_id": subscription_id,
                "report_id": report_id,
                "subscriber_config": subscriber_config,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "active": True
            }
            
            self.report_subscriptions[report_id].append(subscription)
            
            return {
                "status": "success",
                "subscription_id": subscription_id,
                "message": "Subscription created successfully"
            }
            
        except Exception as e:
            logger_analytics.error(f"Error creating subscription: {e}")
            return {"error": str(e)}

    def get_visualization_config(self, chart_type: str,
                                data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate visualization configuration for advanced charts.
        
        Args:
            chart_type: Type of chart (line, bar, scatter, heatmap, etc.)
            data: Data to visualize
        """
        try:
            viz_config = {
                "chart_type": chart_type,
                "data_summary": {
                    "rows": len(data),
                    "columns": len(data.columns),
                    "numeric_columns": list(data.select_dtypes(include=[np.number]).columns),
                    "categorical_columns": list(data.select_dtypes(include=['object']).columns)
                },
                "recommended_configurations": []
            }
            
            # Generate recommendations based on data characteristics
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            if chart_type == "line":
                if len(numeric_cols) >= 1:
                    viz_config["recommended_configurations"].append({
                        "x_axis": "date",
                        "y_axis": numeric_cols[0],
                        "color": "blue",
                        "show_trend": True
                    })
            
            elif chart_type == "bar":
                if len(numeric_cols) >= 1:
                    cat_cols = data.select_dtypes(include=['object']).columns
                    if len(cat_cols) >= 1:
                        viz_config["recommended_configurations"].append({
                            "x_axis": cat_cols[0],
                            "y_axis": numeric_cols[0],
                            "orientation": "vertical"
                        })
            
            elif chart_type == "scatter":
                if len(numeric_cols) >= 2:
                    viz_config["recommended_configurations"].append({
                        "x_axis": numeric_cols[0],
                        "y_axis": numeric_cols[1],
                        "color": numeric_cols[2] if len(numeric_cols) >= 3 else None,
                        "size": None
                    })
            
            elif chart_type == "heatmap":
                corr_matrix = data[numeric_cols].corr()
                viz_config["correlation_matrix"] = corr_matrix.round(3).to_dict()
                viz_config["recommended_configurations"].append({
                    "color_scale": "viridis",
                    "show_values": True
                })
            
            return {
                "status": "success",
                "visualization_config": viz_config
            }
            
        except Exception as e:
            logger_analytics.error(f"Error generating visualization config: {e}")
            return {"error": str(e)}
