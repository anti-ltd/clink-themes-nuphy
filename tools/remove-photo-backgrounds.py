#!/usr/bin/env python3
"""Remove border-connected studio backgrounds locally, without regenerating objects.

Requires Python 3, Pillow, NumPy and SciPy. Writes review files only; never changes Images
or the release manifest. Intended for these uniform-background product photographs,
not arbitrary photos. Review pale edges, transparent cases and shadows before use.

Install: python3 -m pip install -r tools/requirements-background-removal.txt
Run: python3 tools/remove-photo-backgrounds.py --source-dir /path/to/originals --output /path/to/review
Originals are named THEME-ID.png (Pillow detects their actual file format).
"""
import argparse
import html
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageDraw


def remove_background(image, tolerance, closing_radius=2, background_seeds=()):
    rgba = image.convert('RGBA')
    pixels = np.array(rgba)
    if pixels[:, :, 3].min() < 255:
        return rgba, {'method': 'existing alpha preserved'}
    rgb = pixels[:, :, :3].astype(np.float32)
    corners = np.concatenate([rgb[:8, :8].reshape(-1, 3), rgb[:8, -8:].reshape(-1, 3),
                              rgb[-8:, :8].reshape(-1, 3), rgb[-8:, -8:].reshape(-1, 3)])
    background = np.median(corners, axis=0)
    if np.max(np.abs(corners - background)) > tolerance:
        raise ValueError('Corners are not a uniform background; manual review required')
    from scipy import ndimage as ndi
    distance = np.max(np.abs(rgb - background), axis=2)
    # Only flood background connected to the canvas border. Then close tiny
    # JPEG gaps before reconstructing edge coverage from the original pixels.
    eligible = distance <= tolerance
    seeds = np.zeros(eligible.shape, dtype=bool)
    seeds[0, :] = eligible[0, :]; seeds[-1, :] = eligible[-1, :]
    seeds[:, 0] = eligible[:, 0]; seeds[:, -1] = eligible[:, -1]
    removed = ndi.binary_propagation(seeds, mask=eligible)
    mask = ~removed
    labels, count = ndi.label(mask)
    sizes = np.bincount(labels.ravel()); sizes[0] = 0
    mask = sizes[labels] >= max(16, mask.size * 0.0001)
    mask = ndi.binary_closing(mask, iterations=closing_radius)
    mask = ndi.binary_fill_holes(mask)
    mask = ndi.binary_opening(mask, iterations=1)
    # Explicit, source-verified seeds recover enclosed openings such as handles.
    # They are applied after hole filling so enclosed white keys stay protected.
    if background_seeds:
        hole_seeds = np.zeros(eligible.shape, dtype=bool)
        for x, y in background_seeds:
            if not (0 <= x < rgba.width and 0 <= y < rgba.height) or not eligible[y, x]:
                raise ValueError('Enclosed-background seed does not match the source background')
            hole_seeds[y, x] = True
        holes = ndi.binary_propagation(hole_seeds, mask=eligible)
        mask[holes] = False
    # Estimate foreground colour from a known interior pixel, not the maximum
    # contrast of one neighbour. This separates JPEG ringing from real coverage.
    core = ndi.binary_erosion(mask, iterations=3)
    outer = ndi.binary_dilation(mask, iterations=3)
    _, indices = ndi.distance_transform_edt(~core, return_indices=True)
    estimated = rgb[indices[0], indices[1]]
    vector = estimated - background
    denominator = np.sum(vector * vector, axis=2)
    coverage = np.clip(np.sum((rgb-background)*vector, axis=2) / np.maximum(denominator, 1), 0, 1)
    # Near-background foreground colours cannot support reliable colour matting.
    # Keep the spatial contour there rather than dividing by near-zero contrast.
    spatial = ndi.gaussian_filter(mask.astype(np.float32), 0.65)
    coverage = np.where(denominator < 900, spatial, coverage)
    coverage[core] = 1
    coverage[~outer] = 0
    coverage[coverage < 0.06] = 0
    coverage[coverage > 0.98] = 1
    # Subpixel antialiasing after colour estimation suppresses stair-stepping
    # along long diagonal chassis edges, without blurring interior RGB.
    coverage = ndi.gaussian_filter(coverage, 0.55)
    coverage[core] = 1
    coverage[~outer] = 0
    coverage[coverage < 0.01] = 0
    coverage[coverage > 0.995] = 1
    alpha = np.round(coverage*255).astype(np.uint8)
    partial = (alpha > 0) & (alpha < 255)
    coverage = np.maximum(alpha.astype(np.float32)/255, 1/255)
    foreground = (rgb - background*(1-coverage[:,:,None])) / coverage[:,:,None]
    pixels[partial, :3] = np.round(foreground[partial]).clip(0,255).astype(np.uint8)
    pixels[:, :, 3] = alpha
    return Image.fromarray(pixels), {'method':'connected mask with local colour matting', 'backgroundRGB':background.tolist(),
                                     'removedPercent':round(float((alpha==0).mean()*100),2),
                                     'partialEdgePixels':int(partial.sum())}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-dir',type=Path,help='Optional original images named THEME-ID.png')
    parser.add_argument('--tolerance',type=int,default=10)
    parser.add_argument('--closing-radius',type=int,default=2,help='Contour gap closing radius; larger values require careful review')
    args=parser.parse_args()
    if not 1 <= args.closing_radius <= 40: parser.error('closing radius must be between 1 and 40')
    if not 0 <= args.tolerance <= 40: parser.error('tolerance must be between 0 and 40')
    root=Path(__file__).resolve().parents[1]
    output=args.output.resolve()
    if output == root/'Images' or root/'Images' in output.parents:
        parser.error('Use a separate review output directory')
    output.mkdir(parents=True,exist_ok=True)
    metadata=json.loads((root/'comparisons.json').read_text())
    settings=json.loads((Path(__file__).with_name('background-removal-settings.json')).read_text())
    report=[]; cards=[]
    for theme,reference in metadata.items():
        start=time.perf_counter()
        source=root/'Images'/reference['keyboardImage']
        if args.source_dir and (not reference.get('transparentBackground') or reference.get('backgroundProcessing')):
            source=args.source_dir/(theme+'.png')
        original=Image.open(source).convert('RGBA')
        preset=settings.get(theme,{})
        if preset and hashlib.sha256(source.read_bytes()).hexdigest() != preset['sourceSHA256']:
            raise ValueError(f'{theme}: use the reviewed full-resolution original with --source-dir; its mask is not valid for a recompressed preview')
        tolerance=preset.get('tolerance',args.tolerance)
        result,details=remove_background(original,tolerance,args.closing_radius,preset.get("backgroundSeeds",[]))
        name=theme+'.png'
        if details['method'] == 'existing alpha preserved':
            import shutil
            shutil.copyfile(root/'Images'/reference['keyboardImage'],output/name)
        else:
            result.save(output/name,optimize=True)
        # Verify all fully opaque product pixels retain their exact source RGB.
        before=np.array(original);after=np.array(result);opaque=after[:,:,3]==255
        assert np.array_equal(before[:,:,:3][opaque],after[:,:,:3][opaque])
        details.update(tolerance=tolerance, source=str(source), sourceURL=reference["sourceImage"], closingRadius=args.closing_radius, theme=theme,seconds=round(time.perf_counter()-start,3),size=list(result.size),bytes=(output/name).stat().st_size)
        report.append(details)
        thumb=result.copy();thumb.thumbnail((380,330))
        cards.append((reference['model'],thumb))
        print(theme,details['method'],details['seconds'],flush=True)
    for page,start in enumerate(range(0,len(cards),6),1):
        sheet=Image.new('RGB',(1200,780),'#dddddd');draw=ImageDraw.Draw(sheet)
        for i,(title,thumb) in enumerate(cards[start:start+6]):
            x=(i%3)*400;y=(i//3)*390
            draw.rectangle((x,y,x+399,y+345),fill='#242427')
            sheet.paste(thumb,(x+(400-thumb.width)//2,y+(345-thumb.height)//2),thumb)
            draw.text((x+8,y+353),title,fill='#111111')
        sheet.save(output/f'review-{page}.png')
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    body=''.join(f'<article><h2>{html.escape(r["model"])}</h2><div class="pair"><img src="{k}.png"><img src="{k}.png" class="light"></div><a href="{k}.png">Full resolution PNG</a></article>' for k,r in metadata.items())
    (output/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Keyboard cutout review</title><style>body{font:16px system-ui;margin:32px;background:#eee}article{margin:32px 0}h2{font-size:20px}.pair{display:flex;gap:16px}img{width:45%;max-width:600px;background:#242427;object-fit:contain}.light{background:white}</style><h1>Keyboard cutout review</h1><p>Original pixels with locally calculated transparency. Compare dark and white backgrounds.</p>'+body)
    print('Review:',output/'review.html')

if __name__=='__main__':main()
