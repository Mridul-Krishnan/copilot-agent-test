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
    background: $primary;
    color: $text;
    text-style: bold;
    padding: 0 1;
}
#footer-bar {
    dock: bottom;
    height: 1;
    background: $primary;
    color: $text;
    padding: 0 1;
}
.panels-grid {
    layout: grid;
    grid-size: 2;
    grid-gutter: 1;
    padding: 1;
}
MetricPanel Sparkline {
    height: 2;
}
IOMetricPanel Sparkline {
    height: 2;
}
"""
