# Week 9 evidence index

Repository: [CloudWizardBoricua/sdi4213-week9-devsecops](https://github.com/CloudWizardBoricua/sdi4213-week9-devsecops).

The [submission PDF](../../output/pdf/Week9_DevSecOps_Evidence.pdf) contains ten labeled screenshots and four reflections. Execution records were captured on October 25, 2026; JSON metadata uses UTC. Screenshots and the final PDF are added after the security PR so that its completed checks can be documented.

## Capture provenance

Milestones 1, 2, 4, 5, and 7 are genuine browser screenshots of a read-only transcript viewer displaying captured command stdout/stderr. They are explicitly labeled as transcript views, not screenshots of a native terminal. `scripts/record_evidence.py` executes each command and saves its arguments, timestamps, exit code, and unmodified output; `scripts/build_evidence_views.py` displays those records, with excerpts labeled and linked to the full log. No command results or check states are invented.

Milestones 3, 6, 8, 9, and 10 are captured from the public GitHub repository. Supplementary screenshots show the running application. No screenshot contains `.env` contents or an authentication credential.

## Milestones and captions

| Milestone | Screenshot | One-sentence caption |
| --- | --- | --- |
| 1 - Baseline application and tests | [Image](screenshots/milestone-01.png) | Both original tests pass in the unchanged Python 3.13 baseline image before Dockerfile hardening. |
| 2 - .env protected from Git | [Image](screenshots/milestone-02.png) | Git ignores `.env` and confirms that it is not tracked, without exposing its contents. |
| 3 - Dependabot configured | [Image](screenshots/milestone-03.png) | The configuration published on GitHub schedules weekly updates for pip and GitHub Actions. |
| 4 - Baseline Docker Scout CVE scan | [Image](screenshots/milestone-04.png) | Scout reports 5 critical, 41 high, 23 medium, and 28 low findings in `helpdesk:week9-before`. |
| 5 - Docker Scout recommendations / SBOM evidence | [Image](screenshots/milestone-05.png) | Scout identifies the Python 3.13 slim base as up to date while still listing known base-image vulnerabilities. |
| 6 - Dockerfile hardened to non-root | [Image](screenshots/milestone-06.png) | The Dockerfile creates `appuser`, assigns ownership, and selects that user before the application command. |
| 7 - Non-root container verification | [Image](screenshots/milestone-07.png) | The hardened image returns UID 10001, compared with UID 0 in the preserved baseline image. |
| 8 - Security workflow added | [Image](screenshots/milestone-08.png) | The published workflow rejects tracked `.env` files, builds the image, and requires a non-zero runtime UID. |
| 9 - GitHub Actions security checks passing | [Image](screenshots/milestone-09.png) | GitHub Actions completes the security-policy job successfully for the security pull request. |
| 10 - Final pull request and reflection | [Image](screenshots/milestone-10.png) | The final security pull request records successful checks and the reviewed changes before merge. |

## Verification records

- [Baseline tests](logs/baseline-tests.txt), [services](logs/baseline-services.txt), [application screenshot](screenshots/baseline-application.png)
- [Baseline image identity](logs/baseline-image.txt), [CVE scan](logs/baseline-cves.txt), [recommendations](logs/baseline-recommendations.txt), [package inventory](logs/baseline-sbom.txt)
- [Hardened tests](logs/hardened-tests.txt), [UID](logs/hardened-uid.txt), [four positive/negative policy scenarios](logs/policy-scenarios.txt)
- [PostgreSQL record before recreation](logs/postgres-before-recreate.txt), [after recreation](logs/postgres-after-recreate.txt), [final service status](logs/final-services.txt)
- [Running Compose user](logs/compose-uid.txt), [Adminer HTTP response](logs/adminer-health.txt)

The starter's PostgreSQL 18 volume target was repaired before the baseline was established. Local host-port overrides avoid existing Week 7 services and a Windows-reserved port. The baseline Dockerfile and original application/test code were unchanged at baseline scan time. All package versions from the starter remain pinned as supplied.

Scout emitted a Windows temporary-archive cleanup warning, but returned exit code 0 with a complete report. Its full warning is retained in the raw log. Recorded findings describe that image and advisory database at scan time; later scans can differ.

## Milestone 10 reflections

### What security problem does running a container as non-root reduce?

Running the application as UID 10001 reduces the privileges available if an attacker compromises the application process. Compared with root, the account has fewer opportunities to alter protected operating-system files or perform privileged actions inside the container. This is defense in depth; it does not patch vulnerable packages or guarantee protection from every container escape.

### What did Docker Scout identify that normal functional tests would not identify?

Scout matched the baseline software inventory to 97 known vulnerability findings, including five critical findings associated with Pillow 11.3.0. The two functional tests passed because they check request storage and status changes, not dependency advisories. These results show why functional correctness and vulnerability analysis answer different questions.

### Why is .env.example appropriate for Git while .env usually is not?

`.env.example` documents required variable names and uses a conspicuous placeholder instead of a real password. A local `.env` can contain working credentials, so publishing it would expose configuration intended to remain on the developer's machine. Ignore rules protect normal workflows, while CI catches a root `.env` that was forcibly added to Git.

### How does the security workflow turn a security expectation into an enforceable pipeline policy?

The workflow checks Git's index, builds the image, and evaluates its actual runtime UID on pushes and pull requests targeting `main`. A tracked `.env`, failed build, or root UID makes the job fail instead of relying solely on a manual checklist. Requiring that check through branch protection can additionally prevent merging a failing PR; the workflow itself supplies the automated pass/fail evidence.
