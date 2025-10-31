#!/usr/bin/env python3
import argparse, json, os, sys, pathlib, datetime, re

def render(template: str, ctx: dict) -> str:
    out = template
    for k, v in ctx.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    # collapse any accidental double spaces left by replacements
    out = re.sub(r"[ \t]+", " ", out)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", required=True, help="Path to country-profiles.json")
    ap.add_argument("--profile-key", required=True, help="Key in JSON, e.g., UAE, SG, UK")
    ap.add_argument("--template", required=True, help="Path to prompt template .md")
    ap.add_argument("--output", required=True, help="Output path for rendered prompt .md (inside docs_repo)")
    args = ap.parse_args()

    profiles = json.loads(pathlib.Path(args.profiles).read_text(encoding="utf-8"))
    if args.profile_key not in profiles:
        print(f"Profile '{args.profile_key}' not found. Available: {', '.join(sorted(profiles.keys()))}", file=sys.stderr)
        sys.exit(2)

    p = profiles[args.profile_key]
    regs_csv = ", ".join(p.get("regulators", []))

    folders = p.get("folders", {})
    f_family = folders.get("family_office", "family-office/{code}/").replace("{code}", p["country_code"])
    f_risk   = folders.get("risk_management", "risk-management/{code}/").replace("{code}", p["country_code"])
    f_wealth = folders.get("wealth_management", "wealth-management/{code}/").replace("{code}", p["country_code"])

    ctx = {
        "COUNTRY_NAME": p["country_name"],
        "COUNTRY_CODE": p["country_code"],
        "REGULATORS_CSV": regs_csv,
        "FOLDER_FAMILY_OFFICE": f_family,
        "FOLDER_RISK_MANAGEMENT": f_risk,
        "FOLDER_WEALTH_MANAGEMENT": f_wealth,
    }

    tpl = pathlib.Path(args.template).read_text(encoding="utf-8")
    rendered = render(tpl, ctx)

    out_path = pathlib.Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote rendered prompt to: {out_path}")

if __name__ == "__main__":
    main()
