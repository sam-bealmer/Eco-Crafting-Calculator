#!/usr/bin/env python3
"""
Eco Game Data Parser
Parses C# source files from Eco's AutoGen directory and generates
recipes.json, skills.json, tables.json, and item-tags.json.

Usage: python parse_eco_data.py
"""

import os
import re
import json

# ── Configuration ─────────────────────────────────────────────────────────────

ECO_AUTOGEN_DIR = r"C:\Program Files (x86)\Steam\steamapps\common\Eco\Eco_Data\Server\Mods\__core__\AutoGen"
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

# ── Helpers ───────────────────────────────────────────────────────────────────

def camel_to_words(name: str, strip_suffix: str = "") -> str:
    """Convert CamelCase to 'Title Words', optionally stripping a suffix first."""
    if strip_suffix and name.endswith(strip_suffix):
        name = name[: -len(strip_suffix)]
    return re.sub(r"(?<=[a-z])([A-Z])|(?<=[A-Z])([A-Z][a-z])", r" \1\2", name).strip()


def find_block_end(text: str, open_brace_pos: int) -> int:
    """Given the position of an opening '{', return the index just after the matching '}'."""
    depth = 1
    pos = open_brace_pos + 1
    while pos < len(text) and depth > 0:
        ch = text[pos]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        pos += 1
    return pos


def get_all_cs_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(".cs"):
                yield os.path.join(dirpath, fname)


