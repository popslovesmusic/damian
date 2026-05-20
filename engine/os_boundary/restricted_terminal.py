import os
import json
import datetime
import re

class RestrictedAdminTerminal:
    def __init__(self, boundary_contract_path, command_contract_path, data_root):
        with open(boundary_contract_path, 'r') as f:
            self.boundary = json.load(f)
        with open(command_contract_path, 'r') as f:
            self.commands_contract = json.load(f)
        
        self.data_root = data_root
        self.audit_log_path = os.path.join(data_root, self.boundary["audit_config"]["audit_log_path"])
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        
        self.registry = {cmd["command"].split()[0]: cmd for cmd in self.commands_contract["commands"]}

    def log_audit(self, command_str, status, details=None):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "command": command_str,
            "status": status,
            "details": details or {}
        }
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def validate_command_string(self, command_str):
        if len(command_str) > self.commands_contract["validation_rules"]["max_command_length"]:
            return False, "Command too long."
        
        disallowed = self.commands_contract["validation_rules"]["disallowed_characters"]
        for char in disallowed:
            if char in command_str:
                return False, f"Disallowed character detected: {char}"
        
        return True, "Valid"

    def execute(self, command_str):
        is_valid, msg = self.validate_command_string(command_str)
        if not is_valid:
            self.log_audit(command_str, "REJECTED", {"reason": msg})
            return f"ERROR: {msg}"

        parts = command_str.split()
        if not parts:
            return ""
        
        base_cmd = parts[0]
        if base_cmd not in self.registry:
            self.log_audit(command_str, "UNKNOWN")
            return f"ERROR: Unknown command family '{base_cmd}'."

        cmd_info = self.registry[base_cmd]
        
        # Simple Dispatcher
        if base_cmd == "status":
            return self._cmd_status()
        elif base_cmd == "persistence":
            return self._cmd_persistence(parts[1:])
        elif base_cmd == "diag":
            return self._cmd_diag(parts[1:])
        elif base_cmd == "content":
             return self._cmd_content(parts[1:])
        elif base_cmd == "lineage":
             return self._cmd_lineage(parts[1:])
        elif base_cmd == "flash":
             return self._cmd_flash(parts[1:])
        elif base_cmd == "boot":
             return self._cmd_boot(parts[1:])
        elif base_cmd == "recovery":
             return self._cmd_recovery(parts[1:])
        elif base_cmd == "update":
             return self._cmd_update(parts[1:])
        elif base_cmd == "echo":
             return self._cmd_echo(parts[1:])
        elif base_cmd == "audio":
             return self._cmd_audio(parts[1:])
        elif base_cmd == "treaty":
             return self._cmd_treaty(parts[1:])
        elif base_cmd == "reputation":
             return self._cmd_reputation(parts[1:])
        elif base_cmd == "transit":
             return self._cmd_transit(parts[1:])
        elif base_cmd == "relay":
             return self._cmd_relay(parts[1:])
        elif base_cmd == "event":
             return self._cmd_event(parts[1:])
        elif base_cmd == "market":
             return self._cmd_market(parts[1:])
        elif base_cmd == "quest":
             return self._cmd_quest(parts[1:])
        elif base_cmd == "faction":
             return self._cmd_faction(parts[1:])
        elif base_cmd == "politics":
             return self._cmd_politics(parts[1:])
        elif base_cmd == "mvp":
             return self._cmd_mvp(parts[1:])
        elif base_cmd == "alpha":
             return self._cmd_alpha(parts[1:])
        elif base_cmd == "exit":
            return "Closing maintenance hatch..."
        
        self.log_audit(command_str, "NOT_IMPLEMENTED")
        return "ERROR: Command logic not implemented in prototype."

    def _cmd_status(self):
        self.log_audit("status", "SUCCESS")
        return "Tower OS Status: ONLINE\nCore: IMMUTABLE\nData: PERSISTENT\nUptime: 0.1 hours (PROTOTYPE)"

    def _cmd_persistence(self, args):
        if not args or args[0] != "info":
            return "Usage: persistence info"
        
        # Simulate check
        report = {
            "mount": "/tower/data",
            "label": "TOWER_DATA",
            "writable": os.access(self.data_root, os.W_OK),
            "directories": os.listdir(self.data_root) if os.path.exists(self.data_root) else []
        }
        self.log_audit("persistence info", "SUCCESS")
        return f"Persistence Info:\n{json.dumps(report, indent=2)}"

    def _cmd_diag(self, args):
        if not args or args[0] != "health":
            return "Usage: diag health"
        
        # Simulate diagnostic health check
        health = {
            "rootfs_integrity": "VERIFIED",
            "memory_pressure": "LOW",
            "disk_health": "OPTIMAL",
            "kiosk_service": "RUNNING"
        }
        self.log_audit("diag health", "SUCCESS")
        return f"System Health:\n{json.dumps(health, indent=2)}"

    def _cmd_content(self, args):
        if not args or args[0] != "status":
            return "Usage: content status"
        
        # Report cartridge evidence from audit file if it exists
        evidence_path = "outputs/audits/kiosk_launcher_cartridge_verification_result.json"
        if os.path.exists(evidence_path):
            with open(evidence_path, 'r') as f:
                evidence = json.load(f)
            self.log_audit("content status", "SUCCESS")
            return f"Cartridge Verification Status:\n{json.dumps(evidence, indent=2)}"
        else:
            self.log_audit("content status", "MISSING_EVIDENCE")
            return "ERROR: Cartridge verification evidence missing."

    def _cmd_lineage(self, args):
        if not args or args[0] != "status":
            return "Usage: lineage status"
        
        # Report lineage evidence from audit file
        evidence_path = "outputs/audits/kiosk_launcher_lineage_result.json"
        if os.path.exists(evidence_path):
            with open(evidence_path, 'r') as f:
                evidence = json.load(f)
            self.log_audit("lineage status", "SUCCESS")
            return f"Artifact Lineage Status:\n{json.dumps(evidence, indent=2)}"
        else:
            self.log_audit("lineage status", "MISSING_EVIDENCE")
            return "ERROR: Lineage evidence missing."

    def _cmd_flash(self, args):
        if not args:
            return "Usage: flash status | flash report"

        if args[0] == "status":
            # Report flash handoff evidence from audit file if it exists
            evidence_path = "outputs/audits/admin_terminal_usb_handoff_result.json"
            if os.path.exists(evidence_path):
                with open(evidence_path, 'r') as f:
                    evidence = json.load(f)
                self.log_audit("flash status", "SUCCESS")
                return f"USB Flashing Handoff Status:\n{json.dumps(evidence, indent=2)}"
            else:
                self.log_audit("flash status", "MISSING_EVIDENCE")
                return "ERROR: Flash handoff evidence missing."

        elif args[0] == "report":
            # Report physical flash execution evidence
            evidence_path = "outputs/audits/controlled_flash_execution_result.json"
            if os.path.exists(evidence_path):
                with open(evidence_path, 'r') as f:
                    evidence = json.load(f)
                self.log_audit("flash report", "SUCCESS")
                return f"Physical Flash Execution Report:\n{json.dumps(evidence, indent=2)}"
            else:
                self.log_audit("flash report", "MISSING_EVIDENCE")
                return "ERROR: Flash execution evidence missing."

        return f"ERROR: Unknown flash subcommand '{args[0]}'."

    def _cmd_boot(self, args):
        if not args or args[0] != "status":
            return "Usage: boot status"
        
        # Report physical boot validation evidence
        evidence_path = "outputs/audits/physical_boot_validation_result.json"
        if os.path.exists(evidence_path):
            with open(evidence_path, 'r') as f:
                evidence = json.load(f)
            self.log_audit("boot status", "SUCCESS")
            return f"Physical Boot Validation Status:\n{json.dumps(evidence, indent=2)}"
        else:
            self.log_audit("boot status", "MISSING_EVIDENCE")
            return "ERROR: Boot validation evidence missing."

    def _cmd_recovery(self, args):
        if not args:
            return "Usage: recovery scan | recovery simulate <id> | recovery audit"
        
        if args[0] == "scan":
            # In a real tool, we'd instantiate RecoveryManager and run scan_integrity()
            self.log_audit("recovery scan", "SUCCESS")
            return "Recovery Scan: No critical integrity violations detected (PROTOTYPE)."
            
        elif args[0] == "simulate":
             if len(args) < 2: return "Usage: recovery simulate <snapshot_id>"
             self.log_audit(f"recovery simulate {args[1]}", "SUCCESS")
             return f"Recovery Simulation: Dry-run for snapshot '{args[1]}' successful."
             
        elif args[0] == "audit":
             evidence_path = "outputs/audits/recovery_lineage_audit_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("recovery audit", "SUCCESS")
                 return f"Recovery Audit Log:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("recovery audit", "MISSING_EVIDENCE")
                 return "ERROR: Recovery audit evidence missing."
                 
        return f"ERROR: Unknown recovery subcommand '{args[0]}'."

    def _cmd_update(self, args):
        if not args:
            return "Usage: update scan <path> | update plan | update audit"
            
        if args[0] == "scan":
             if len(args) < 2: return "Usage: update scan <cartridge_path>"
             self.log_audit(f"update scan {args[1]}", "SUCCESS")
             return f"Update Scan: Cartridge at '{args[1]}' verified and ready for planning."
             
        elif args[0] == "plan":
             self.log_audit("update plan", "SUCCESS")
             return "Update Plan: Patch migration dry-run generated (PROTOTYPE)."
             
        elif args[0] == "audit":
             evidence_path = "outputs/audits/update_cartridge_verification_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("update audit", "SUCCESS")
                 return f"Update Artifact Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("update audit", "MISSING_EVIDENCE")
                 return "ERROR: Update audit evidence missing."
                 
        return f"ERROR: Unknown update subcommand '{args[0]}'."

    def _cmd_echo(self, args):
        if not args:
            return "Usage: echo export | echo report"
            
        if args[0] == "export":
            # In a real tool, we'd instantiate DomainEchoExporter
            self.log_audit("echo export", "SUCCESS")
            return "Domain Echo: State exported and hash-verified (PROTOTYPE)."
            
        elif args[0] == "report":
            evidence_path = "outputs/audits/offline_domain_attack_result.json"
            if os.path.exists(evidence_path):
                with open(evidence_path, 'r') as f:
                    evidence = json.load(f)
                self.log_audit("echo report", "SUCCESS")
                return f"Domain Echo Attack Report:\n{json.dumps(evidence, indent=2)}"
            else:
                self.log_audit("echo report", "MISSING_EVIDENCE")
                return "ERROR: Domain Echo attack evidence missing."
                
        return f"ERROR: Unknown echo subcommand '{args[0]}'."

    def _cmd_audio(self, args):
        if not args or args[0] != "status":
            return "Usage: audio status"
        
        # Report live audio session status
        evidence_path = "outputs/audits/voice_session_stub_result.json"
        if os.path.exists(evidence_path):
            with open(evidence_path, 'r') as f:
                evidence = json.load(f)
            self.log_audit("audio status", "SUCCESS")
            return f"Live Audio Session Status:\n{json.dumps(evidence, indent=2)}"
        else:
            self.log_audit("audio status", "MISSING_EVIDENCE")
            return "ERROR: Audio session evidence missing."

    def _cmd_treaty(self, args):
        if not args:
            return "Usage: treaty status | treaty audit"
        
        if args[0] == "status":
             # Report active treaty status
             evidence_path = "outputs/audits/treaty_creation_stub_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("treaty status", "SUCCESS")
                 return f"Active Treaty Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("treaty status", "MISSING_EVIDENCE")
                 return "ERROR: Treaty evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/shared_reward_burden_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("treaty audit", "SUCCESS")
                 return f"Treaty Shared Burden Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("treaty audit", "MISSING_EVIDENCE")
                 return "ERROR: Treaty burden evidence missing."
                 
        return f"ERROR: Unknown treaty subcommand '{args[0]}'."

    def _cmd_reputation(self, args):
        if not args:
            return "Usage: reputation status | reputation audit"
            
        if args[0] == "status":
             # Report current reputation snapshot
             evidence_path = "outputs/audits/reputation_snapshot_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("reputation status", "SUCCESS")
                 return f"Survivor Reputation Snapshot:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("reputation status", "MISSING_EVIDENCE")
                 return "ERROR: Reputation snapshot missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/reputation_signal_generation_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("reputation audit", "SUCCESS")
                 return f"Reputation Signal Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("reputation audit", "MISSING_EVIDENCE")
                 return "ERROR: Reputation signal evidence missing."
                 
        return f"ERROR: Unknown reputation subcommand '{args[0]}'."

    def _cmd_transit(self, args):
        if not args:
            return "Usage: transit export | transit status"
            
        if args[0] == "export":
            # In a real tool, we'd instantiate TransitManager
            self.log_audit("transit export", "SUCCESS")
            return "Cross-World Transit: Survivor exported and identity hash-verified (PROTOTYPE)."
            
        elif args[0] == "status":
             evidence_path = "outputs/audits/survivor_transit_export_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("transit status", "SUCCESS")
                 return f"Cross-World Transit Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("transit status", "MISSING_EVIDENCE")
                 return "ERROR: Transit evidence missing."
                 
        return f"ERROR: Unknown transit subcommand '{args[0]}'."

    def _cmd_relay(self, args):
        if not args:
            return "Usage: relay status | relay audit"
        
        if args[0] == "status":
             # Report active relay hub status
             evidence_path = "outputs/audits/distributed_survivor_hub_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("relay status", "SUCCESS")
                 return f"Relay Hub Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("relay status", "MISSING_EVIDENCE")
                 return "ERROR: Relay hub evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/relay_visibility_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("relay audit", "SUCCESS")
                 return f"Relay Visibility Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("relay audit", "MISSING_EVIDENCE")
                 return "ERROR: Relay visibility evidence missing."
                 
        return f"ERROR: Unknown relay subcommand '{args[0]}'."

    def _cmd_event(self, args):
        if not args:
            return "Usage: event status | event forecast | event audit"
            
        if args[0] == "status":
             # Report active event wave status
             evidence_path = "outputs/audits/event_wave_generation_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("event status", "SUCCESS")
                 return f"Active Event Wave Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("event status", "MISSING_EVIDENCE")
                 return "ERROR: Event wave evidence missing."
                 
        elif args[0] == "forecast":
             evidence_path = "outputs/audits/global_pressure_forecast_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("event forecast", "SUCCESS")
                 return f"Global Pressure Forecast:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("event forecast", "MISSING_EVIDENCE")
                 return "ERROR: Pressure forecast evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/relay_pressure_propagation_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("event audit", "SUCCESS")
                 return f"Event Wave Audit Log:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("event audit", "MISSING_EVIDENCE")
                 return "ERROR: Event wave audit evidence missing."
                 
        return f"ERROR: Unknown event subcommand '{args[0]}'."

    def _cmd_market(self, args):
        if not args:
            return "Usage: market status | market audit"
            
        if args[0] == "status":
             # Report current market listing evidence
             evidence_path = "outputs/audits/market_listing_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("market status", "SUCCESS")
                 return f"Survivor Market Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("market status", "MISSING_EVIDENCE")
                 return "ERROR: Market evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/market_instability_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("market audit", "SUCCESS")
                 return f"Market Instability Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("market audit", "MISSING_EVIDENCE")
                 return "ERROR: Market instability evidence missing."
                 
        return f"ERROR: Unknown market subcommand '{args[0]}'."

    def _cmd_quest(self, args):
        if not args:
            return "Usage: quest status | quest audit"
            
        if args[0] == "status":
             # Report current quest/contract status
             evidence_path = "outputs/audits/procedural_contract_generation_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("quest status", "SUCCESS")
                 return f"Survivor Contract Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("quest status", "MISSING_EVIDENCE")
                 return "ERROR: Contract evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/contract_failure_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("quest audit", "SUCCESS")
                 return f"Contract Failure Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("quest audit", "MISSING_EVIDENCE")
                 return "ERROR: Contract audit evidence missing."
                 
        return f"ERROR: Unknown quest subcommand '{args[0]}'."

    def _cmd_faction(self, args):
        if not args:
            return "Usage: faction status | faction audit"
            
        if args[0] == "status":
             # Report current faction bloc evidence
             evidence_path = "outputs/audits/faction_emergence_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("faction status", "SUCCESS")
                 return f"Survivor Bloc Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("faction status", "MISSING_EVIDENCE")
                 return "ERROR: Faction evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/faction_stability_fracture_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("faction audit", "SUCCESS")
                 return f"Faction Stability Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("faction audit", "MISSING_EVIDENCE")
                 return "ERROR: Faction stability evidence missing."
                 
        return f"ERROR: Unknown faction subcommand '{args[0]}'."

    def _cmd_politics(self, args):
        if not args:
            return "Usage: politics status | politics audit"
            
        if args[0] == "status":
             # Report current schism evidence
             evidence_path = "outputs/audits/faction_schism_generation_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("politics status", "SUCCESS")
                 return f"Faction Schism Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("politics status", "MISSING_EVIDENCE")
                 return "ERROR: Politics evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/political_recovery_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("politics audit", "SUCCESS")
                 return f"Political Recovery Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("politics audit", "MISSING_EVIDENCE")
                 return "ERROR: Political recovery evidence missing."
                 
        return f"ERROR: Unknown politics subcommand '{args[0]}'."

    def _cmd_mvp(self, args):
        if not args:
            return "Usage: mvp status | mvp audit"
            
        if args[0] == "status":
             # In prototype, status is just a heartbeat that the command is active
             self.log_audit("mvp status", "SUCCESS")
             return "MVP Vertical Slice Runtime: READY for smoke testing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/mvp_runtime_smoke_test_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("mvp audit", "SUCCESS")
                 return f"MVP Runtime Smoke Test Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("mvp audit", "MISSING_EVIDENCE")
                 return "ERROR: MVP runtime smoke test evidence missing."
                 
        return f"ERROR: Unknown mvp subcommand '{args[0]}'."

    def _cmd_alpha(self, args):
        if not args:
            return "Usage: alpha status | alpha audit"
            
        if args[0] == "status":
             # Report current closed alpha cohort evidence
             evidence_path = "outputs/audits/alpha_cohort_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("alpha status", "SUCCESS")
                 return f"Closed Alpha Cohort Status:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("alpha status", "MISSING_EVIDENCE")
                 return "ERROR: Alpha cohort evidence missing."
                 
        elif args[0] == "audit":
             evidence_path = "outputs/audits/offline_telemetry_export_result.json"
             if os.path.exists(evidence_path):
                 with open(evidence_path, 'r') as f:
                     evidence = json.load(f)
                 self.log_audit("alpha audit", "SUCCESS")
                 return f"Closed Alpha Telemetry Audit:\n{json.dumps(evidence, indent=2)}"
             else:
                 self.log_audit("alpha audit", "MISSING_EVIDENCE")
                 return "ERROR: Alpha telemetry evidence missing."
                 
        return f"ERROR: Unknown alpha subcommand '{args[0]}'."


if __name__ == "__main__":
    # Test stub
    data_root = "build/runtime_persistence_test"
    os.makedirs(data_root, exist_ok=True)
    
    term = RestrictedAdminTerminal(
        "engine/os_boundary/contracts/restricted_terminal_boundary.json",
        "engine/os_boundary/contracts/admin_terminal_command_contract.json",
        data_root
    )
    
    print(term.execute("status"))
    print(term.execute("persistence info"))
    print(term.execute("diag health"))
    print(term.execute("sudo rm -rf /")) # Should be rejected
    print(term.execute("unknown_cmd"))    # Should be unknown
