"""Rewrite the Contributions section of README.md with merged pull requests
to repositories owned by someone else. Run daily by update-contributions.yml."""
import json, os, re, urllib.parse, urllib.request
from datetime import datetime

user = os.environ.get("GH_USER", "SamuelCGilbert")
token = os.environ.get("GITHUB_TOKEN", "")
query = f"is:pr is:merged author:{user} -user:{user}"
url = "https://api.github.com/search/issues?per_page=100&sort=created&order=desc&q=" + urllib.parse.quote(query)
req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                           **({"Authorization": f"Bearer {token}"} if token else {})})
items = json.load(urllib.request.urlopen(req))["items"]

prs = []
for it in items:
    repo = it["repository_url"].split("/repos/", 1)[1]
    merged = (it.get("pull_request") or {}).get("merged_at") or it["closed_at"]
    prs.append((merged, repo, it["title"].strip(), it["html_url"]))
prs.sort(reverse=True)

lines = []
for merged, repo, title, link in prs:
    when = datetime.strptime(merged[:10], "%Y-%m-%d").strftime("%b %Y")
    lines.append(f"- **[{repo}](https://github.com/{repo})**: [{title}]({link}) ({when})")
body = "\n".join(lines) if lines else "_None yet._"

readme = open("README.md", encoding="utf-8").read()
new = re.sub(r"(<!-- contributions:start -->).*?(<!-- contributions:end -->)",
             lambda m: m.group(1) + "\n" + body + "\n" + m.group(2), readme, flags=re.S)
if new != readme:
    open("README.md", "w", encoding="utf-8", newline="\n").write(new)
    print(f"updated: {len(prs)} merged pull requests")
else:
    print("no change")
