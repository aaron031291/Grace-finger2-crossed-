# In parent system
route_tag, routing_meta = entropy_filter.route(anchor)

# Route handling
if route_tag == "discarded":
    storage_purge(anchor, verification=routing_meta["shred_verification"])
elif route_tag == "escalated":
    alert_system.notify(
        parties=routing_meta["notified_parties"],
        deadline=routing_meta["response_deadline"]
    )