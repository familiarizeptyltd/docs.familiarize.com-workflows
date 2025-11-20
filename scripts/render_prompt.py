#!/usr/bin/env python3
import argparse, json, os, sys, pathlib, re

def render(template: str, ctx: dict) -> str:
    # Replace tokens like {{KEY}} or {{ KEY }} with ctx values; leave unknowns intact
    def sub_key(m):
        key = m.group(1).strip()
        return ctx.get(key, m.group(0))
    out = re.sub(r"\{\{\s*([A-Z0-9_]+)\s*\}\}", sub_key, template)
    # Normalize stray multiple spaces
    out = re.sub(r"[ \t]+", " ", out)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", required=True, help="Path to country-profiles.json (or legacy name)")
    ap.add_argument("--profile-key", required=True, help="Key in JSON, e.g., UAE, SG, UK")
    ap.add_argument("--template", required=True, help="Path to prompt template .md")
    ap.add_argument("--output", required=True, help="Output path for rendered prompt .md (inside docs_repo)")
    args = ap.parse_args()

    profiles_text = pathlib.Path(args.profiles).read_text(encoding="utf-8")
    profiles = json.loads(profiles_text)

    key = args.profile_key
    if key not in profiles:
        # Try case-insensitive match
        alt = {k.lower(): k for k in profiles.keys()}
        if key.lower() in alt:
            key = alt[key.lower()]
        else:
            raise SystemExit(f"Profile '{args.profile_key}' not found. Available: {', '.join(sorted(profiles.keys()))}")

    p = profiles[key]
    regs_csv = ", ".join(p.get("regulators", []))

    folders = p.get("folders", {})
    f_family = folders.get("family_office", f"family-office/{p['country_code']}/")
    f_risk   = folders.get("risk_management", f"risk-management/{p['country_code']}/")
    f_wealth = folders.get("wealth_management", f"wealth-management/{p['country_code']}/")

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
