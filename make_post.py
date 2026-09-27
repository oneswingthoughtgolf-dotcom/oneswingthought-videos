"""Build today's One Swing Thought post.

Usage: python3 make_post.py            -> renders the next tip, writes post.json, advances state.json
       python3 make_post.py --day N    -> renders a specific tip without touching state.json

Tips come from tips.json (days 1-30). After day 30 the daily run appends new tips to tips.json
before calling this script (see RUNBOOK.md).
"""
import json, os, sys
from render import render

HASHTAGS = {
    "Swing Fix": "#golf #golftips #golfswing #golfinstruction #oneswingthought",
    "Short Game": "#golf #shortgame #chipping #golftips #oneswingthought",
    "Putting": "#golf #putting #puttingtips #golftips #oneswingthought",
    "Drill": "#golf #golfdrills #golfpractice #golftips #oneswingthought",
    "Course Smarts": "#golf #coursemanagement #golfstrategy #breaking90 #oneswingthought",
    "Myth vs. Fact": "#golf #golftips #golfmyths #golfbeginner #oneswingthought",
    "Mental Game": "#golf #mentalgame #golfmindset #golflife #oneswingthought",
}

def main():
    tips = json.load(open("tips.json"))
    state = json.load(open("state.json"))
    fixed = "--day" in sys.argv
    day = int(sys.argv[sys.argv.index("--day") + 1]) if fixed else state["next_day"]
    tip = next((t for t in tips if t["day"] == day), None)
    if tip is None:
        sys.exit(f"NO_TIP_FOR_DAY {day}: add it to tips.json first")
    tip = dict(tip, label=f"{tip['pillar']} · Day {day}")
    os.makedirs("videos", exist_ok=True)
    fname = f"videos/day{day:03d}.mp4"
    render(tip, fname)
    caption = (f"{tip['thought']}\n\nTry it on your next range session and see what changes.\n\n"
               f"{tip['question']}\n\n(Lefties: flip it.)\n\n{HASHTAGS.get(tip['pillar'], HASHTAGS['Swing Fix'])}")
    post = {"day": day, "file": fname, "title": tip["hook"][:95], "caption": caption, "pillar": tip["pillar"]}
    json.dump(post, open("post.json", "w"), indent=1)
    if not fixed:
        state["next_day"] = day + 1
        state["history"].append({"day": day, "file": fname})
        json.dump(state, open("state.json", "w"), indent=1)
    print(json.dumps(post))

if __name__ == "__main__":
    main()
