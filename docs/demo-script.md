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

## [TERMINAL SCREENCAST — ~80 seconds raw, edit to ~60 seconds in timeline]

While the audio chunk below plays, the picture is a sped-up screencast of the following commands, run from your laptop with `AWS_PROFILE=cs5296`. Use a large monospace font (16pt+) so it is readable at 1080p.

**What to record (one take, ~80 seconds at normal pace):**

```bash
# 1) prove the three deployments are alive
ALB=http://cs5296-alb-550516460.us-east-1.elb.amazonaws.com
curl -s $ALB/ec2/healthz     | jq .
curl -s $ALB/fargate/healthz | jq .
curl -s $ALB/lambda/healthz  | jq .

# 2) round-trip on the redirect path against Lambda
curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"url":"https://example.com"}' \
     $ALB/lambda/shorten | jq .
# response shows {"code":"abc1234"}

curl -s -i $ALB/lambda/r/abc1234 | head -3
# response is 301 Moved Permanently to https://example.com

# 3) regenerate every figure from raw measurements
ls data/results/run-personal-20260418T154912Z/ | head
python -m analysis.build_figures run-personal-20260418T154912Z
ls report/figures/

# 4) open the report PDF
open report/main.pdf
```

**Editor: speed this clip 2x to 3x. Audio (chunk below) plays over it at normal speed.**

> What you are seeing is, first, three live healthcheck calls — one per paradigm, all returning two-hundred OK. Second, a real round-trip on the URL-shortener path: a POST to slash shorten returns a short code; a GET to slash r slash code returns a three-oh-one redirect. Third, a single command — python dash m analysis dot build underscore figures — reads the raw k6 CSV from this run and regenerates all five figures plus the headline summary CSVs in under a minute. And finally, the full report PDF opens, with every figure in the report sourced from this exact pipeline.

*Estimated audio: 60 seconds.*

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

# Time budget

| # | Section                       | Audio | Slide on screen |
|---|-------------------------------|-------|-----------------|
| 1 | Title                         | 28s   | Slide 1         |
| 2 | The choice                    | 50s   | Slide 2         |
| 3 | Architecture                  | 65s   | Slide 3         |
| 4 | Four scenarios                | 38s   | Slide 4         |
| 5 | Steady-state results          | 60s   | Slide 5         |
| 6 | Elasticity                    | 45s   | Slide 6         |
| 7 | Cost & break-even             | 50s   | Slide 7         |
| 8 | Live demo transition          | 8s    | Slide 8         |
|   | + Terminal screencast (sped)  | 60s   | terminal clip   |
| 9 | Reproducibility               | 35s   | Slide 9         |
| 10| Findings & threats            | 65s   | Slide 10        |
| 11| Thank you                     | 12s   | Slide 11        |
|   | **TOTAL**                     | **~8m 36s** | |

Adds 4–6 seconds of cross-fade between slides → comfortable 8m 50s total. Inside the 10-minute hard limit with margin.
