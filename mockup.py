"""Anteprima: badge sul retro (grande) e sul petto (piccolo) di una maglia nera."""
import cairosvg
from badge import badge, path_d

ring, ball = badge()
TEE = ("M 150,40 L 250,10 Q 300,60 350,10 L 450,40 L 540,170 L 450,215 L 430,180 "
       "L 430,560 Q 300,580 170,560 L 170,180 L 150,215 L 60,170 Z")

def tee(x, front, scale, cx, cy, label):
    d = path_d(ring, scale, cx - 500 * scale, cy - 500 * scale) + " " + path_d(ball, scale, cx - 500 * scale, cy - 500 * scale)
    collar = ('<path d="M 250,10 Q 300,60 350,10" fill="none" stroke="#2a2a2a" stroke-width="10"/>' if not front else
              '<path d="M 250,10 Q 300,90 350,10" fill="#0c0c0c" stroke="#2a2a2a" stroke-width="10"/>')
    return (f'<g transform="translate({x},40)"><path d="{TEE}" fill="#151515" stroke="#2a2a2a" stroke-width="4"/>'
            f'{collar}<path fill="#f2f2f2" fill-rule="evenodd" d="{d}"/>'
            f'<text x="300" y="620" text-anchor="middle" font-family="Inter" font-size="22" fill="#555">{label}</text></g>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 700" width="1240" height="700">'
       f'<rect width="1240" height="700" fill="#e9e7e3"/>'
       f'{tee(20, False, 0.27, 300, 220, "RETRO")}{tee(620, True, 0.085, 375, 150, "FRONTE")}</svg>')
cairosvg.svg2png(bytestring=svg.encode(), write_to="mockup.png", output_width=2480, output_height=1400)
print("ok")
