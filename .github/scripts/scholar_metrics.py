"""Read the all-time metrics from a public Google Scholar profile."""
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import sys
from urllib.request import Request, urlopen

PROFILE = "https://scholar.google.com/citations?user=UysVplUAAAAJ&hl=en"
REQUIRED = {"citations", "h-index", "i10-index"}


class ScholarMetrics(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.row = None
        self.cell = None
        self.metrics = {}

    def handle_starttag(self, tag, attrs):
        if tag == "table" and dict(attrs).get("id") == "gsc_rsb_st":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.row = []
        elif self.row is not None and tag == "td":
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            self.row.append("".join(self.cell).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if len(self.row) >= 2:
                label = self.row[0].lower()
                if label in REQUIRED:
                    value = self.row[1].replace(",", "").replace("\u00a0", "").replace(" ", "")
                    if value.isdecimal():
                        self.metrics[label] = int(value)
            self.row = None
        elif tag == "table" and self.in_table:
            self.in_table = False


def main():
    request = Request(PROFILE, headers={"User-Agent": "VimalPortfolioCitationRefresh/1.0"})
    with urlopen(request, timeout=20) as response:
        page = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    parser = ScholarMetrics()
    parser.feed(page)
    if parser.metrics.keys() != REQUIRED:
        raise SystemExit("Google Scholar did not return a complete citation table.")
    snapshot = {"source": PROFILE, "metrics": parser.metrics,
                "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    json.dump(snapshot, sys.stdout, indent=2, sort_keys=True)
    print()


if __name__ == "__main__":
    main()
