# ============================================================
# CELL 1: Auth & Init (same as before)
# ============================================================
!pip install earthengine-api matplotlib imageio[ffmpeg] pillow requests -q

import ee

ee.Authenticate()
ee.Initialize(
    project='promising-idea-432505-i4',
    opt_url='https://earthengine-highvolume.googleapis.com'
)

print("✅ Done")


# ============================================================
# CELL 2: DEBUG - Check AOI & Image Count First
# ============================================================
import ee

aoi = ee.FeatureCollection('projects/promising-idea-432505-i4/assets/AOI')
roi = aoi.geometry()

# --- Check AOI is valid ---
print("AOI feature count:", aoi.size().getInfo())
print("AOI bounds:", roi.bounds().getInfo())

# --- Check Landsat 5 image count for 2004 ---
l5 = (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
      .filterBounds(roi)
      .filterDate('2004-01-01', '2004-12-31'))
print("\nLandsat 5 images in 2004:", l5.size().getInfo())

# --- Check Landsat 8 image count for 2020 ---
l8 = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
      .filterBounds(roi)
      .filterDate('2020-01-01', '2020-12-31'))
print("Landsat 8 images in 2020:", l8.size().getInfo())



# CELL 3

import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

def mask_l5(image):
    qa = image.select('QA_PIXEL')
    mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
    return image.updateMask(mask)

def mask_l8(image):
    qa = image.select('QA_PIXEL')
    mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
    return image.updateMask(mask)

# Test NDVI for 2005 (Landsat 5)
col_l5 = (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
           .filterBounds(roi)
           .filterDate('2005-01-01', '2005-12-31')
           .map(mask_l5))

ndvi_l5 = col_l5.map(lambda img: img.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI'))
ndvi_2005 = ndvi_l5.mean().clip(roi)

# Test NDVI for 2020 (Landsat 8)
col_l8 = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
           .filterBounds(roi)
           .filterDate('2020-01-01', '2020-12-31')
           .map(mask_l8))

