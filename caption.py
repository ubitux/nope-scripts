from dataclasses import dataclass
from pathlib import Path

import pynopegl as ngl
from pynopegl_utils.misc import SceneCfg, scene


@dataclass
class _Theme:
    bg_color: tuple[float, float, float]
    bg_opacity: float
    fg_color: tuple[float, float, float]


_THEMES = dict(
    dark=_Theme(bg_color=(0, 0, 0), bg_opacity=0.7, fg_color=(1, 1, 1)),
    light=_Theme(bg_color=(1, 1, 1), bg_opacity=0.9, fg_color=(0.15, 0.15, 0.15)),
    pimp=_Theme(bg_color=(0, 0.5, 1), bg_opacity=0.7, fg_color=(1, 0.5, 0)),
    paris1=_Theme(bg_color=(1, 1, 1), bg_opacity=0.9, fg_color=(0, 0.196, 0.431)),
)

_ASSETS_DIR = Path(__file__).parent / "assets"
_EASING = "cubic_out"
_FONT = (_ASSETS_DIR / "fonts" / "InclusiveSans-Regular.ttf").as_posix()


@scene(
    compat_specs="~=0.9",  # FIXME actually a dev version at the moment
    controls=dict(
        font=scene.Text(),
        side=scene.List(choices=["left", "right"]),
        theme=scene.List(choices=["dark", "light", "pimp", "paris1"]),
    ),
)
def caption(cfg: SceneCfg, font=_FONT, side="left", theme="light"):
    cfg.clear_color = (0, 0, 0, 0)  # transparent background so it can be overlayed

    start = 0
    end = 10
    effect_duration = 1
    name_scale = 0.8
    desc_scale = 0.6

    cfg.duration = end - start
    assert cfg.duration >= effect_duration * 2

    w_ratio = 1 / 3
    w_ratio *= 2
    h = 1 / 4

    if side == "right":
        caption_corner = (1 - w_ratio, -1 + 0.1, 0)
        outside_pos = (w_ratio, 0, 0)
    elif side == "left":
        caption_corner = (-1, -1 + 0.1, 0)
        outside_pos = (-w_ratio, 0, 0)
    else:
        assert False

    theme_settings = _THEMES[theme]

    text = ngl.Group(
        children=(
            ngl.Text(
                text="John Doe",
                live_id="name",
                box_corner=(
                    caption_corner[0],
                    caption_corner[1] + h * 1 / 3,
                    caption_corner[2],
                ),
                box_width=(w_ratio, 0, 0),
                box_height=(0, h * 2 / 3, 0),
                fg_color=theme_settings.fg_color,
                bg_color=(0, 0, 0),
                bg_opacity=0,
                font_files=font,
                font_scale=name_scale,
                aspect_ratio=cfg.aspect_ratio,
            ),
            ngl.Text(
                text="Historico-mathématicien",
                live_id="desc",
                box_corner=caption_corner,
                box_width=(w_ratio, 0, 0),
                box_height=(0, h * 1 / 3, 0),
                fg_color=theme_settings.fg_color,
                bg_color=(0, 0.5, 0),
                bg_opacity=0,
                font_files=font,
                font_scale=desc_scale,
                aspect_ratio=cfg.aspect_ratio,
            ),
        )
    )

    caption_bg = ngl.RenderColor(
        geometry=ngl.Quad(
            corner=caption_corner,
            width=(w_ratio, 0, 0),
            height=(0, h, 0),
        ),
        color=theme_settings.bg_color,
        opacity=theme_settings.bg_opacity,
        blending="src_over",
    )

    animkf = [
        ngl.AnimKeyFrameVec3(start, outside_pos),
        ngl.AnimKeyFrameVec3(start + effect_duration, (0, 0, 0), _EASING),
        ngl.AnimKeyFrameVec3(end - effect_duration, (0, 0, 0)),
        ngl.AnimKeyFrameVec3(end, outside_pos, _EASING),
    ]

    caption = ngl.Group(children=[caption_bg, text])
    caption = ngl.Translate(caption, vector=ngl.AnimatedVec3(animkf))

    bg = ngl.UserSwitch(ngl.RenderGradient4(), live_id="background")
    return ngl.Group(children=[bg, caption])
