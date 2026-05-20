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
