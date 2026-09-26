from io import BytesIO

import pytest

Image = pytest.importorskip("PIL.Image")

from balance_domain.diascia_tree_figure_recovery import flatten_png_on_white


def test_flatten_png_on_white_preserves_black_labels_on_white_background():
    image = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
    image.putpixel((1, 1), (0, 0, 0, 255))
    buf = BytesIO()
    image.save(buf, format="PNG")

    flattened = Image.open(BytesIO(flatten_png_on_white(buf.getvalue()))).convert("RGB")
    assert flattened.getpixel((0, 0)) == (255, 255, 255)
    assert flattened.getpixel((1, 1)) == (0, 0, 0)
