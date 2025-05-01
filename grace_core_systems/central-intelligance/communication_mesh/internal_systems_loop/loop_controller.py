def dynamic_threshold_adjustment(sandbox: DecaySandbox):
    current_load = len(sandbox.current_batch)
    if current_load > 1000:
        sandbox.config["reinforce_threshold"] = 0.85  # Be more selective
    elif current_load < 200:
        sandbox.config["reinforce_threshold"] = 0.7   # Allow more learning