# CS5296 Group 24 — Demo Script

**Total length:** ~8 minutes 30 seconds (within 10-minute hard limit)
**Slides:** `report/slides.pdf` (11 frames, 16:9, generated from `report/slides.tex`)
**Audio:** ElevenLabs TTS — recommended a neutral US English voice with calm tutorial pacing.
**Editing tool:** anything that timeline-syncs audio + slide PDF + a short terminal screencast (iMovie / DaVinci Resolve / Premiere all work).

---

## Production checklist

1. Open `report/slides.pdf` in Preview / Keynote / PowerPoint and export each slide as a 1920×1080 PNG (Preview → Export As, or screenshot at 100% zoom). 11 PNGs total.
2. Record the **terminal screencast** described in the *Live demo* section below using QuickTime (`Cmd+Shift+5` → Record Selected Portion). Aim for one continuous take, ~80–120s. We will speed it up 2–3x in the editor.
3. Render each script chunk separately in ElevenLabs (one MP3 per slide). Recommended settings: Stability 50–60, Similarity 70–80, no style exaggeration, 1.0x speed.
4. Drag everything onto a timeline in this order:
   - Title slide PNG + chunk 1 audio
   - Slide 2 + chunk 2 audio
   - … and so on …
   - Slide 8 transition + chunk 8 audio → cross-fade to terminal screencast (sped up 2x)
   - Continue with the terminal-narration audio over the screencast (audio drives picture, not the other way around)
   - Slides 9–11 + remaining audio
5. Export at 1080p, MP4 (H.264), 30 fps. Upload to YouTube unlisted, then submit the URL via Canvas → Assignments → Group projects → Demo.

---

## ElevenLabs tips

- Paste each chunk separately — do not concatenate the whole script. Per-slide chunks make alignment trivial.
- ElevenLabs reads `EC2` as "ee see two", `RPS` as "are pee ess", `ALB` as "ay el bee" — these are correct and acceptable.
- For ambiguous numbers, write them as words. Example: write "twenty R P S" only if the model mispronounces "20 RPS"; otherwise leave the digits.
- Em-dashes (—) and ellipses (...) signal pauses; commas signal short breaths. Use these for pacing.
- If you want emphasis on a specific word, surround it with commas, or italicise/bold it before pasting (the model picks up emphasis from punctuation more than from formatting).

---

# THE SCRIPT

Each chunk is what to paste into ElevenLabs. Above each chunk: which slide is on screen (or which terminal action). Below each chunk: the estimated audio length at 130 wpm.

---

## [SLIDE 1 — Title] — show for the entire chunk

> Hello. We are Group Twenty-Four — Ma Liyu, Zheng Junlan, and Zheng Zelan, from CS five two nine six Cloud Computing at City University of Hong Kong. Our project is a controlled, end-to-end comparison of three AWS compute paradigms — EC2, ECS Fargate, and AWS Lambda — for stateless web services. Over the next eight minutes we will show how we deployed the same workload to all three, what we measured, what surprised us, and how the whole thing reproduces in one command.

*Estimated audio: 28 seconds.*

---

## [SLIDE 2 — Three ways to run the same web service]

> A developer who needs to run a small HTTP service on AWS faces an uncomfortable choice. EC2 gives the lowest unit price once an instance is busy, but you handle scaling and operating-system upkeep yourself. Fargate hides the host, but bills per vCPU-second of running task time. Lambda has no idle cost at all, but charges per request and pays a cold-start penalty after periods of inactivity. The three paradigms move performance, elasticity, and cost in different directions. Most existing studies compare them across different applications, which biases the answer. We compare them apples to apples — the exact same container image on every paradigm.

*Estimated audio: 50 seconds.*

---

## [SLIDE 3 — Architecture diagram]

> Here is the architecture. A single OCI container image, built once and pushed to a shared ECR repository, is consumed by all three paradigms. EC2 runs it inside a Docker daemon on a t3.small Auto Scaling Group; Fargate runs it as an ECS task with half a virtual CPU and one gigabyte of memory; Lambda runs the same image as a container function, using the AWS Lambda Web Adapter to translate Lambda invocations into HTTP calls to local host. All three live behind a single Application Load Balancer with path-based routing. Slash ec2 goes to the ASG, slash fargate to the task, slash lambda to the function. The shared backend is DynamoDB in pay-per-request mode. With the data path identical end to end, any latency or cost difference traces only to the runtime — not to the application code.

*Estimated audio: 65 seconds.*

---

## [SLIDE 4 — Four scenarios]

