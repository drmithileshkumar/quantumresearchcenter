# Daily editorial automation

Produces one sourced article, a narrated 720p slide video and an X link post per
publication date. The default is **18:00 Asia/Kolkata**, with AI narration. The
public site remains static. This is separate from `content/DAILY-UPDATE.md`'s
paper-curation routine; neither invokes the other.

## Setup

Use a dedicated, clean checkout on `main` on a Linux machine that stays online.
Keep the production checkout separate from your normal development checkout.
Git must already have permission to push to `origin/main`; the existing GitHub
Actions deployment publishes the website after checks pass. Branch protection
must permit this automation, otherwise use the manual article/PR path below.

```sh
python3 -m pip install -r requirements.txt -r scripts/editorial/requirements.txt
python3 scripts/editorial_pipeline.py --help
```

Provide these environment variables through your host's secret manager or a
private environment file **outside the repository**. Do not paste tokens into
chat, commit them, or place them in a public web directory.

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Research, writing, technical review and speech |
| `OPENAI_MODEL` | Explicit model ID supporting Responses web search and JSON output |
| `OPENAI_TTS_MODEL` | Optional; defaults to `gpt-4o-mini-tts` |
| `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` | Google OAuth application |
| `YOUTUBE_REFRESH_TOKEN` | Channel-owner OAuth token with `youtube.upload` permission |
| `X_ACCESS_TOKEN` | User-context OAuth access token with permission to create posts; not an app-only token |
| `QRC_FONT` | Optional font path; defaults to Linux DejaVu Sans |

Configure platform OAuth apps and obtain credentials through their normal
authorization flows. This implementation does not provision accounts, handle X
token refresh, or configure platform billing. Use a credential manager to renew
X access tokens when needed. Check current API access/quotas in the platforms'
developer consoles. Configure spend limits before enabling unattended LLM calls.

Edit `config.json` for topic rotation, author, voice, site URL, timezone and
publication time. The topic rotation is a starter backlog, not a guarantee of
fresh daily news. Maintain it weekly; the research step checks existing article
titles but semantic duplication still needs editorial review.

## First package

```sh
python3 scripts/editorial_pipeline.py run --topic "Introduce measurement-based quantum computing"
```

`run` now advances through separate editorial stages and stops at each review:

1. **Article:** research, generate the article only, and run technical review.
   Read `preview.html` and `review.json`; edit the article in `package.json`.
2. **Article approval:** after proofreading and corrections, approve the text.
3. **Animated slides:** create a storyboard and narration script from that exact
   article, then render `slides.mp4` without voice. Slides have fade-ins and a
   gentle zoom. Review the slide video and the script in `preview.html`.
4. **Slide approval:** approve the slides and narration script.
5. **Voice and video:** generate AI narration and render `video.mp4` using the
   same slide effects, extending each slide to its narration length.
6. **Final approval:** review the complete video and approve publication.

```sh
# Stage 1: article only; does not create slides or audio
python3 scripts/editorial_pipeline.py prepare --date 2026-11-02 --topic "Measurement-based quantum computing"
# After editing package.json, rerun the technical article review
python3 scripts/editorial_pipeline.py review --date 2026-11-02
python3 scripts/editorial_pipeline.py approve-article --date 2026-11-02 --editor "Your name"
# Stage 2: animated slides and written narration script, no generated voice
python3 scripts/editorial_pipeline.py slides --date 2026-11-02
python3 scripts/editorial_pipeline.py approve-slides --date 2026-11-02 --editor "Your name"
# Stage 3: add voice and render final video
python3 scripts/editorial_pipeline.py render --date 2026-11-02
python3 scripts/editorial_pipeline.py approve --date 2026-11-02 --editor "Your name"
python3 scripts/editorial_pipeline.py publish --date 2026-11-02
```

Use the package's actual date. Requests use the Responses API directly; no
additional agent framework is required. `run` performs the next production step
once its preceding approval exists; it never grants approvals itself.

