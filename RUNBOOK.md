# One Swing Thought — daily run

Faceless golf-tip page. One 20-second vertical video a day to Instagram Reels, TikTok,
YouTube Shorts and Facebook Reels via Metricool. Owner: Nick (hands-off — don't ask him things
unless something is broken).

- Metricool brand: blogId **7099967**, timezone America/Phoenix
- Video host: this repo (public). Video URL pattern:
  `https://raw.githubusercontent.com/oneswingthoughtgolf-dotcom/oneswingthought-videos/main/<file>`
- Brand: clubhouse green #0F3729, cream #F5F1E8, gold #C9A24A; Lora italic + Poppins. Renderer handles it.

## Every day

1. `python3 make_post.py` → renders the next tip to `videos/dayNNN.mp4`, writes `post.json`, advances `state.json`.
   - If it exits with `NO_TIP_FOR_DAY`, first append 7 new tips to `tips.json` (next day numbers),
     following the rules below and the weekly pillar rotation, then rerun.
2. Look at one frame (e.g. `ffmpeg -ss 15 -i <file> -frames:v 1 check.png` and view it). Text must fit
   on screen, nothing cut off. If it overflows, shorten the tip's wording in tips.json and re-render.
3. `git add -A && git commit -m "Day N" && git push`.
4. Schedule in Metricool with `createScheduledPost` (blogId 7099967), media = the raw GitHub URL of the video,
   publish time today in America/Phoenix (use `getBestTimeToPostByNetwork` for instagram; if unavailable,
   12:15). Providers: instagram, tiktok, youtube, facebook. Network data:
   - instagramData: `{"type":"REEL","showReelOnFeed":true}`
   - facebookData: `{"type":"REEL","title":<title>}`
   - tiktokData: `{"title":<title>,"privacyOption":"PUBLIC_TO_EVERYONE","isAigc":true}` (title is required)
   - youtubeData: `{"title":<title> + " #shorts","type":"short","privacy":"public","category":"SPORTS","madeForKids":false,"tags":["golf","golf tips","golf swing"]}`
   - text = post.json caption.
   If one network rejects the post, retry once without that network and note it in the report.
5. Check `getScheduledPosts` for yesterday's post: if any network shows ERROR, mention it in the run summary.

## Sundays (in addition)
Pull last 7 days of analytics from Metricool (reach/views, watch time, saves, shares, followers per network).
Write a 5-line summary: followers, top video, weakest video, what changes next week. Lean next week's new
tips toward the best-performing pillar/hook style. Email the summary to Nick
(pricklypearjunkremoval@gmail.com) via Gmail if the Gmail connector is available.

## Tip-writing rules
- Weekly pillars: Mon Swing Fix · Tue Short Game · Wed Putting · Thu Drill · Fri Course Smarts · Sat Myth vs. Fact · Sun Mental Game.
- Only mainstream, widely taught fundamentals. No made-up stats. No injury/medical advice.
- Written for right-handers (caption says lefties flip it).
- hook ≤ 8 words, thought ≤ 12 words, 3 beats ≤ 12 words each, plus a comment-bait question.
- Never repeat a previous tip; vary hooks.