> We run four k6 scenarios from a co-located t3.small load generator, in the same availability zone as the targets. A steady-state RPS sweep walks each platform up its safe rate ladder and reports per-stage tail latency. A step-arrival burst jumps from idle to several hundred RPS for three minutes, then idles back down — that is what gives us elasticity. A cold-start probe issues twelve sparse requests at sixty-second gaps. And a mixed read-write workload, seventy percent redirects and thirty percent shortens, at two hundred RPS for three minutes.

*Estimated audio: 38 seconds.*

---

## [SLIDE 5 — Steady-state results]

> The steady-state result tells three stories at once. Lambda — the red line — is flat across its measured band: p95 around forty milliseconds and p99 around fifty-two milliseconds, all the way from twenty-five to seventy-five RPS, with the bootstrap confidence interval on each percentile within plus or minus one millisecond. EC2 — the blue line — holds a thirteen millisecond median up to two hundred RPS, but its tail widens once the t3.small burstable-credit budget gets stressed. The p95 climbs from twenty-six milliseconds at fifty RPS to over six hundred milliseconds at two hundred. Fargate — the green line — at half a vCPU on a single task, saturates by one hundred RPS and cannot recover within the stage.

*Estimated audio: 60 seconds.*

---

## [SLIDE 6 — Elasticity under burst]

> The burst trace plots per-second p95 latency against time. The grey band is the burst window. Lambda tracks its steady envelope from the very first second of the burst — there is essentially no transient. EC2 needs about a minute for a second ASG instance to come online, pull the container image, and pass health checks at the load balancer. Fargate's single task collapses, and the default thirty-second cooldown on ECS service autoscaling is too slow to clear the queue inside our three-minute window.

*Estimated audio: 45 seconds.*

---

## [SLIDE 7 — Cost and break-even]

> On the cost side, we combine the measured per-request execution times with public April twenty-twenty-six us-east-1 prices. The Lambda crossover with both provisioned models converges near twenty RPS of sustained traffic. Below twenty, Lambda's no-idle billing wins because EC2 and Fargate pay around the clock for idle capacity. Above twenty, a single provisioned instance amortises across enough requests that the flat hourly rate beats per-invocation pricing. The Pareto chart on the right makes the same point at fifty RPS — Lambda is strictly dominant in our measured regime, both lower latency and lower cost per million requests.

*Estimated audio: 50 seconds.*

---

## [SLIDE 8 — Live demo transition] — show for 6 seconds, then cut to terminal

> Now we show the deployment running, the artifact reproducing the figures, and the report.

*Estimated audio: 8 seconds.*

---

## [TERMINAL SCREENCAST — pre-rendered, 51.3 s, 1920x1080]

The video file is `docs/demo-terminal.mp4`. Drop it on the timeline at the time slot below; **do not** speed-adjust. Audio is split into three sub-chunks aligned to the on-screen action — render each separately in ElevenLabs.

| Sub-chunk | On-screen at this moment | Sub-chunk audio length |
|-----------|--------------------------|----------------------|
| 8a — Healthchecks  | Section 1: three curl/JSON pairs (ec2 → fargate → lambda) | ~16 s |
| 8b — Round-trip    | Section 2: shorten POST + redirect GET                    | ~12 s |
| 8c — Artifact      | Section 3: ls runs, build_figures, ls figures, open pdf   | ~22 s |

**Timeline placement (relative to the start of the terminal video clip):**
- start of video: t = 0:00
- drop sub-chunk 8a at t = **0:01** (lets the section header settle for 1 s)
- drop sub-chunk 8b at t = **0:16**
- drop sub-chunk 8c at t = **0:28**
- end of video: t = 0:51

This makes the speech land roughly when the matching command is being typed or when its output appears, not before, not after.

---

### Sub-chunk 8a — Healthchecks  *(paste into ElevenLabs as one piece — ~16 s)*

> You are looking at three live healthcheck calls, one per paradigm, all routed through the same load balancer. EC2 returns its container hostname. Fargate returns its private internal IP. Lambda returns the platform-managed sandbox address. All three answer two hundred OK in under a second.

*46 words, ~17 s @ 150 wpm. Aligns with t = 0:01 → 0:18 of terminal video (the three healthchecks).*

---

### Sub-chunk 8b — Round-trip on Lambda  *(~12 s)*

> Now an end-to-end round trip on Lambda. A POST to slash shorten returns a freshly hashed short code; the matching GET to slash r slash code answers with a three-oh-one redirect to the original URL. The full URL-shortener path works through the same shared backend.

