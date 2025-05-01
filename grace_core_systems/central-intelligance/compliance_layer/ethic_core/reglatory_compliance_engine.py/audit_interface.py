# audit_interface.py

from typing import Optional
import questionary  # For rich CLI interactions
from rich.console import Console
from rich.table import Table

class AuditCLI:
    def __init__(self, engine: ComplianceEngine):
        self.engine = engine
        self.console = Console()
        
    def start_session(self):
        """Interactive audit interface"""
        while True:
            choice = questionary.select(
                "Compliance Audit Interface",
                choices=[
                    "Check Current Compliance",
                    "Generate Report",
                    "Inspect Violations",
                    "Debug Last Failure",
                    "Exit"
                ]).ask()
            
            if choice == "Check Current Compliance":
                self._display_compliance_state()
            elif choice == "Generate Report":
                self._generate_report_flow()
            elif choice == "Inspect Violations":
                self._show_violations()
            elif choice == "Debug Last Failure":
                self._debug_failure()
            else:
                break

    def _display_compliance_state(self):
        table = Table(title="Current Compliance Status")
        table.add_column("Standard", justify="left")
        table.add_column("Status", justify="center")
        table.add_column("Last Checked", justify="right")
        
        monitor = ComplianceMonitor(self.engine)
        status = monitor.check_current_compliance()
        
        for standard, data in status.items():
            status_icon = "✅" if data['compliant'] else "❌"
            table.add_row(
                standard.value.upper(),
                status_icon,
                data['last_checked'].strftime("%Y-%m-%d %H:%M")
            )
            
        self.console.print(table)

class AuditGUI:
    # Web-based GUI implementation would go here
    # Using FastAPI + React for enterprise web interface
    pass