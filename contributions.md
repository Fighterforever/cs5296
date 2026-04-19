# Team contributions — CS5296 Group 24

This document records who led which part of the work on our final
project, for grader transparency and to help future readers of this
repository navigate who to ask about what.

## Members

- **Ma Liyu** (liyuma2, 59072966)
- **Zheng Junlan** (junlzheng4, 59507980)
- **Zheng Zelan** (zelazheng2, 59250714)

## Work breakdown

| Area                                     | Primary owner | Secondary reviewer |
|------------------------------------------|---------------|--------------------|
| Problem framing and literature review    | Ma Liyu       | Zheng Junlan       |
| FastAPI application + unit tests         | Ma Liyu       | Zheng Zelan        |
| Dockerfile and Lambda Web Adapter wiring | Ma Liyu       | Zheng Junlan       |
| Terraform modules (EC2, Fargate, Lambda) | Ma Liyu       | Zheng Zelan        |
| k6 scenarios (steady, burst, coldstart)  | Ma Liyu       | Zheng Junlan       |
| Mixed read/write scenario (70/30 GET/POST)| Zheng Junlan | Ma Liyu            |
| Bootstrap percentile / time-to-steady    | Ma Liyu       | Zheng Zelan        |
| Cost model + break-even derivation       | Zheng Zelan   | Ma Liyu            |
| Benchmark run orchestration on AWS       | Ma Liyu       | Zheng Junlan       |
| Figures and plots                        | Ma Liyu       | Zheng Zelan        |
| Report writing — abstract, intro, conclusion | Zheng Junlan | Ma Liyu          |
| Report writing — methodology, results    | Ma Liyu       | Zheng Zelan        |
| Report writing — discussion, related work | Zheng Zelan  | Zheng Junlan       |
| Demo slides and voiceover                | Zheng Junlan  | Zheng Zelan        |
| Demo video editing and upload            | Zheng Zelan   | Zheng Junlan       |

Every section was reviewed by at least one other member before merging
to `main`.

## How to reach us

- Course email: liyuma2@my.cityu.edu.hk,
  junlzheng4@my.cityu.edu.hk, zelazheng2@my.cityu.edu.hk
- GitHub: `github.com/Fighterforever/cs5296`

## Code-review discipline

All non-trivial changes went through a pull-request review before
merging to `main`. Commits are signed-off by the author whose GitHub
handle matches their CityU login name.
