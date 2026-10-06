"""Oldingi tadqiqotlarni yo‘l/Telegram shaxsiy ma’lumotsiz bilim bazasiga yig‘adi."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

REGIONS = {
    "surxondaryo": "Surxondaryo", "qashqadaryo": "Qashqadaryo", "samarqand": "Samarqand",
    "buxoro": "Buxoro", "jizzax": "Jizzax", "andijon": "Andijon", "fargona": "Farg‘ona",
    "namangan": "Namangan", "toshkent": "Toshkent", "xorazm": "Xorazm",
}


def text(value):
    if isinstance(value, list):
        return "; ".join(text(x) for x in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value) if value is not None else ""


def first(row, *keys):
    return next((row[k] for k in keys if row.get(k)), "")


def records(value):
    if isinstance(value, list):
        return value
    for key in ("entries", "rules", "cards", "sources"):
        if isinstance(value.get(key), list):
            return value[key]
    return []


def sources_in(value):
    if isinstance(value, list):
        return value
    output = []
    for key, item in value.items():
        if key in {"sources", "uploaded_sources", "supplementary_sources", "academic_sources_used", "additional_sources"} and isinstance(item, list):
            output.extend(x for x in item if isinstance(x, dict))
    return output


def run(root: Path, output: Path):
    cards, inputs, profiles = [], [], []
    specs = [(name, label, "regional") for name, label in REGIONS.items()]
    specs += [("toshkent_kocha_v2", "Toshkent ko‘cha", "street"), ("xorazm_kocha", "Xorazm ko‘cha · sinov", "street_trial")]
    for directory, label, register in specs:
        folder = root / directory
        dialect = "toshkent_kocha" if directory == "toshkent_kocha_v2" else directory
        region = dialect.split("_kocha")[0]
        profiles.append({"id": dialect, "label": label, "region": region, "register": register,
                         "trial": register == "street_trial",
                         "scope_note": "Viloyat ichida variantlar mavjud; karta hududi va konteksti ustuvor."})
        manifest = folder / "MANBALAR.json"
        if not manifest.exists():
            manifest = folder / "MANBALAR_HOLATI.json"
        source_map = {}
        if manifest.exists():
            for source in sources_in(json.loads(manifest.read_text())):
                source_map[str(first(source, "id", "source_id"))] = source
        filenames = ["LUGAT.json", "GRAMMATIKA.json"]
        if directory == "toshkent_kocha_v2":
            filenames = ["SLANG_VA_YOZUV_KARTALARI.json"]
        elif directory == "xorazm_kocha":
            filenames = ["NORASMIY_MUOMALA_TAYANCHLARI.json"]
        for filename in filenames:
            path = folder / filename
            if not path.exists():
                continue
            content = path.read_bytes()
            inputs.append({"research": directory, "file": filename, "sha256": hashlib.sha256(content).hexdigest()})
            for index, row in enumerate(records(json.loads(content)), 1):
                if not isinstance(row, dict):
                    raise ValueError(f"Noto‘g‘ri karta: {directory}/{filename}/{index}")
                form = text(first(row, "form", "lemma", "form_latin", "dialect_form_display", "display_form", "form_source", "label", "attested_form_display", "dialect_reading", "observation", "title", "kind"))
                meaning = text(first(row, "meaning_uz", "meanings", "meaning_or_analysis_uz", "claim_uz", "analysis_uz", "standard_context_form", "standard", "explanation"))
                if not form or not meaning:
                    raise ValueError(f"Ma’nosiz/shaklsiz karta: {directory}/{filename}/{index}: {list(row)}")
                refs = first(row, "source_refs", "refs", "evidence")
                refs = refs if isinstance(refs, list) else [row] if row.get("source_id") else []
                evidence = []
                for item in refs:
                    sid = str(first(item, "source_id", "source"))
                    meta = source_map.get(sid, {})
                    is_chat = "message_id" in item or sid.startswith("TG")
                    evidence.append({"source_id": sid,
                        "title": text(first(meta, "title")) or ("Foydalanuvchi bergan chat eksportidagi leksik kuzatuv" if is_chat else sid),
                        "author": text(first(meta, "author", "authors", "editor")), "year": meta.get("year"),
                        "pdf_page": item.get("pdf_page"),
                        "printed_page": first(item, "printed_page", "printed_pages"),
                        "source_sha256": first(item, "source_sha256") or meta.get("sha256", ""),
                        "kind": "chat_lexical_observation" if is_chat else "written_source"})
                kind = "grammar" if filename == "GRAMMATIKA.json" else "lexicon"
                note = text(first(row, "usage_note", "note", "notes", "application", "bot_application"))
                scope = text(first(row, "regions_as_source_claim", "regions", "region", "area", "scope", "corpus_scope"))
                card = {"id": f"{dialect}:{kind}:{index:04}", "dialect": dialect, "kind": kind,
                    "form": form, "meaning": meaning, "scope": scope, "note": note,
                    "evidence": evidence, "modern_usage_verified": False,
                    "chat_observed": bool(row.get("observed_in_uploaded_export")), "native_validated": False}
                if register == "street_trial":
                    card["note"] += " Zamonaviy ko‘cha chatida tasdiqlanmagan tayanch."
                cards.append(card)
    profiles.insert(0, {"id": "adabiy", "label": "Adabiy o‘zbekcha", "region": "umumiy", "register": "standard", "trial": False,
                        "scope_note": "O‘qilishi qulay adabiy o‘zbekcha."})
    bundle = {"schema_version": 1, "profiles": profiles, "cards": cards,
              "provenance": {"inputs": inputs, "raw_chat_exports_included": False,
                             "personal_chat_metadata_included": False, "training_weights_changed": False}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n")
    summary = {"profiles": len(profiles), "cards": len(cards), "by_dialect": dict(Counter(c['dialect'] for c in cards)),
               "by_kind": dict(Counter(c['kind'] for c in cards)), "bundle_sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    output.with_name("import-report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-root", default="/workspace/research")
    parser.add_argument("--output", default="data/knowledge.json")
    args = parser.parse_args()
    run(Path(args.research_root), Path(args.output))
