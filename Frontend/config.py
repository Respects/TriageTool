API_BASE = "http://localhost:8000"

PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}
PRIORITY_OPTIONS = ["High", "Medium", "Low"]
STATUS_OPTIONS = ["New", "Processing", "Closed"]

PRIORITY_STYLE = {
    "High":   ("#ef4444", "rgba(239, 68, 68, 0.15)"),
    "Medium": ("#f59e0b", "rgba(245, 158, 11, 0.15)"),
    "Low":    ("#22c55e", "rgba(34, 197, 94, 0.15)"),
}
STATUS_STYLE = {
    "New":        ("#3b82f6", "rgba(59, 130, 246, 0.15)"),
    "Processing": ("#f59e0b", "rgba(245, 158, 11, 0.15)"),
    "Closed":     ("#9ca3af", "rgba(156, 163, 175, 0.18)"),
}
DEFAULT_STYLE = ("#9ca3af", "rgba(156, 163, 175, 0.18)")