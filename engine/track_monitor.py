"""
TransitPulse AI - GMRC Metro Track & Wayside Telemetry Engine
Monitors real-time / simulated track circuit status, CBTC signaling integrity,
750V DC third-rail traction power, and Temporary Speed Restrictions (TSR)
across Ahmedabad & Gandhinagar Metro corridors.
"""

from typing import Dict, List, Any, Optional
from config import GMRC_CORRIDORS, GMRC_TRACK_STATUSES

class TrackBlock:
    def __init__(
        self,
        block_id: str,
        line_key: str,
        from_station: str,
        to_station: str,
        length_km: float,
        status: str,  # CLEAR, OCCUPIED, SPEED_RESTRICTION, POWER_FAULT, MAINTENANCE_POSSESSION
        speed_limit_kmh: int,
        actual_speed_kmh: int,
        third_rail_voltage_v: float,
        cbtc_status: str,
        active_train: Optional[str] = None,
        notes: str = ""
    ):
        self.block_id = block_id
        self.line_key = line_key
        self.from_station = from_station
        self.to_station = to_station
        self.length_km = round(length_km, 2)
        self.status = status
        self.speed_limit_kmh = speed_limit_kmh
        self.actual_speed_kmh = actual_speed_kmh
        self.third_rail_voltage_v = round(third_rail_voltage_v, 1)
        self.cbtc_status = cbtc_status
        self.active_train = active_train
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        cfg = GMRC_TRACK_STATUSES.get(self.status, GMRC_TRACK_STATUSES["CLEAR"])
        return {
            "block_id": self.block_id,
            "line_key": self.line_key,
            "from_station": self.from_station,
            "to_station": self.to_station,
            "segment_label": f"{self.from_station} ⇄ {self.to_station}",
            "length_km": self.length_km,
            "status": self.status,
            "status_label": cfg.get("label", self.status),
            "status_color": cfg.get("color", "#10B981"),
            "status_icon": cfg.get("icon", "🟢"),
            "badge_bg": cfg.get("badge_bg", "#ECFDF5"),
            "border": cfg.get("border", "#A7F3D0"),
            "speed_limit_kmh": self.speed_limit_kmh,
            "actual_speed_kmh": self.actual_speed_kmh,
            "third_rail_voltage_v": self.third_rail_voltage_v,
            "cbtc_status": self.cbtc_status,
            "active_train": self.active_train,
            "notes": self.notes
        }