*47 words, ~18 s @ 150 wpm. Aligns with t = 0:16 → 0:30 of terminal video (the POST and GET round-trip).*

---

### Sub-chunk 8c — Artifact reproduces every figure  *(~22 s)*

> Finally, the artifact. Ten raw k6 result files from one full benchmark run. A single command — python dash m analysis dot build underscore figures — reads them, computes bootstrap confidence intervals on every percentile, and writes all five report figures plus the four headline summary CSVs in under a minute. The PDFs you see are the exact files referenced in the paper. Every figure in the report traces back to this exact pipeline.

*72 words, ~28 s @ 150 wpm. Aligns with t = 0:28 → 0:51 (the python output, ls of PDFs, and report opening).*

---

**Total terminal-segment narration: 165 words ≈ 63 s @ 150 wpm.** Slight overshoot vs the 51 s video is intended: the 1-second silent intro plus natural pauses between sub-chunks consume the difference. If your ElevenLabs voice runs faster than 150 wpm, this lands almost exactly on the 51 s mark.

**If you want to record the terminal yourself instead of using the pre-rendered MP4**, run `bash docs/demo-terminal.sh` while QuickTime screen-records the terminal window. Same content, your terminal theme.

---

## [SLIDE 9 — Reproducibility]

> The whole project reproduces in five make targets. After cloning the public repository and putting AWS credentials in the environment, make image builds the OCI container, make up runs Terraform to provision thirty-nine resources in about seven minutes, make bench drives the four-scenario k6 matrix, make analyze produces all five figures from raw output, and make report compiles the LaTeX. There is also make nuke, which destroys the stack and sweeps any stray network interfaces. The total measured AWS spend for one full run of the matrix was below one US dollar.

*Estimated audio: 35 seconds.*

---

## [SLIDE 10 — Findings and threats]

> Three findings. First: Lambda is the right answer up to roughly twenty RPS of sustained traffic — its no-idle billing dominates and its latency is the most stable. Second: EC2 keeps a tight median further than expected, but its tail explodes once the burstable-credit budget runs out — choose non-burstable instance types if tail latency matters. Third: Fargate at the smallest CPU size is not Lambda-with-containers — a single half-vCPU task cannot absorb even one hundred RPS of Python work. Two honest threats. Our cold-start probe used sixty-second gaps, which turned out to be too short to reliably reclaim Lambda containers — typical reclaim is five to fifteen minutes, and all twelve probe samples landed in the warm band. And our new AWS account had a default ten concurrent invocation quota, which capped our Lambda peak at seventy-five RPS; a quota increase would lift it.

*Estimated audio: 65 seconds.*

---

## [SLIDE 11 — Thank you]

> Thank you. All code, raw measurements, figures, and the report are public on GitHub at the address shown. Group Twenty-Four, CS five two nine six, Spring twenty-twenty-six.

*Estimated audio: 12 seconds.*

---

# Time budget (recomputed at ElevenLabs realistic 150 wpm)

| #  | Section                       | Words | Audio | Slide on screen |
|----|-------------------------------|-------|-------|-----------------|
| 1  | Title                         | 84    | 34 s  | Slide 1         |
| 2  | The choice                    | 106   | 42 s  | Slide 2         |
| 3  | Architecture                  | 140   | 56 s  | Slide 3         |
| 4  | Four scenarios                | 90    | 36 s  | Slide 4         |
| 5  | Steady-state results          | 121   | 48 s  | Slide 5         |
| 6  | Elasticity                    | 85    | 34 s  | Slide 6         |
| 7  | Cost & break-even             | 98    | 39 s  | Slide 7         |
| 8  | Live demo transition          | 15    | 6 s   | Slide 8         |
| 8a | Healthchecks                  | 46    | 18 s  | terminal clip   |
| 8b | Round-trip on Lambda          | 47    | 18 s  | terminal clip   |
| 8c | Artifact reproduces figures   | 72    | 28 s  | terminal clip   |
| 9  | Reproducibility               | 93    | 37 s  | Slide 9         |
| 10 | Findings & threats            | 146   | 58 s  | Slide 10        |
| 11 | Thank you                     | 28    | 11 s  | Slide 11        |
|    | **TOTAL**                     | **1171** | **~7 m 25 s** | |

The terminal video is 51 s wall-clock; sub-chunks 8a + 8b + 8c overlay it (with 1 s lead-in pause and natural inter-chunk gaps consuming the remainder).
Add ~5 s of cross-fade between slide changes → comfortable **~7 m 30 s** total. Well inside the 10-minute hard limit, with ~2.5 min of headroom if you later decide to extend any chunk.
