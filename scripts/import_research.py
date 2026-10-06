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
    for key in ("entries", "rules", "cards", "samples", "profiles", "sources"):
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


def short(value, limit=360):
    return text(value).strip()[:limit]


def voice_and_variants(folder: Path, directory: str):
    """Faqat oldingi tahlilning tuzilgan xulosalari; xom sitata/IDlar emas."""
    voice = {}
    filename = "USLUB_PROFILI_QORALAMA.json" if directory == "xorazm_kocha" else "USLUB_PROFILI.json"
    path = folder / filename
    if path.exists():
        data = json.loads(path.read_text())
        keys = ("default_region_candidate", "default_region_is_editorial_choice",
                "all_xorazm_represented_by_default", "vocabulary_policy", "morphology_policy",
                "regional_separation", "orthography", "sense_selection_required",
                "unsupported_generation_fallback", "address_rotation", "reply_behavior",
                "rare_items_not_forced_every_reply", "default_level", "levels",
                "new_independent_web_source_count", "current_2026_usage_verified",
                "voice_intonation_verified", "new_modern_street_slang_cards",
                "real_chat_dialogue_pairs", "ready_to_claim_modern_xorazm_street_style",
                "toshkent_slang_auto_imported")
        voice = {key: data[key] for key in keys if key in data}
        if directory == "xorazm":
            glossary = json.loads((folder / "LUGAT.json").read_text())
            by_id = {str(row.get("id")): short(row.get("form"), 80)
                     for row in records(glossary)}
            voice["low_risk_forms"] = [by_id[sid] for sid in data.get("initial_low_risk_vocabulary_candidates", [])
                                       if by_id.get(sid)]
    if directory == "toshkent_kocha_v2":
        methods = folder / "YOZISHMA_USULLARI.json"
        if methods.exists():
            voice["interaction_patterns"] = [
                {"title": short(row.get("title"), 80),
                 "analysis": short(row.get("analysis_uz"), 240),
                 "tashkent_exclusive": row.get("tashkent_exclusive", False)}
                for row in records(json.loads(methods.read_text()))]
    variants = []
    path = folder / "HUDUDIY_PROFILLAR.json"
    if path.exists():
        for row in records(json.loads(path.read_text())):
            if not isinstance(row, dict):
                continue
            name = short(first(row, "name", "label", "region"), 100)
            if name:
                variants.append({"name": name,
                    "scope": short(first(row, "scope", "source_region", "region", "area"), 180),
                    "summary": short(first(row, "summary", "traits", "classification", "usable_basis", "notes"), 360),
                    "limit": short(first(row, "limit", "coverage_limit", "unresolved", "notes"), 280),
                    "native_validated": bool(row.get("ready_native_generation_verified", False))})
    return voice, variants


