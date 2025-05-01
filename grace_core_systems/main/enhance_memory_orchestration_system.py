# memory/orchestrator.py

class MemoryOrchestrator:
    def __init__(self):
        # Existing components
        self.fusion = FusionVault()
        self.lightning = LightningStore()
        self.auditor = AnchorAuditor(self.fusion)
        
        # New components
        self.sandbox = DecaySandbox(self.fusion, self.lightning)
        self.learner = LearningLoop(self.sandbox, self.auditor)
        
    def _stress_test_fusion(self):
        """Demote to sandbox instead of Lightning"""
        for node in self.fusion.graph.nodes:
            if self._is_stale(node):
                anchor = self.fusion.get_anchor(node)
                self.sandbox.add_expired_anchor(anchor)
                self.fusion.graph.remove_node(node)
                
    def start(self):
        self.learner.start()
        super().start()
        
    def stop(self):
        self.learner.stop()
        super().stop()