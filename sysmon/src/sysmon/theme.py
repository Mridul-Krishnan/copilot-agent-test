"""Dark and light theme CSS for sysmon.

Uses Textual's built-in :dark / :light pseudo-classes. The app toggles
via `self.dark = True/False` which automatically activates the right rules.
"""

SYSMON_CSS = """
Screen {
    background: $surface;
}
#header-bar {
    dock: top;
    height: 1;
    background: $primary-darken-2;
    color: $text;
    text-style: bold;
    padding: 0 1;
}
#footer-bar {
    dock: bottom;
    height: 1;
    background: $primary-darken-2;
    color: $text;
    padding: 0 1;
}
.panels-grid {
    layout: grid;
    grid-size: 2;
    grid-gutter: 1;
    padding: 1;
}
.panels-grid > * {
    border: round $primary;
}
MetricPanel Sparkline {
    height: 3;
}
IOMetricPanel Sparkline {
    height: 3;
}

/* Per-metric sparkline colours */
#cpu Sparkline {
    color: $success;
}
#ram Sparkline {
    color: $warning;
}
#swap Sparkline {
    color: $warning-darken-1;
}
#disk-r Sparkline {
    color: $accent;
}
#disk-w Sparkline {
    color: $accent-darken-1;
}
#net-s Sparkline {
    color: $secondary;
}
#net-r Sparkline {
    color: $secondary-darken-1;
}

/* Progress bar colour classes */
MetricPanel ProgressBar.ok Bar {
    color: $success;
}
MetricPanel ProgressBar.warn Bar {
    color: $warning;
}
MetricPanel ProgressBar.crit Bar {
    color: $error;
}

/* Panel border colours based on severity */
.panels-grid > MetricPanel.ok {
    border: round $success;
}
.panels-grid > MetricPanel.warn {
    border: round $warning;
}
.panels-grid > MetricPanel.crit {
    border: round $error;
}

/* Blink effect on critical metric labels */
.crit-label {
    text-style: bold blink;
}

/* Per-core CPU mini-bar */
.core-bar {
    color: $success;
}

/* Process table view */
#proc-view {
    display: none;
    padding: 1;
}
"""
