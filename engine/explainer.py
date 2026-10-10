"""
TransitPulse AI - AI-Assisted Explanation Engine
Transforms deterministic exception metrics into structured, evidence-backed
operational briefings. Follows strict governance rules:
- Clear separation between observed factual data and causal hypotheses
- Explanations grounded directly in corroborating telemetry
- Actionable operational recommendations
- 100% Offline Rule-Based Engine + Optional Gemini API enhancement
"""

import os
from typing import List, Dict, Any, Optional
from engine.detector import TransitException

class ExplainedException:
    def __init__(
        self,
        exception: TransitException,
        title: str,
        observation: str,
        possible_explanations: List[str],
        evidence_points: List[str],
        recommended_action: str,
        uncertainty_statement: str
    ):
        self.raw = exception
        self.title = title
        self.observation = observation
        self.possible_explanations = possible_explanations
        self.evidence_points = evidence_points
        self.recommended_action = recommended_action
        self.uncertainty_statement = uncertainty_statement

    def to_dict(self):
        return {
            "id": self.raw.id,
            "operator": self.raw.operator,
            "scope": self.raw.scope,
            "severity": self.raw.severity,
            "metric": self.raw.metric_name,
            "title": self.title,
            "observation": self.observation,
            "possible_explanations": self.possible_explanations,
            "evidence_points": self.evidence_points,
            "recommended_action": self.recommended_action,
            "uncertainty_statement": self.uncertainty_statement,
            "current_val": self.raw.current_val,
            "baseline_val": self.raw.baseline_val,
            "pct_change": self.raw.pct_change,
            "unit": self.raw.unit_str
        }

class AIExplainerEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")

    def explain_exception(self, ex: TransitException) -> ExplainedException:
        """
        Generates structured, evidence-backed explanation for a single exception.
        Uses deterministic intelligence with domain-specific transit rules.
        """
        op = ex.operator
        metric = ex.metric_name
        cur = ex.current_val
        base = ex.baseline_val
        pct = ex.pct_change
        scope = ex.scope
        unit = ex.unit_str
        corr = ex.corroborating_facts

        # 1. Title Generation
        direction = "Decline" if (pct and pct < 0) else "Spike" if (pct and pct > 0) else "Anomaly"
        title = f"{op}: Significant {direction} in {metric} ({scope})"
        
        # 2. Precise Observation Statement
        unit_formatted = f" {unit}" if unit else ""
        if base is not None:
            direction_word = "declined" if (pct and pct < 0) else "increased"
            observation = (
                f"Recorded {metric.lower()} on {scope} reached {cur:,.1f}{unit_formatted}, "
                f"representing a {abs(pct):.1f}% {direction_word} compared to the "
                f"{ex.baseline_method.lower()} of {base:,.1f}{unit_formatted} "
                f"(absolute delta: {ex.abs_change:+,.1f}{unit_formatted})."
            )
        else:
            observation = f"Observed {metric.lower()} of {cur:,.1f}{unit_formatted} on {scope} crossed operational tolerance."

        # 3. Formulate Evidence & Corroborating Signals
        evidence_points = []
        possible_explanations = []
        recommended_action = ""
        uncertainty = "High confidence in recorded telemetry; causal hypotheses require field verification."

        if "Ridership" in metric:
            if pct and pct < 0:
                evidence_points.append(
                    f"Ridership deficit of {abs(ex.abs_change):,.0f} passengers relative to baseline period."
                )
                if "corridor_delay" in corr and corr["corridor_delay"] != "N/A":
                    evidence_points.append(f"Concurrent corridor average delay reached {corr['corridor_delay']} min.")
                if "completed_trips" in corr and "scheduled_trips" in corr and corr["scheduled_trips"] != "N/A":
                    lost_trips = corr["scheduled_trips"] - corr["completed_trips"]
                    if lost_trips > 0:
                        evidence_points.append(f"Trip completion deficit of {lost_trips} cancelled/undelivered services.")

                possible_explanations = [
                    f"Hypothesis A: Infrastructure impediment or signaling delay led to passenger diversion to parallel modes.",
                    f"Hypothesis B: Localized corridor blockage, road repair, or event-driven travel pattern shifting.",
                    f"Hypothesis C: Fare collection gate telemetry latency or incomplete turnstile sync."
                ]
                recommended_action = (
                    f"Dispatch field supervisor to verify {scope} platform passenger loading and coordinate with "
                    f"{op} operations center to audit ticket turnstile timestamp logs."
                )
            else:
                evidence_points.append(f"Passenger surplus of {ex.abs_change:,.0f} riders.")
                possible_explanations = [
                    "Hypothesis A: Special city event, exhibition, or convention along transit corridor.",
                    "Hypothesis B: Modal shift from disrupted parallel transit routes."
                ]
                recommended_action = f"Review platform crowd management and verify headway adequacy on {scope}."

        elif "Service Availability" in metric:
            sched = corr.get("scheduled_trips", "N/A")
            comp = corr.get("completed_trips", "N/A")
            canc = corr.get("cancelled_trips", "N/A")
            evidence_points.append(f"Delivered {comp} out of {sched} scheduled trips ({cur:.1f}% delivery rate).")
            evidence_points.append(f"{canc} scheduled services remained unfulfilled.")
            
            if op == "Metro":
                possible_explanations = [
                    "Hypothesis A: Rolling stock propulsion or overhead traction power trip.",
                    "Hypothesis B: Automated train supervision (ATS) interlocking fail-safe reset."
                ]
                recommended_action = "Request traction power dispatch log from GMRC Operations Control Center (OCC)."
            else:
                possible_explanations = [
                    "Hypothesis A: Depot maintenance backlog or fleet rollout mechanical failure.",
                    "Hypothesis B: Crew absenteeism or shift changeover bottlenecks at terminal depots."
                ]
                recommended_action = f"Audit {op} terminal depot rollout sheets and inspect mechanic duty logs."

        elif "Delay" in metric:
            evidence_points.append(f"Average transit delay reached {cur:.1f} min vs normal baseline of {base:.1f} min.")
            if "delay_inflation_minutes" in corr:
                evidence_points.append(f"Delay inflation of +{corr['delay_inflation_minutes']:.1f} minutes above tolerance.")
            
            if op == "Metro":
                possible_explanations = [
                    "Hypothesis A: Speed restriction imposed due to track circuit or signaling communication jitter.",
                    "Hypothesis B: Prolonged station dwell time caused by door obstruction or medical emergency."
                ]
                recommended_action = "Review ATS line headway report and verify if speed restrictions remain in place."
            elif op == "BRTS":
                possible_explanations = [
                    "Hypothesis A: Mixed traffic lane encroachment at key corridor intersections.",
                    "Hypothesis B: Dedicated bus lane blockage (construction, broken-down feeder vehicle, or utility work)."
                ]
                recommended_action = "Contact Ahmedabad Traffic Police & Janmarg control room to clear lane obstructions."
            else:
                possible_explanations = [
                    "Hypothesis A: Severe arterial road congestion along mixed-traffic bus routes.",
                    "Hypothesis B: Road works, monsoon waterlogging, or festival processions along the route."
                ]
                recommended_action = "Coordinate with traffic management team for temporary lane priority or route bypass."

        else:
            evidence_points.append(f"Metric value {cur} deviates by {pct:.1f}% from expected standard {base}.")
            possible_explanations = [
                "Hypothesis A: Transient operational variance requiring supervisory monitoring.",
                "Hypothesis B: Sensor reporting delay or intermediate data processing sync lag."
            ]
            recommended_action = f"Monitor next scheduled telemetry feed and verify reporting integrity for {scope}."

        return ExplainedException(
            exception=ex,
            title=title,
            observation=observation,
            possible_explanations=possible_explanations,
            evidence_points=evidence_points,
            recommended_action=recommended_action,
            uncertainty_statement=uncertainty
        )

    def generate_morning_brief(
        self,
        date_str: str,
        citywide_metrics: Dict[str, Any],
        operator_metrics: Dict[str, Dict[str, Any]],
        explained_exceptions: List[ExplainedException]
    ) -> Dict[str, Any]:
        """
        Synthesizes the complete 'Two-Minute Morning Brief' for senior transit management.
        """
        crit_count = sum(1 for e in explained_exceptions if e.raw.severity == "CRITICAL")
        warn_count = sum(1 for e in explained_exceptions if e.raw.severity == "WARNING")
        
        # Calculate transit health index (0 to 100)
        base_score = 98.0
        base_score -= (crit_count * 12.0)
        base_score -= (warn_count * 4.0)
        overall_health_score = max(45.0, min(100.0, base_score))
        
        status_label = "HEALTHY / NOMINAL" if overall_health_score >= 90 else (
            "ATTENTION REQUIRED" if overall_health_score >= 75 else "ELEVATED OPERATIONAL DISTRESS"
        )
        
        # Executive Summary Narrative
        tot_riders = citywide_metrics.get("total_ridership", 0)
        network_avail = citywide_metrics.get("network_availability_pct", 0)
        avg_delay = citywide_metrics.get("citywide_avg_delay_minutes", 0)
        
        exec_narrative = (
            f"On {date_str}, citywide public transit across Metro, BRTS, and AMTS recorded "
            f"{int(tot_riders):,} passengers with an aggregate network availability rate of {network_avail:.1f}% "
            f"and an average delay of {avg_delay:.1f} minutes. "
        )
        
        if crit_count > 0:
            crit_ops = list(set(e.raw.operator for e in explained_exceptions if e.raw.severity == "CRITICAL"))
            exec_narrative += (
                f"Management attention is urgently required on {', '.join(crit_ops)} due to {crit_count} "
                f"critical operational exception(s) involving severe schedule deviations and ridership disruptions. "
            )
        elif warn_count > 0:
            exec_narrative += (
                f"All three networks operated within broad tolerance, though {warn_count} operational warnings "
                f"warrant monitoring during morning operational briefings."
            )
        else:
            exec_narrative += "All systems operated within nominal baseline parameters with no significant exceptions detected."

        # Top 3 Action Items
        action_items = []
        for i, ex in enumerate(explained_exceptions[:3], 1):
            action_items.append({
                "priority": f"Priority {i} ({ex.raw.severity})",
                "target": f"{ex.raw.operator} - {ex.raw.scope}",
                "action": ex.recommended_action
            })

        return {
            "report_date": date_str,
            "overall_health_score": overall_health_score,
            "status_label": status_label,
            "critical_exceptions_count": crit_count,
            "warning_exceptions_count": warn_count,
            "executive_narrative": exec_narrative,
            "top_actions": action_items,
            "citywide_metrics": citywide_metrics,
            "operator_metrics": operator_metrics,
            "detailed_exceptions": [e.to_dict() for e in explained_exceptions]
        }
