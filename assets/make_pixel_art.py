"""Generates assets/turtleneck.svg from the character grid below. Run: python3 assets/make_pixel_art.py"""
import os

ROWS = """
.........www.........
........w...w........
............w........
..........ww.........
..........w..........
......KkKkKkKkK......
......kKkKkKkKk......
......KkKkKkKkK......
.....kKkKkKkKkKk.....
...kkkkkkkkkkkkkkk...
.kkkkkkkkkkkkkkkkkkk.
kkkkkkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkkkkkk
kkk.kkkkkkkkkkkkk.kkk
kkk.kkkkkkkkkkkkk.kkk
kkk.kkkkkkkkkkkkk.kkk
kkk.kkkkkkkkkkkkk.kkk
kkk.kkkkkkkkkkkkk.kkk
kkk.kkkkkkkkkkkkk.kkk
KkK.kkkkkkkkkkkkk.KkK
kKk.kkkkkkkkkkkkk.kKk
....kkkkkkkkkkkkk....
....kkkkkkkkkkkkk....
....KkKkKkKkKkKkK....
....kKkKkKkKkKkKk....
""".strip("\n").split("\n")

PALETTE = {
    "w": "#8b6b4a",  # hanger
    "K": "#3a3a3a",  # ribbing
    "k": "#161616",  # sweater
    ".": None,
}
BG, PAD, CELL = "#e9dcc9", 2, 12


def main() -> None:
    w, h = len(ROWS[0]), len(ROWS)
    bad = [i for i, r in enumerate(ROWS) if len(r) != w]
    assert not bad, f"rows with wrong length: {bad}"
    size = ((w + 2 * PAD) * CELL, (h + 2 * PAD) * CELL)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size[0]} {size[1]}" '
        f'width="{size[0]}" height="{size[1]}" shape-rendering="crispEdges">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
    ]
    for y, row in enumerate(ROWS):
        for x, ch in enumerate(row):
            if PALETTE[ch]:
                out.append(
                    f'<rect x="{(x + PAD) * CELL}" y="{(y + PAD) * CELL}" '
                    f'width="{CELL}" height="{CELL}" fill="{PALETTE[ch]}"/>'
                )
    out.append("</svg>")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "turtleneck.svg")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print(f"wrote {path}: {w}x{h} grid, {len(out) - 3} pixels")
    shade = str.maketrans({".": " ", "k": "█", "K": "▓", "w": "▒"})
    print("\n".join(r.translate(shade) for r in ROWS))


if __name__ == "__main__":
    main()