class GMRCTrackMonitor:
    """
    Manages track blocks, wayside signaling telemetry, and simulated operational states
    for GMRC Metro network (East-West Line, North-South Line, and GN Branch).
    """

    @staticmethod
    def get_corridor_telemetry(corridor_key: str = "East-West Line", scenario: str = "nominal") -> Dict[str, Any]:
        """
        Generates track circuit and wayside telemetry for a given corridor and scenario.
        Scenarios:
        - 'nominal': Standard peak operations (clean 750V DC, nominal headway, no TSRs)
        - 'incident': Injected Kalupur signaling jitter & 25 km/h TSR on East-West Line
        - 'power_trip': Apparel Park substation traction breaker trip (0V DC)
        - 'switch_fault': Old High Court interchange point machine lock
        """
        if corridor_key not in GMRC_CORRIDORS:
            corridor_key = "East-West Line"

        corr_info = GMRC_CORRIDORS[corridor_key]
        stations = corr_info["stations"]
        code = corr_info["code"]
        num_stations = len(stations)
        
        # Total inter-station track blocks = num_stations - 1
        blocks: List[TrackBlock] = []
        avg_block_length = corr_info["length_km"] / max(num_stations - 1, 1)

        # Baseline train positions
        active_train_indices = {
            "East-West Line": [2, 6, 10, 14],  # Train present on these blocks
            "North-South Line": [2, 6, 11, 15, 22, 28],
            "GN Branch": [1]
        }.get(corridor_key, [1])


        for i in range(num_stations - 1):
            block_num = i + 1
            block_id = f"{code}-BLK-{block_num:02d}"
            st_from = stations[i]["name"]
            st_to = stations[i + 1]["name"]

            # Defaults: Nominal clear block
            status = "CLEAR"
            speed_limit = 80
            actual_speed = 74
            third_rail_v = 751.2
            cbtc_mode = "CBTC-ATO (Nominal)"
            active_train = None
            notes = "Track circuit impedance nominal; wayside balise signal link verified."

            # Assign active trains
            if i in active_train_indices:
                status = "OCCUPIED"
                actual_speed = 68
                train_num = 100 + (block_num * 2)
                direction = "EB" if corridor_key == "East-West Line" else "NB"
                active_train = f"GMRC-{train_num} ({direction})"
                notes = f"Train {train_num} en route to {st_to}; Automatic Train Protection (ATP) active."

            # SCENARIO INJECTIONS
            if scenario == "incident" and corridor_key == "East-West Line":
                # Incident on Kalupur zone (block around Shahpur / Gheekanta / Kalupur)
                if st_from == "Shahpur" or st_from == "Gheekanta":
                    status = "SPEED_RESTRICTION"
                    speed_limit = 25
                    actual_speed = 22
                    third_rail_v = 698.4
                    cbtc_mode = "Degraded (Wayside Balise Jitter)"
                    active_train = "GMRC-104 (EB - Delayed)"
                    notes = "🚨 Active TSR 25 km/h enforced by OCC Apparel Park due to wayside signal packet loss."
                elif st_from == "Old High Court":
                    # Trailing congestion behind TSR
                    status = "OCCUPIED"
                    actual_speed = 30
                    active_train = "GMRC-106 (EB - Holding)"
                    notes = "Train holding outside Shahpur station; ATO headway spacing regulation active."

            elif scenario == "power_trip" and corridor_key == "East-West Line":
                if "Apparel Park" in st_from or "Apparel Park" in st_to:
                    status = "POWER_FAULT"
                    speed_limit = 0
                    actual_speed = 0
                    third_rail_v = 0.0
                    cbtc_mode = "ATP Restricted"
                    active_train = "GMRC-112 (EB - Stalled)"
                    notes = "⚡ Traction Substation TSS-04 breaker trip; 750V DC de-energized. Emergency traction battery on."

            elif scenario == "switch_fault" and (corridor_key in ["East-West Line", "North-South Line"]):
                if "Old High Court" in st_from or "Old High Court" in st_to:
                    status = "SPEED_RESTRICTION"
                    speed_limit = 20
                    actual_speed = 15
                    cbtc_mode = "Interlocking Fail-Safe (Manual Route Check)"
                    notes = "⚠️ Point switch 102A route confirmation delay at Old High Court interchange."

            block = TrackBlock(
                block_id=block_id,
                line_key=corridor_key,
                from_station=st_from,
                to_station=st_to,
                length_km=avg_block_length,
                status=status,
                speed_limit_kmh=speed_limit,
                actual_speed_kmh=actual_speed,
                third_rail_voltage_v=third_rail_v,
                cbtc_status=cbtc_mode,
                active_train=active_train,
                notes=notes
            )
            blocks.append(block)

        # Aggregate Statistics
        block_dicts = [b.to_dict() for b in blocks]
        clear_cnt = sum(1 for b in blocks if b.status == "CLEAR")
        occ_cnt = sum(1 for b in blocks if b.status == "OCCUPIED")
        tsr_cnt = sum(1 for b in blocks if b.status == "SPEED_RESTRICTION")
        fault_cnt = sum(1 for b in blocks if b.status in ["POWER_FAULT", "MAINTENANCE_POSSESSION"])
        active_trains_cnt = sum(1 for b in blocks if b.active_train is not None)

        avg_speed = round(sum(b.actual_speed_kmh for b in blocks) / max(len(blocks), 1), 1)
        
        # Calculate nominal vs incident headways
        headway_min = 3.5
        if scenario == "incident" and corridor_key == "East-West Line":
            headway_min = 15.6  # Correlates with the injected anomaly
        elif scenario == "power_trip":
            headway_min = 25.0
        elif scenario == "switch_fault":
            headway_min = 8.5

        overall_health = "NOMINAL"
        if fault_cnt > 0:
            overall_health = "CRITICAL"
        elif tsr_cnt > 0 or scenario in ["incident", "switch_fault"]:
            overall_health = "WARNING"

        return {
            "corridor_key": corridor_key,
            "corridor_code": code,
            "name": corr_info["name"],
            "route_label": corr_info["route_label"],
            "color": corr_info["color"],
            "length_km": corr_info["length_km"],
            "station_count": num_stations,
            "stations": stations,
            "block_count": len(blocks),
            "blocks": block_dicts,
            "summary": {
                "clear_blocks": clear_cnt,
                "occupied_blocks": occ_cnt,
                "tsr_blocks": tsr_cnt,
                "fault_blocks": fault_cnt,
                "active_trains_count": active_trains_cnt,
                "average_speed_kmh": avg_speed,
                "operating_headway_min": headway_min,
                "overall_health": overall_health,
                "scenario": scenario
            }
        }

    @staticmethod
    def get_network_overview(scenario: str = "nominal") -> Dict[str, Any]:
        """
        Returns full multi-corridor GMRC track telemetry overview.
        """
        corridors_data = {}
        total_blocks = 0
        total_tsrs = 0
        total_faults = 0
        total_active_trains = 0

        for key in GMRC_CORRIDORS.keys():
            data = GMRCTrackMonitor.get_corridor_telemetry(key, scenario=scenario)
            corridors_data[key] = data
            s = data["summary"]
            total_blocks += data["block_count"]
            total_tsrs += s["tsr_blocks"]
            total_faults += s["fault_blocks"]
            total_active_trains += s["active_trains_count"]

        system_status = "NOMINAL"
        if total_faults > 0:
            system_status = "CRITICAL"
        elif total_tsrs > 0 or scenario != "nominal":
            system_status = "WARNING"

        return {
            "system_status": system_status,
            "scenario": scenario,
            "total_corridors": len(corridors_data),
            "total_blocks": total_blocks,
            "total_tsr_zones": total_tsrs,
            "total_power_faults": total_faults,
            "total_active_trains": total_active_trains,
            "corridors": corridors_data
        }

    @staticmethod
    def get_track_evidence_for_explainer(corridor_key: str = "East-West Line", scenario: str = "incident") -> List[str]:
        """
        Produces factual wayside evidence bullet points to ground AI Explainer exceptions.
        """
        data = GMRCTrackMonitor.get_corridor_telemetry(corridor_key, scenario=scenario)
        evidence = []
        summary = data["summary"]

        if summary["tsr_blocks"] > 0:
            tsr_blocks = [b for b in data["blocks"] if b["status"] == "SPEED_RESTRICTION"]
            for b in tsr_blocks:
                evidence.append(
                    f"Wayside Track Telemetry: Block {b['block_id']} ({b['segment_label']}) operating under "
                    f"active TSR ({b['speed_limit_kmh']} km/h vs 80 km/h nominal) due to {b['cbtc_status']}."
                )

        if summary["fault_blocks"] > 0:
            fault_blocks = [b for b in data["blocks"] if b["status"] in ["POWER_FAULT", "MAINTENANCE_POSSESSION"]]
            for b in fault_blocks:
                evidence.append(
                    f"Traction Power Alert: Block {b['block_id']} ({b['segment_label']}) third rail de-energized "
                    f"({b['third_rail_voltage_v']}V DC logged at local substation feeder)."
                )

        evidence.append(
            f"Signaling Headway: Real-time corridor headway widened to {summary['operating_headway_min']:.1f} min "
            f"(nominal peak headway is 3.5 min)."
        )

        return evidence