def read_file(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


# ── Pass 1: WorldObject display names (XxxObject → "Display Name") ────────────

def build_object_display_map(cs_files: list) -> dict:
    """
    Returns { "BlastFurnaceObject": "Blast Furnace", ... }

    WorldObject classes expose their name via two patterns:
      1. override property: public override LocString DisplayName => Localizer.DoStr("...");
      2. WorldObjectItem<XxxObject> with [LocDisplayName("...")] on the item class
    """
    display_map = {}

    # Pattern 1: DisplayName override property inside an XxxObject class
    # Find class XxxObject, then look for the DoStr inside its body
    class_pat = re.compile(r'public\s+partial\s+class\s+(\w+Object)\b')
    dostr_pat  = re.compile(r'DisplayName\s*=>\s*Localizer\.DoStr\("([^"]+)"\)')

    # Pattern 2: WorldObjectItem<XxxObject> with [LocDisplayName] on same item class
    woi_pat = re.compile(
        r'\[LocDisplayName\("([^"]+)"\)\][^{;]*?'
        r'public\s+partial\s+class\s+\w+Item\s*:\s*WorldObjectItem\s*<\s*(\w+Object)\s*>',
        re.DOTALL,
    )

    for path in cs_files:
        content = read_file(path)

        # Pattern 1 — scan each Object class body for the DisplayName override
        for cls_m in class_pat.finditer(content):
            obj_class = cls_m.group(1)
            # Find the opening brace of the class
            brace_pos = content.find("{", cls_m.end())
            if brace_pos == -1:
                continue
            body_end = find_block_end(content, brace_pos)
            body     = content[brace_pos:body_end]
            dn_m = dostr_pat.search(body)
            if dn_m:
                display_map[obj_class] = dn_m.group(1)

        # Pattern 2 — WorldObjectItem<XxxObject> [LocDisplayName]
        for m in woi_pat.finditer(content):
            display_map[m.group(2)] = m.group(1)

    return display_map


# ── Pass 2: Item display names (XxxItem → "Display Name") ────────────────────

def build_item_display_map(cs_files: list) -> dict:
    """
    Returns { "SteelBarItem": "Steel Bar", ... }
    """
    display_map = {}
    pattern = re.compile(
        r'\[LocDisplayName\("([^"]+)"\)\][^{;]*?'
        r'public\s+partial\s+class\s+(\w+Item)\b',
        re.DOTALL,
    )
    for path in cs_files:
        content = read_file(path)
        for m in pattern.finditer(content):
            display_map[m.group(2)] = m.group(1)
    return display_map


def resolve_item_name(type_name: str, item_display_map: dict) -> str:
    """Map 'SteelBarItem' → 'Steel Bar', falling back to camelCase splitting."""
    if type_name in item_display_map:
        return item_display_map[type_name]
    return camel_to_words(type_name, "Item")


# ── Pass 3: Item tags (XxxItem → ["Tag1", "Tag2", ...]) ──────────────────────

# Tags we want to skip — not useful as ingredient-category tags
_SKIP_TAGS = {
    "Currency", "Usable", "Upgrade", "ModernUpgrade", "MechanicsUpgrade",
    "BasicUpgrade", "IndustrialUpgrade", "AdvancedUpgrade", "ElectronicsUpgrade",
    "Armor",
}

def build_item_tags_map(cs_files: list) -> dict:
    """
    Returns { "SteelBarItem": ["Metal", ...], ... }
    Only includes tags that are plausible ingredient-group tags.
    """
    tags_map: dict[str, set] = {}
    for path in cs_files:
        content = read_file(path)
        # Find each XxxItem class
        for cls_match in re.finditer(r"public\s+partial\s+class\s+(\w+Item)\b", content):
            class_name = cls_match.group(1)
            # Scan the 600 chars before the class keyword for [Tag("...")] attributes
            start = max(0, cls_match.start() - 600)
            preceding = content[start : cls_match.start()]
            tags = re.findall(r'\[Tag\("([^"]+)"\)\]', preceding)
            useful = [t for t in tags if t not in _SKIP_TAGS and not t.startswith("Partial")]
            if useful:
                tags_map.setdefault(class_name, set()).update(useful)
    return {k: sorted(v) for k, v in tags_map.items()}


# ── Pass 4: Recipe families ───────────────────────────────────────────────────

def parse_ingredient_element(text: str, item_display_map: dict) -> dict | None:
    """
    Parse a single IngredientElement line and return {"name": ..., "qty": ...}.
    Handles both typeof(XxxItem) and "TagName" forms.
    """
    # typeof(XxxItem) form
    m = re.match(
        r'\s*new\s+IngredientElement\s*\(\s*typeof\s*\(\s*(\w+Item)\s*\)\s*,\s*([\d.]+)',
        text,
    )
    if m:
        name = resolve_item_name(m.group(1), item_display_map)
        qty = float(m.group(2))
        return {"name": name, "qty": int(qty) if qty == int(qty) else qty}

    # "TagName" string form
    m = re.match(
        r'\s*new\s+IngredientElement\s*\(\s*"([^"]+)"\s*,\s*([\d.]+)',
        text,
    )
    if m:
        qty = float(m.group(2))
        return {"name": m.group(1), "qty": int(qty) if qty == int(qty) else qty}

    return None


def parse_crafting_element(text: str, item_display_map: dict):
    """
    Parse a single CraftingElement line.
    Returns (name, qty, is_byproduct).
    """
    # CraftingElement<XxxItem>(typeof(Skill), qty) — byproduct
    m = re.match(
        r'\s*new\s+CraftingElement\s*<\s*(\w+Item)\s*>\s*\(\s*typeof\s*\(',
        text,
    )
    if m:
        item_name = resolve_item_name(m.group(1), item_display_map)
        qty_m = re.search(r'\),\s*([\d.]+)', text)
        qty = float(qty_m.group(1)) if qty_m else 1.0
        return item_name, int(qty) if qty == int(qty) else qty, True

    # CraftingElement<XxxItem>(qty) or CraftingElement<XxxItem>() — primary output
    m = re.match(
        r'\s*new\s+CraftingElement\s*<\s*(\w+Item)\s*>\s*\(\s*([\d.]*)\s*\)',
        text,
    )
    if m:
        item_name = resolve_item_name(m.group(1), item_display_map)
        qty_str = m.group(2).strip()
        qty = float(qty_str) if qty_str else 1.0
        return item_name, int(qty) if qty == int(qty) else qty, False

    return None, None, False


def parse_all_recipes(cs_files: list, object_display_map: dict, item_display_map: dict) -> dict:
    """
    Returns { "item_display_name": [ recipe_dict, ... ], ... }
    where each recipe_dict matches the recipes.json schema.
    """
    recipes_by_item: dict[str, list] = {}

    # Find ALL RecipeFamily subclasses (with or without [RequiresSkill])
    recipe_class_pat = re.compile(
        r'public\s+partial\s+class\s+(\w+Recipe)\s*:\s*RecipeFamily',
    )
    # Pattern to extract [RequiresSkill] from the 800 chars before a class definition
    skill_attr_pat = re.compile(
        r'\[RequiresSkill\s*\(\s*typeof\s*\(\s*(\w+Skill)\s*\)\s*,\s*(\d+)\s*\)\]',
    )

    for path in cs_files:
        content = read_file(path)

        if "RecipeFamily" not in content:
            continue

        for cls_match in recipe_class_pat.finditer(content):
            recipe_class_name = cls_match.group(1)  # e.g. "SteelBarRecipe"

            # Look back up to 800 chars for [RequiresSkill]
            look_back_start = max(0, cls_match.start() - 800)
            preceding = content[look_back_start : cls_match.start()]
            skill_m = skill_attr_pat.search(preceding)
            if skill_m:
                skill_display = camel_to_words(skill_m.group(1), "Skill")
                skill_level   = int(skill_m.group(2))
            else:
                skill_display = ""
                skill_level   = 0

            # ── Find constructor body ──────────────────────────────────────────
            # The constructor signature is: public XRecipe() { ... }
            search_start = cls_match.end()
            ctor_pat = re.compile(
                r'public\s+' + re.escape(recipe_class_name) + r'\s*\(\s*\)\s*\{',
                re.DOTALL,
            )
            ctor_match = ctor_pat.search(content, search_start)
            if not ctor_match:
                continue

            ctor_open = ctor_match.end() - 1  # position of '{'
            ctor_end  = find_block_end(content, ctor_open)
            ctor_body = content[ctor_open : ctor_end]

            # ── displayName ───────────────────────────────────────────────────
            disp_m = re.search(r'displayName:\s*Localizer\.DoStr\("([^"]+)"\)', ctor_body)
            if not disp_m:
                continue
            recipe_display_name = disp_m.group(1)

            # ── laborCalories ─────────────────────────────────────────────────
            labor_m = re.search(r'CreateLaborInCaloriesValue\s*\(\s*([\d.]+)', ctor_body)
            labor_calories = int(float(labor_m.group(1))) if labor_m else 0

            # ── crafting table ────────────────────────────────────────────────
            table_m = re.search(
                r'CraftingComponent\.AddRecipe\s*\(\s*tableType:\s*typeof\s*\(\s*(\w+Object)\s*\)',
                ctor_body,
            )
            if table_m:
                obj_type   = table_m.group(1)
                table_name = object_display_map.get(obj_type, camel_to_words(obj_type, "Object"))
            else:
                table_name = ""

            # ── ingredients ──────────────────────────────────────────────────
            ingredients = []
            ingr_block_m = re.search(
                r'ingredients:\s*new\s+List\s*<\s*IngredientElement\s*>\s*\{([^}]*)\}',
                ctor_body,
                re.DOTALL,
            )
            if ingr_block_m:
                ingr_block = ingr_block_m.group(1)
                # Split on lines; each non-empty line starting with "new" is an ingredient
                for line in ingr_block.splitlines():
                    if "new IngredientElement" in line:
                        entry = parse_ingredient_element(line, item_display_map)
                        if entry:
                            ingredients.append(entry)

            # ── outputs & byproducts ──────────────────────────────────────────
            output_qty  = 1
            byproducts  = []
            output_item_name = recipe_display_name  # fallback

            items_block_m = re.search(
                r'items:\s*new\s+List\s*<\s*CraftingElement\s*>\s*\{([^}]*)\}',
                ctor_body,
                re.DOTALL,
            )
            if items_block_m:
                items_block = items_block_m.group(1)
                primary_found = False
                for line in items_block.splitlines():
                    if "new CraftingElement" not in line:
                        continue
                    name, qty, is_bp = parse_crafting_element(line, item_display_map)
                    if name is None:
                        continue
                    if is_bp:
                        byproducts.append({"name": name, "qty": qty})
                    elif not primary_found:
                        output_item_name = name
                        output_qty       = qty
                        primary_found    = True

            recipe_dict = {
                "label":        table_name or "Default",
                "skill":        skill_display,
                "craftingTable": table_name,
                "laborCalories": labor_calories,
                "outputQty":    output_qty,
                "ingredients":  ingredients,
                "byproducts":   byproducts,
                "profitOverride": -1,
                "minLevel":     skill_level,
            }

            recipes_by_item.setdefault(output_item_name, []).append(recipe_dict)

    return recipes_by_item


# ── Main ──────────────────────────────────────────────────────────────────────

def load_json(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {path}  ({len(data)} entries)")


def main():
    print("Scanning Eco AutoGen C# files …")
    cs_files = list(get_all_cs_files(ECO_AUTOGEN_DIR))
    print(f"  Found {len(cs_files)} .cs files")

    print("Building display-name maps …")
    object_display_map = build_object_display_map(cs_files)
    item_display_map   = build_item_display_map(cs_files)
    item_tags_map      = build_item_tags_map(cs_files)
    print(f"  {len(object_display_map)} world-object names, "
          f"{len(item_display_map)} item names, "
          f"{len(item_tags_map)} items with tags")

    print("Parsing recipe families …")
    recipes_by_item = parse_all_recipes(cs_files, object_display_map, item_display_map)
    print(f"  Found {sum(len(v) for v in recipes_by_item.values())} recipes "
          f"for {len(recipes_by_item)} items")

    # ── recipes.json ──────────────────────────────────────────────────────────
    existing_recipes = load_json(os.path.join(PUBLIC_DIR, "recipes.json"))
    # Build a lookup of existing items for price preservation
    existing_by_name = {item["name"]: item for item in existing_recipes}

    new_recipes_list = []
    # Items found in game files
    for item_name in sorted(recipes_by_item):
        item_recipes = recipes_by_item[item_name]
        existing     = existing_by_name.get(item_name, {})
        new_recipes_list.append({
            "name":           item_name,
            "marketPrice":    existing.get("marketPrice", None),
            "defaultRecipeIdx": 0,
            "recipes":        item_recipes,
        })
    # Keep existing items that have no game-file recipe (raw materials, etc.)
    game_item_names = set(recipes_by_item.keys())
    for item in existing_recipes:
        if item["name"] not in game_item_names:
            new_recipes_list.append(item)
    new_recipes_list.sort(key=lambda x: x["name"])

    # ── skills.json ───────────────────────────────────────────────────────────
    existing_skills    = load_json(os.path.join(PUBLIC_DIR, "skills.json"))
    existing_skill_set = {s["name"] for s in existing_skills}

    found_skills: set[str] = set()
    for item_recipes in recipes_by_item.values():
        for r in item_recipes:
            if r["skill"]:
                found_skills.add(r["skill"])

    new_skills = list(existing_skills)
    for skill in sorted(found_skills - existing_skill_set):
        new_skills.append({"name": skill, "level": 1, "lavish": False})
    new_skills.sort(key=lambda x: x["name"])

    # ── tables.json ───────────────────────────────────────────────────────────
    # Only include tables actually referenced by at least one recipe.
    # Preserve upgrade settings from existing entries; default to "none" for new ones.
    existing_tables     = load_json(os.path.join(PUBLIC_DIR, "tables.json"))
    existing_table_map  = {t["name"]: t for t in existing_tables}

    found_tables: set[str] = set()
    for item_recipes in recipes_by_item.values():
        for r in item_recipes:
            if r["craftingTable"]:
                found_tables.add(r["craftingTable"])

    new_tables = []
    for table_name in sorted(found_tables):
        existing = existing_table_map.get(table_name, {})
        new_tables.append({"name": table_name, "upgrade": existing.get("upgrade", "none")})

    # ── item-tags.json ────────────────────────────────────────────────────────
    existing_tags    = load_json(os.path.join(PUBLIC_DIR, "item-tags.json"))
    existing_tag_set = {t["name"] for t in existing_tags}

    # Build tag → member display names
    tags_to_members: dict[str, set] = {}
    for item_type, tags in item_tags_map.items():
        display_name = resolve_item_name(item_type, item_display_map)
        for tag in tags:
            tags_to_members.setdefault(tag, set()).add(display_name)

    new_tags = list(existing_tags)
    for tag_name in sorted(tags_to_members):
        if tag_name in existing_tag_set:
            continue
        members = sorted(tags_to_members[tag_name])
        new_tags.append({"name": tag_name, "marketPrice": None, "memberNames": members})
    # Also update existing tags with new members from game files
    for tag_entry in new_tags:
        tag_name = tag_entry["name"]
        if tag_name in tags_to_members:
            existing_members = set(tag_entry.get("memberNames", []))
            new_members = tags_to_members[tag_name]
            merged = sorted(existing_members | new_members)
            tag_entry["memberNames"] = merged

    # ── Write outputs ─────────────────────────────────────────────────────────
    print("\nWriting JSON files …")
    save_json(os.path.join(PUBLIC_DIR, "recipes.json"),   new_recipes_list)
    save_json(os.path.join(PUBLIC_DIR, "skills.json"),    new_skills)
    save_json(os.path.join(PUBLIC_DIR, "tables.json"),    new_tables)
    save_json(os.path.join(PUBLIC_DIR, "item-tags.json"), new_tags)
    print("\nDone!")


if __name__ == "__main__":
    main()