ndvi_l8 = col_l8.map(lambda img: img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI'))
ndvi_2020 = ndvi_l8.mean().clip(roi)

# --- Check actual NDVI value range ---
stats_2005 = ndvi_2005.reduceRegion(
    reducer=ee.Reducer.minMax(),
    geometry=roi,
    scale=30,
    maxPixels=1e9
).getInfo()
print("NDVI 2005 stats:", stats_2005)

stats_2020 = ndvi_2020.reduceRegion(
    reducer=ee.Reducer.minMax(),
    geometry=roi,
    scale=30,
    maxPixels=1e9
).getInfo()
print("NDVI 2020 stats:", stats_2020)



import ee # Added import
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

ee.Authenticate()
ee.Initialize(
    project='promising-idea-432505-i4',
    opt_url='https://earthengine-highvolume.googleapis.com'
)

# Re-define aoi and roi here to make this cell self-sufficient for debugging
aoi = ee.FeatureCollection('projects/promising-idea-432505-i4/assets/AOI')
roi = aoi.geometry()

def mask_l5(image):
    qa = image.select('QA_PIXEL')
    mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
    return image.updateMask(mask)

# Re-calculate ndvi_2005 for 2005 (Landsat 5)
col_l5 = (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
           .filterBounds(roi)
           .filterDate('2005-01-01', '2005-12-31')
           .map(mask_l5))

ndvi_l5 = col_l5.map(lambda img: img.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI'))
ndvi_2005 = ndvi_l5.mean().clip(roi)

palette = ['#d73027','#f46d43','#fdae61','#fee08b',
           '#d9ef8b','#a6d96a','#66bd63','#1a9850']

# Get thumbnail URL for 2005
url_2005 = ndvi_2005.getThumbURL({
    'region': roi,
    'dimensions': 512,
    'format': 'png',
    'min': 0.0,
    'max': 0.8,
    'palette': palette
})
print("URL 2005:", url_2005)

resp = requests.get(url_2005, timeout=60)
print("HTTP status:", resp.status_code)
print("Content-Type:", resp.headers.get('Content-Type'))
print("Content size (bytes):", len(resp.content))

# Try to open the image
try:
    img = Image.open(BytesIO(resp.content)).convert('RGB')
    arr = np.array(img)
    print("Image shape:", arr.shape)
    print("Pixel value range:", arr.min(), "-", arr.max())

    plt.figure(figsize=(6,5))
    plt.imshow(arr)
    plt.title("NDVI 2005 - TEST FRAME")
    plt.axis('off')
    plt.show()
    print("✅ Single frame looks good!")
except Exception as e:
    print("❌ Image open failed:", e)
    print("Raw response:", resp.content[:200])





import ee
import numpy as np
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter, PillowWriter
from IPython.display import display, Video, Image as IPImage

aoi = ee.FeatureCollection('projects/promising-idea-432505-i4/assets/AOI')
roi = aoi.geometry()

# ---- Cloud mask (same for both sensors) ----
def cloud_mask(image):
    qa = image.select('QA_PIXEL')
    mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
    return image.updateMask(mask)

# ---- NDVI using SR_ prefix band names ----
def ndvi_l5(image):
    # Landsat 5 C2 T1_L2: NIR=SR_B4, Red=SR_B3
    return image.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')

def ndvi_l8(image):
    # Landsat 8 C2 T1_L2: NIR=SR_B5, Red=SR_B4
    return image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')

palette = ['#d73027','#f46d43','#fdae61','#fee08b',
           '#d9ef8b','#a6d96a','#66bd63','#1a9850']

years  = list(range(2004, 2026))
frames = []
labels = []
sensor_names = []
failed = []

print("Downloading NDVI frames...\n")

for year in years:
    try:
        start = f'{year}-01-01'
        end   = f'{year}-12-31'

        if year <= 2012:
            col = (ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
                   .filterBounds(roi)
                   .filterDate(start, end)
                   .map(cloud_mask))
            ndvi_col = col.map(ndvi_l5)
            sensor   = 'Landsat 5'
        else:
            col = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                   .filterBounds(roi)
                   .filterDate(start, end)
                   .map(cloud_mask))
            ndvi_col = col.map(ndvi_l8)
            sensor   = 'Landsat 8'

        count = col.size().getInfo()
        if count == 0:
            print(f"  ⚠️  {year}: 0 images — skipping")
            failed.append(year)
            continue

        ndvi_img = ndvi_col.mean().clip(roi)

        # Auto-detect value range
        stats = ndvi_img.reduceRegion(
            reducer=ee.Reducer.percentile([2, 98]),
            geometry=roi,
            scale=30,
            maxPixels=1e9
        ).getInfo()

        vmin = float(stats.get('NDVI_p2') or 0.0)
        vmax = float(stats.get('NDVI_p98') or 0.8)
        vmin = max(vmin, -0.1)
        vmax = min(vmax,  1.0)
        if vmax - vmin < 0.1:   # fallback if range too narrow
            vmin, vmax = 0.0, 0.8

        url = ndvi_img.getThumbURL({
            'region': roi,
            'dimensions': 512,
            'format': 'png',
            'min': vmin,
            'max': vmax,
            'palette': palette
        })

        resp = requests.get(url, timeout=90)
        resp.raise_for_status()

        arr = np.array(Image.open(BytesIO(resp.content)).convert('RGB'))
        frames.append(arr)
        labels.append(str(year))
        sensor_names.append(sensor)
        print(f"  ✅ {year} ({sensor}) | {count} imgs | NDVI [{vmin:.2f}–{vmax:.2f}]")

    except Exception as e:
        print(f"  ❌ {year}: {e}")
        failed.append(year)

print(f"\n✅ Downloaded: {len(frames)} | ❌ Failed: {len(failed)}")





# ============================================================
# CLEAN LAYOUT - No timeline bar, year shown bold on frame
# ============================================================

fps      = 2
repeat_n = 2

exp_frames, exp_labels, exp_sensors = [], [], []
for f, l, s in zip(frames, labels, sensor_names):
    for _ in range(repeat_n):
        exp_frames.append(f)
        exp_labels.append(l)
        exp_sensors.append(s)

total_sec = len(exp_frames) / fps
print(f"🎬 {total_sec:.0f} sec")

palette = ['#d73027','#f46d43','#fdae61','#fee08b',
           '#d9ef8b','#a6d96a','#66bd63','#1a9850']

import matplotlib.colors as mcolors
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter, FFMpegWriter
import matplotlib.pyplot as plt
from IPython.display import display, Video, Image as IPImage
from google.colab import files

# ── Figure ───────────────────────────────────────────────────
fig = plt.figure(figsize=(9, 9), dpi=120, facecolor='#0d1117')

# ── Axes layout ──────────────────────────────────────────────
# [left, bottom, width, height]
ax_img = fig.add_axes([0.05, 0.18, 0.90, 0.75])   # image
ax_cb  = fig.add_axes([0.08, 0.09, 0.84, 0.04])   # colorbar

ax_img.axis('off')

# ── NDVI image ───────────────────────────────────────────────
im = ax_img.imshow(exp_frames[0])

# ── Year — large text INSIDE the image (top-left corner) ─────
year_txt = ax_img.text(
    0.02, 0.97, exp_labels[0],
    transform=ax_img.transAxes,
    ha='left', va='top',
    fontsize=36, fontweight='bold', color='white',
    bbox=dict(facecolor='#000000aa', edgecolor='none',
              boxstyle='round,pad=0.3')
)

# ── Sensor — inside image (top-right corner) ─────────────────
sensor_txt = ax_img.text(
    0.98, 0.97, exp_sensors[0],
    transform=ax_img.transAxes,
    ha='right', va='top',
    fontsize=12, color='#cccccc', style='italic',
    bbox=dict(facecolor='#000000aa', edgecolor='none',
              boxstyle='round,pad=0.3')
)

# ── NDVI Scale label ─────────────────────────────────────────
fig.text(0.5, 0.155,  'NDVI Scale',
         ha='center', va='center',
         color='white', fontsize=10, fontweight='bold')

fig.text(0.08, 0.155, '◀  Bare Soil / Water',
         ha='left', va='center',
         color='#f46d43', fontsize=9, fontweight='bold')

fig.text(0.92, 0.155, 'Dense Vegetation  ▶',
         ha='right', va='center',
         color='#66bd63', fontsize=9, fontweight='bold')

# ── Colorbar ─────────────────────────────────────────────────
cmap = mcolors.LinearSegmentedColormap.from_list('ndvi', palette)
norm = mcolors.Normalize(vmin=0.0, vmax=0.8)
sm   = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

cb = fig.colorbar(sm, cax=ax_cb, orientation='horizontal')
cb.set_ticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
cb.set_ticklabels(['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8'])
cb.ax.tick_params(
    axis='x', which='both',
    colors='white', labelcolor='white',
    labelsize=10, length=6, width=1.2,
    bottom=True, labelbottom=True,
    top=False,    labeltop=False
)
cb.outline.set_edgecolor('#888888')
cb.outline.set_linewidth(1.0)

# ── Footer ───────────────────────────────────────────────────
fig.text(0.5, 0.03,
         'NDVI 2004–2025  |  Landsat 5 & 8  |  Google Earth Engine',
         ha='center', va='center',
         color='#888888', fontsize=9)

# ── Animation ────────────────────────────────────────────────
def update(i):
    im.set_data(exp_frames[i])
    year_txt.set_text(exp_labels[i])
    sensor_txt.set_text(exp_sensors[i])
    return [im, year_txt, sensor_txt]

ani = animation.FuncAnimation(
    fig, update,
    frames=len(exp_frames),
    interval=1000 / fps,
    blit=True
)
plt.close()
print("✅ Animation ready")

# ── Save ─────────────────────────────────────────────────────
gif_path = '/content/ndvi_2004_2025.gif'
mp4_path = '/content/ndvi_2004_2025.mp4'

print("💾 Saving GIF...")
ani.save(gif_path, writer=PillowWriter(fps=fps), dpi=110)
print(f"✅ GIF saved  ({total_sec:.0f} sec)")

print("💾 Saving MP4...")
ani.save(mp4_path, writer=FFMpegWriter(fps=fps, bitrate=2500), dpi=110)
print("✅ MP4 saved")

display(IPImage(gif_path))
display(Video(mp4_path, embed=True, width=700))

files.download(gif_path)
files.download(mp4_path)





import math

cols = 6
rows = math.ceil(len(frames) / cols)
fig, axes = plt.subplots(rows, cols, figsize=(18, rows*3), facecolor='#0d1117')
fig.suptitle('NDVI Preview 2004–2025', color='white', fontsize=14)

for i, ax in enumerate(axes.flat):
    ax.axis('off')
    if i < len(frames):
        ax.imshow(frames[i])
        ax.set_title(labels[i], color='white', fontsize=9, pad=2)

plt.tight_layout()
plt.savefig('/content/ndvi_grid_preview.png', dpi=80,
            bbox_inches='tight', facecolor='#0d1117')
plt.show()

