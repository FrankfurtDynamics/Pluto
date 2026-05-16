import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import lidar

# ── Setup ─────────────────────────────────────────────────────────────────────
lidar.start()

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={'projection': 'polar'})
ax.set_facecolor('#0d0d0f')
fig.patch.set_facecolor('#0d0d0f')
ax.set_ylim(0, 6000)          # max range in mm (6 m)
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)    # clockwise to match physical rotation
ax.tick_params(colors='#72727a')
ax.yaxis.label.set_color('#72727a')
ax.grid(color='#222228', linewidth=0.5)
ax.set_title('LiDAR Point Cloud', color='#00e5a0', pad=15)

scat = ax.scatter([], [], s=2, c='#00e5a0', alpha=0.8)
closest_scat = ax.scatter([], [], s=40, c='#ff4d4d', zorder=5)
info_text = ax.text(0.01, 0.99, '', transform=ax.transAxes,
                    color='#f0f0f2', fontsize=8, va='top',
                    fontfamily='monospace')

def update(_):
    scan = lidar.get_scan()
    if not scan:
        return scat, closest_scat, info_text

    angles = [math.radians(a) for _, a, _ in scan]
    distances = [d for _, _, d in scan]

    scat.set_offsets(list(zip(angles, distances)))
    scat.set_array(None)

    if distances:
        idx = distances.index(min(distances))
        closest_scat.set_offsets([[angles[idx], distances[idx]]])
        info_text.set_text(
            f"Points : {len(scan)}\n"
            f"Closest: {distances[idx]:.0f} mm @ {math.degrees(angles[idx]):.1f}°"
        )

    return scat, closest_scat, info_text

ani = animation.FuncAnimation(fig, update, interval=200, blit=False)

try:
    plt.tight_layout()
    plt.show()
finally:
    lidar.stop()
