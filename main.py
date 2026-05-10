import os
import urllib.request
import json as _json
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import gifos


def compute_top_langs(user):
    """Aggregate language bytes across all repos (forks included).

    gifos excludes forks, which drops libfabric/aws-ofi-nccl/upstream-to-nvshmem.
    Jupyter Notebook and Makefile are filtered out as they're vendored artifacts,
    not languages actively written.
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    ignored = {"Jupyter Notebook", "Makefile"}
    totals = defaultdict(int)
    page = 1
    while True:
        url = f"https://api.github.com/users/{user}/repos?per_page=100&type=owner&page={page}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as r:
            repos = _json.loads(r.read())
        if not repos:
            break
        for repo in repos:
            lang_url = f"https://api.github.com/repos/{repo['full_name']}/languages"
            lreq = urllib.request.Request(lang_url, headers=headers)
            with urllib.request.urlopen(lreq) as r:
                langs = _json.loads(r.read())
            for name, size in langs.items():
                if name in ignored:
                    continue
                totals[name] += size
        page += 1
    return [n for n, _ in sorted(totals.items(), key=lambda kv: -kv[1])]

def main():
    t = gifos.Terminal(750, 440, 15, 15)

    # BIOS boot
    t.gen_text("", 1, count=15)
    t.toggle_show_cursor(False)
    year_now = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y")
    t.gen_text("XUAN_OS Modular BIOS v2.0.26", 1)
    t.gen_text(f"Copyright (C) {year_now}, \\x1b[35mAnnapurna Labs\\x1b[0m", 2)
    t.gen_text("\\x1b[94mNeural Compute Engine, Rev 2026\\x1b[0m", 4)
    t.gen_text("Krypton(tm) GIFCPU - 500Hz", 6)
    for i in range(0, 65653, 9000):
        t.delete_row(7)
        t.gen_text(f"Memory Test: {i}", 7, contin=True)
    t.delete_row(7)
    t.gen_text("Memory Test: 64KB OK", 7, count=8, contin=True)
    t.gen_text("", 9, count=8, contin=True)

    # Boot sequence
    t.clear_frame()
    t.gen_text("Initiating Boot Sequence ", 1, contin=True)
    t.gen_typing_text(".....", 1, contin=True)

    # Login
    t.clear_frame()
    t.clone_frame(5)
    t.toggle_show_cursor(False)
    t.gen_text("\\x1b[93mXUAN_OS v2.0.26 (tty1)\\x1b[0m", 1, count=5)
    t.gen_text("login: ", 3, count=5)
    t.toggle_show_cursor(True)
    t.gen_typing_text("xuan", 3, contin=True)
    t.gen_text("", 4, count=5)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=5)
    t.toggle_show_cursor(True)
    t.gen_typing_text("**********", 4, contin=True)
    t.toggle_show_cursor(False)
    time_now = datetime.now(ZoneInfo("America/Los_Angeles")).strftime(
        "%a %b %d %I:%M:%S %p %Z %Y"
    )
    t.gen_text(f"Last login: {time_now} on tty1", 6)

    # Neofetch-style output
    t.gen_prompt(8, count=5)
    prompt_col = t.curr_col
    t.toggle_show_cursor(True)
    t.gen_typing_text("\\x1b[91mfetch.s", 8, contin=True)
    t.delete_row(8, prompt_col)
    t.gen_text("\\x1b[92mfetch.sh\\x1b[0m", 8, contin=True)
    t.gen_typing_text(" -u Xuan-1998", 8, contin=True)

    git_stats = gifos.utils.fetch_github_stats("Xuan-1998")
    top_langs = compute_top_langs("Xuan-1998")

    details = f"""
    \\x1b[30;105mXuan-1998@GitHub\\x1b[0m
    ----------------
    \\x1b[96mRole:    \\x1b[93mSr. HPC/AI Engineer @ AWS Annapurna Labs\\x1b[0m
    \\x1b[96mAffil:   \\x1b[93mResearch Affiliate @ MIT\\x1b[0m
    \\x1b[96mPhD:     \\x1b[93mUC Berkeley\\x1b[0m
    \\x1b[96mPrev:    \\x1b[93mGoogle, Lawrence Berkeley National Lab\\x1b[0m
    \\x1b[96mFocus:   \\x1b[93mDistributed Training, GPU Networking, MoE\\x1b[0m

    \\x1b[30;105mGitHub Stats:\\x1b[0m
    ----------------
    \\x1b[96mFollowers:   \\x1b[93m{git_stats.total_followers}\\x1b[0m
    \\x1b[96mTotal Stars: \\x1b[93m{git_stats.total_stargazers}\\x1b[0m
    \\x1b[96mCommits:     \\x1b[93m{git_stats.total_commits_last_year}\\x1b[0m
    \\x1b[96mPRs:         \\x1b[93m{git_stats.total_pull_requests_made}\\x1b[0m
    \\x1b[96mContribs:    \\x1b[93m{git_stats.total_repo_contributions}\\x1b[0m
    \\x1b[96mTop Langs:   \\x1b[93m{', '.join(top_langs[:5])}\\x1b[0m
    """

    t.toggle_show_cursor(False)
    t.gen_text(details, 9, 5, count=5, contin=True)
    t.toggle_show_cursor(True)
    t.gen_prompt(t.curr_row)
    t.gen_typing_text(
        "\\x1b[92m# Building the future of distributed AI \\x1b[0m",
        t.curr_row,
        contin=True,
    )
    t.gen_text("", t.curr_row, count=100, contin=True)

    t.gen_gif()

    readme_content = open("README.template.md").read()
    readme_content = readme_content.replace("{{TIMESTAMP}}", time_now)
    with open("README.md", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()
