#!/usr/bin/env python3
import argparse, os, sys, subprocess, pathlib, shutil

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-path", required=True)
    ap.add_argument("--prompt-path", required=True)
    ap.add_argument("--llm-provider", required=True, choices=["openai","openai_compat","grok"])
    ap.add_argument("--llm-model", required=True)
    ap.add_argument("--enable-browsing", default="true")
    ap.add_argument("--enable-search", default="true")
    ap.add_argument("--logs", default="openhands_run")
    args = ap.parse_args()

    os.makedirs(args.logs, exist_ok=True)

    env = os.environ.copy()

    # Map provider env expected by your OpenHands build
    if args.llm_provider == "openai":
        # expects OPENAI_API_KEY in env
        env["OPENAI_MODEL"] = args.llm_model
    elif args.llm_provider == "openai_compat":
        # expects OPENAI_API_KEY + OPENAI_BASE_URL in env
        env["OPENAI_MODEL"] = args.llm_model
    elif args.llm_provider == "grok":
        # expects GROK_API_KEY in env
        env["GROK_MODEL"] = args.llm_model

    env["OH_ENABLE_BROWSING"] = args.enable_browsing
    env["OH_ENABLE_SEARCH"]   = args.enable_search

    goal_text = pathlib.Path(args.prompt_path).read_text(encoding="utf-8")

    # Prefer CLI if available; otherwise try module invocation
    if shutil.which("openhands"):
        cmd = ["openhands", "run",
               "--repo", args.repo_path,
               "--goal", goal_text,
               "--logs", args.logs]
    else:
        cmd = [sys.executable, "-m", "openhands",
               "run",
               "--repo", args.repo_path,
               "--goal", goal_text,
               "--logs", args.logs]

    print("Running:", " ".join(cmd), flush=True)
    rc = subprocess.call(cmd, env=env)
    sys.exit(rc)

if __name__ == "__main__":
    main()
