# Demo video script (≤ 10 min, English only)

Resolution: at least 1280×720 (project requirement: ≥640×480).
Tools: macOS Cmd-Shift-5 to record; iMovie or DaVinci Resolve to edit.
Use captions on every slide.

---

## Shot list and timing

| # | Time   | Shot                                 | What is on screen                                              | Voiceover (read at normal pace) |
|---|--------|--------------------------------------|---------------------------------------------------------------|---------------------------------|
| 1 | 0:00–0:25 | Title slide                       | Title, three names + group ID, course tag                      | "We compare three native AWS deployment paradigms — EC2, ECS Fargate, and Lambda — for the same web service, in one controlled experiment." |
| 2 | 0:25–1:15 | Slide: the question               | Three logos with three different billing models, prompt: "which one should I pick?" | "Picking among them is hard because performance, elasticity, and cost don't usually point in the same direction. We answer this with measurements, not vendor brochures." |
| 3 | 1:15–2:30 | Architecture diagram (the figure from the report) | Slide: one image, three runtimes, one ALB | "We package a FastAPI URL-shortener as a single OCI container. The AWS Lambda Web Adapter lets the same image run on Lambda. EC2 uses an Auto Scaling Group; Fargate runs a 0.5 vCPU task; Lambda is a 1 GB container function. All three sit behind one Application Load Balancer so the data path is identical." |
| 4 | 2:30–3:30 | Terminal: `tofu apply` (sped-up) and `aws ecr describe-images` | Show ECR repo, ALB DNS, Lambda function URL output | "One Terraform run brings all 26 resources up. Everything references the Learner Lab role, no IAM creation, fully reproducible." |
| 5 | 3:30–5:00 | Live curl: shorten + redirect on each platform | Three browser tabs / curl outputs showing 200 + 301 from each | "End-to-end shorten-then-redirect works on all three. Notice the platform header in the response — that confirms which runtime served the call." |
| 6 | 5:00–6:30 | Terminal: `bash benchmark/run.sh` (sped-up) and CloudWatch Lambda metric graph | Show k6 progress, ECS task count climbing, Lambda concurrency rising | "k6 runs four scenarios from a co-located c5.large worker. The autoscaler reactions are visible in CloudWatch." |
| 7 | 6:30–8:00 | Slide: Steady latency figure       | The steady_latency_vs_rps PDF                                  | "EC2 holds the lowest tail latency at every load. Fargate tracks within roughly 2x. Lambda's curve is the noisiest because every container spawn pays a cold init." |
| 8 | 8:00–8:45 | Slide: Elasticity trace            | The elasticity_p95_trace PDF                                   | "Under a step burst, Fargate stabilises in about 25 seconds. EC2 takes a full minute waiting for a fresh VM. Lambda spikes hardest on the very first second but then absorbs the load fastest." |
| 9 | 8:45–9:20 | Slide: Cost-vs-RPS                 | The cost_vs_rps PDF                                            | "Combining the measured per-request latency with public April 2026 pricing gives explicit break-even points. Lambda dominates Fargate up to about 17 RPS and EC2 up to about 60 RPS for our 1 GB workload." |
|10 | 9:20–9:55 | Slide: take-aways + repo URL       | 3-bullet take-aways + GitHub link                              | "Take-aways: Lambda for sparse traffic; Fargate when traffic is bursty but known; EC2 once you can amortise a fixed instance. Code, Terraform, k6, analysis and the report itself are all in this public repo." |
|11 | 9:55–10:00 | End card                          | Thanks slide                                                   | "Thanks for watching." |

---

## Caption style

* All captions in white sans-serif, 24pt, bottom centred, translucent black background.
* Each scene has its number ("1/11") in the top-right of the screen.
* Highlight numbers and product names in **bold yellow** the moment they are spoken.

## Recording tips

* Quit Slack/Mail/Notification Center first. Hide the menu bar with `defaults write NSGlobalDomain _HIHideMenuBar -bool true; killall Finder`.
* Set Terminal to a 16pt monospace font; resize to 120×30.
* Do a full dry-run before recording — it makes the live narration shorter.
* Export the final video at 1920×1080, H.264, 8 Mbps; expected file size ≈ 350 MB.

## Upload

* YouTube → Unlisted → set the link to public when ready, copy URL.
* The link goes into Canvas → Group projects → Demo, alongside the report submission.