Artifacts are stored in `content/.production/YYYY-MM-DD/`, gitignored and
excluded from the public site. Back this directory up privately: it contains
approvals and delivery records. A custom `--work-dir` should be outside the
repository and outside any public web directory.

Article edits invalidate article approval and downstream work. After approving
a revised article, run `slides` to regenerate the storyboard. For slide or script
edits with the article unchanged, edit `package.json` and run `slides` to rebuild
the silent preview, then approve slides again. Voice cannot be generated before
slide approval. Final approval binds the package, research, review and video to
content hashes; configuration changes also invalidate final approval.

The HTML preview shows TeX source rather than MathJax. Current animations are
presentation effects, not scientific simulations or animated circuit diagrams.
Custom scientific diagrams, synchronized captions and recorded human narration
are not implemented. No third-party figures are copied automatically. Model
review assists your proofreading; it does not establish scientific correctness.
`render --silent` rebuilds the animated slide preview after article approval.

## Scheduling

On the production host, create a private wrapper (outside the repo) which loads
credentials, changes into the dedicated checkout, and runs:

```sh
python3 scripts/editorial_pipeline.py run
```

Schedule that wrapper every 30 minutes using cron or your host scheduler. Example
crontab entry, replacing the paths with your own:

```cron
*/30 * * * * /absolute/private/run-qrc-editorial >> /absolute/private/qrc-editorial.log 2>&1
```

It prepares an article once per date, waits at each review stage, and publishes when the
configured local time is reached. Cron is approximate, so delivery may occur
up to 30 minutes later, plus build/upload time. Keep the machine awake. No cron
job is installed automatically. To prepare tomorrow or publish an older approved
package, invoke `run --date YYYY-MM-DD` explicitly; today's job never silently
publishes a previous day's backlog.

## Delivery and recovery

1. Check article, slide and final approvals, due time and required credentials.
2. Require a clean `main` checkout. Refuse an existing article slug.
3. Add only the approved article JSON; build, link-check and test the site.
4. Commit that article and push. Failed build/test gates remove its source and
   rebuild the previous site. No user files are reset or discarded.
5. Wait for a later scheduled invocation if the new article is not live yet.
6. Upload the narrated video to YouTube as public; wait for public availability.
7. Post the article link on X. The video description links back to the article.

The publisher records each channel in `delivery.json`. Completed channels are
skipped. It saves `started` **before** external writes; a crash or ambiguous API
error stops automatic retries for that channel, avoiding duplicate publication.
To recover, first inspect the actual platform. If delivery succeeded, change
that entry to `{"status":"done","result":...}` using its verified commit,
video ID (`{"id":"..."}`), or X post ID. If it definitely did not succeed,
remove only that channel entry and retry. For a successful commit but failed
push, push the existing commit and record it; do not create another article.
Keep a backup of the ledger before editing. Do not delete it to force a retry.

Lock files prevent concurrent writes to a package. After a crashed process,
confirm it has stopped before deleting that package's `.lock` file. Run only
one production checkout per publication stream.

If automatic git pushes are unsuitable, copy the reviewed article from
`package.json` to `content/news-articles/<slug>.json`, set status to `published`
when ready, and use your normal PR/deployment procedure. Then reconcile the
website channel before resuming the other deliveries.

## Checks and limitations

```sh
python3 -m unittest discover -s tests -p 'test_editorial_pipeline.py' -v
```

Automated tests use mocked provider responses and temporary packages. Live API
quality, OAuth, quotas, deployment timing, and channel ownership must be tested
with your credentials. The initial pipeline does not embed the YouTube video
into the article, refresh X tokens, or gather analytics. It intentionally stops
on failed reviews rather than spending indefinitely on automatic rewrites.

API references: [Responses](https://developers.openai.com/api/reference/resources/responses/methods/create),
[web search](https://developers.openai.com/api/docs/guides/tools-web-search),
[speech](https://developers.openai.com/api/docs/guides/text-to-speech),
[YouTube upload](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert),
[X posts](https://docs.x.com/x-api/posts/create-post).