def run(root: Path, output: Path):
    cards, inputs, profiles, skipped_examples = [], [], [], []
    specs = [(name, label, "regional") for name, label in REGIONS.items()]
    specs += [("toshkent_kocha_v2", "Toshkent ko‘cha", "street"), ("xorazm_kocha", "Xorazm ko‘cha · sinov", "street_trial")]
    for directory, label, register in specs:
        folder = root / directory
        dialect = "toshkent_kocha" if directory == "toshkent_kocha_v2" else directory
        region = dialect.split("_kocha")[0]
        voice, variants = voice_and_variants(folder, directory)
        profiles.append({"id": dialect, "label": label, "region": region, "register": register,
                         "trial": register == "street_trial",
                         "scope_note": "Viloyat ichida variantlar mavjud; karta hududi va konteksti ustuvor.",
                         "voice": voice, "regional_variants": variants})
        for extra in ("USLUB_PROFILI.json", "USLUB_PROFILI_QORALAMA.json",
                      "HUDUDIY_PROFILLAR.json", "YOZISHMA_USULLARI.json"):
            path = folder / extra
            if path.exists():
                inputs.append({"research": directory, "file": extra,
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        manifest = folder / "MANBALAR.json"
        if not manifest.exists():
            manifest = folder / "MANBALAR_HOLATI.json"
        source_map = {}
        if manifest.exists():
            for source in sources_in(json.loads(manifest.read_text())):
                source_map[str(first(source, "id", "source_id"))] = source
        filenames = ["LUGAT.json", "GRAMMATIKA.json", "FONETIKA.json", "NUTQ_NAMUNALARI.json"]
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
                if filename == "FONETIKA.json":
                    form = short(first(row, "display_approximation", "form_source", "input_as_source", "literary_form", "label", "title"), 240)
                    meaning = short(first(row, "meaning_or_analysis_uz", "claim_uz", "process", "display_note", "analysis_uz", "notes"), 360)
                elif filename == "NUTQ_NAMUNALARI.json":
                    form = short(first(row, "display", "text_source", "readable_surface", "source_text_extracted", "original_extracted", "label", "target"), 240)
                    meaning = short(first(row, "standard_meaning", "meaning_uz", "meaning_standard_uz", "meaning_or_analysis_uz"), 360)
                    if not meaning:
                        skipped_examples.append({"research": directory, "row": index,
                                                 "reason": "Tasdiqlangan standart ma’no yo‘q"})
                        continue
                else:
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
                kind = {"GRAMMATIKA.json": "grammar", "FONETIKA.json": "phonetics",
                        "NUTQ_NAMUNALARI.json": "example"}.get(filename, "lexicon")
                note = text(first(row, "usage_note", "note", "notes", "application", "bot_application"))
                scope = text(first(row, "regions_as_source_claim", "regions", "region", "area", "scope", "corpus_scope"))
                if kind == "phonetics":
                    note += " Fonetik manba qaydi; yozuv/audio tasdig‘isiz umumiy talaffuz qoidasi emas."
                elif kind == "example":
                    note += " Manbadagi nutq namunasi; bugungi umumiy nutq sifatida avtomatik ko‘chirilmaydi."
                meta = {"research_status": short(row.get("evidence_status"), 120),
                        "writing_status": short(row.get("writing_status") or row.get("display_note"), 180),
                        "register": short(row.get("register") or row.get("role"), 120),
                        "genre": short(row.get("genre"), 100),
                        "application": short(row.get("bot_application"), 180),
                        "exclusive_to_region": row.get("exclusive_to_region") is True,
                        "audio_verified": row.get("audio_verified") is True,
                        "modern_usage_verified": (row.get("independent_modern_usage_verified") is True
                                                  or row.get("current_usage_verified") is True),
                        "native_validated": row.get("native_speaker_validated") is True,
                        "chat_observed": row.get("observed_in_uploaded_export") is True}
                card = {"id": f"{dialect}:{kind}:{index:04}", "dialect": dialect, "kind": kind,
                    "form": form, "meaning": meaning, "scope": scope, "note": note,
                    "evidence": evidence, "meta": meta}
                if register == "street_trial":
                    card["note"] += " Zamonaviy ko‘cha chatida tasdiqlanmagan tayanch."
                cards.append(card)
    profiles.insert(0, {"id": "adabiy", "label": "Adabiy o‘zbekcha", "region": "umumiy", "register": "standard", "trial": False,
                        "scope_note": "O‘qilishi qulay adabiy o‘zbekcha.", "voice": {}, "regional_variants": []})
    bundle = {"schema_version": 1, "profiles": profiles, "cards": cards,
              "provenance": {"inputs": inputs, "skipped_untranslated_examples": skipped_examples,
                             "raw_chat_exports_included": False,
                             "personal_chat_metadata_included": False, "training_weights_changed": False}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n")
    summary = {"profiles": len(profiles), "cards": len(cards), "by_dialect": dict(Counter(c['dialect'] for c in cards)),
               "by_kind": dict(Counter(c['kind'] for c in cards)),
               "skipped_untranslated_examples": len(skipped_examples),
               "bundle_sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    output.with_name("import-report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-root", default="/workspace/research")
    parser.add_argument("--output", default="data/knowledge.json")
    args = parser.parse_args()
    run(Path(args.research_root), Path(args.output))
