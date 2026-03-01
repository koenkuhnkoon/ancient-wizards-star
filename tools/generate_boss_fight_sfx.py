"""Generate sound_brief_boss_fights.md assets as 44.1kHz 16-bit mono WAV."""

from __future__ import annotations

from pathlib import Path
import math
import random
import struct
import wave


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sounds"
SR = 44100


def clamp(x: float) -> float:
    return -1.0 if x < -1.0 else (1.0 if x > 1.0 else x)


def envelope(n: int, a: float, d: float, s: float, r: float) -> list[float]:
    aa = int(n * a)
    dd = int(n * d)
    rr = int(n * r)
    ss = max(0, n - aa - dd - rr)
    out = [0.0] * n
    i = 0
    for _ in range(aa):
        out[i] = (i + 1) / max(1, aa)
        i += 1
    for j in range(dd):
        t = j / max(1, dd)
        out[i] = 1.0 + (s - 1.0) * t
        i += 1
    for _ in range(ss):
        out[i] = s
        i += 1
    for j in range(rr):
        t = j / max(1, rr)
        out[i] = s * (1.0 - t)
        i += 1
    return out


def low_noise(n: int, alpha: float) -> list[float]:
    y = 0.0
    out = []
    for _ in range(n):
        x = random.uniform(-1.0, 1.0)
        y += alpha * (x - y)
        out.append(y)
    return out


def sine(freq: float, n: int) -> list[float]:
    out = [0.0] * n
    ph = 0.0
    st = 2.0 * math.pi * freq / SR
    for i in range(n):
        out[i] = math.sin(ph)
        ph += st
    return out


def chirp(f0: float, f1: float, n: int) -> list[float]:
    out = [0.0] * n
    for i in range(n):
        t = i / max(1, n - 1)
        f = f0 + (f1 - f0) * t
        out[i] = math.sin(2.0 * math.pi * f * (i / SR))
    return out


def mix(*signals: list[float]) -> list[float]:
    n = max(len(s) for s in signals)
    out = [0.0] * n
    for s in signals:
        for i, v in enumerate(s):
            out[i] += v
    return out


def scale(sig: list[float], g: float) -> list[float]:
    return [v * g for v in sig]


def apply_env(sig: list[float], a: float, d: float, s: float, r: float) -> list[float]:
    e = envelope(len(sig), a, d, s, r)
    return [sig[i] * e[i] for i in range(len(sig))]


def normalize(sig: list[float], peak: float = 0.92) -> list[float]:
    m = max(1e-9, max(abs(v) for v in sig))
    g = peak / m
    return [v * g for v in sig]


def write(name: str, sig: list[float]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    sig = normalize(sig)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        b = bytearray()
        for v in sig:
            b.extend(struct.pack("<h", int(clamp(v) * 32767)))
        w.writeframes(bytes(b))


def monster_sfx() -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}

    n = int(0.3 * SR)
    out["enemy_evil_ninja_attack.wav"] = apply_env(mix(scale(chirp(2200, 600, n), 0.5), scale(low_noise(n, 0.45), 0.2)), 0.01, 0.2, 0.2, 0.4)

    n = int(0.4 * SR)
    bones = mix(scale(chirp(460, 220, n), 0.35), scale(low_noise(n, 0.18), 0.25))
    out["enemy_skeleton_attack.wav"] = apply_env(bones, 0.01, 0.25, 0.25, 0.3)

    n = int(0.5 * SR)
    wet = mix(scale(chirp(180, 90, n), 0.35), scale(low_noise(n, 0.08), 0.35))
    out["enemy_zombie_attack.wav"] = apply_env(wet, 0.02, 0.25, 0.4, 0.3)

    n = int(0.4 * SR)
    splat = mix(scale(low_noise(n, 0.25), 0.45), scale(chirp(280, 120, n), 0.2))
    out["enemy_sewage_creature_attack.wav"] = apply_env(splat, 0.01, 0.25, 0.25, 0.35)

    n = int(0.4 * SR)
    thwack = mix(scale(chirp(600, 180, n), 0.35), scale(low_noise(n, 0.22), 0.3))
    pop = [0.0] * n
    for i in range(int(0.03 * SR)):
        pop[int(0.28 * SR) + i] = math.sin(2 * math.pi * 900 * i / SR) * (1 - i / int(0.03 * SR)) * 0.35
    out["enemy_land_octopus_attack.wav"] = apply_env(mix(thwack, pop), 0.01, 0.2, 0.3, 0.3)

    n = int(0.3 * SR)
    zing = mix(scale(chirp(1800, 900, n), 0.3), scale(sine(2400, n), 0.18))
    out["enemy_little_devil_attack.wav"] = apply_env(zing, 0.005, 0.18, 0.2, 0.3)

    n = int(0.4 * SR)
    puff = mix(scale(low_noise(n, 0.33), 0.3), scale(chirp(900, 350, n), 0.2))
    hiss = [0.0] * n
    for i in range(int(0.12 * SR)):
        idx = n - int(0.14 * SR) + i
        if 0 <= idx < n:
            hiss[idx] = random.uniform(-1, 1) * 0.12
    out["enemy_poisonous_mushroom_attack.wav"] = apply_env(mix(puff, hiss), 0.01, 0.2, 0.25, 0.35)

    n = int(0.5 * SR)
    snap = mix(scale(chirp(900, 180, n), 0.42), scale(low_noise(n, 0.35), 0.18))
    click = [0.0] * n
    for i in range(int(0.05 * SR)):
        click[int(0.3 * SR) + i] = math.sin(2 * math.pi * 500 * i / SR) * (1 - i / int(0.05 * SR)) * 0.25
    out["enemy_stonehead_turtle_attack.wav"] = apply_env(mix(snap, click), 0.01, 0.24, 0.3, 0.3)
    return out


def boss_sfx() -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}

    n = int(0.5 * SR)
    grim = mix(scale(chirp(140, 70, n), 0.45), scale(low_noise(n, 0.12), 0.3))
    out["boss_grimrak_attack.wav"] = apply_env(grim, 0.01, 0.23, 0.35, 0.3)

    n = int(0.8 * SR)
    boom = mix(scale(chirp(120, 40, n), 0.45), scale(low_noise(n, 0.08), 0.35))
    rumble = [math.sin(2 * math.pi * 45 * i / SR) * 0.2 for i in range(n)]
    out["boss_grimrak_slam.wav"] = apply_env(mix(boom, rumble), 0.01, 0.15, 0.45, 0.35)

    n = int(0.4 * SR)
    zcharge = mix(scale(chirp(350, 1100, n), 0.33), scale(low_noise(n, 0.28), 0.2))
    out["boss_zara_attack.wav"] = apply_env(zcharge, 0.01, 0.2, 0.3, 0.3)

    n = int(0.4 * SR)
    zfire = mix(scale(chirp(1200, 500, n), 0.35), scale(chirp(700, 1400, n), 0.18), scale(low_noise(n, 0.35), 0.16))
    out["boss_zara_bolt_fire.wav"] = apply_env(zfire, 0.005, 0.18, 0.25, 0.35)

    n = int(0.3 * SR)
    zhit = mix(scale(chirp(1800, 500, n), 0.28), scale(sine(2300, n), 0.16), scale(low_noise(n, 0.42), 0.18))
    out["boss_zara_bolt_hit.wav"] = apply_env(zhit, 0.005, 0.2, 0.2, 0.3)

    n = int(0.4 * SR)
    vslash = mix(scale(chirp(1600, 450, n), 0.28), scale(low_noise(n, 0.38), 0.2), scale(chirp(220, 120, n), 0.2))
    out["boss_voltrak_attack.wav"] = apply_env(vslash, 0.01, 0.2, 0.2, 0.35)

    n = int(0.4 * SR)
    vbolt = mix(scale(chirp(2000, 900, n), 0.3), scale(sine(2600, n), 0.12), scale(low_noise(n, 0.4), 0.2))
    out["boss_voltrak_bolt.wav"] = apply_env(vbolt, 0.005, 0.18, 0.2, 0.35)

    n = int(1.0 * SR)
    hum = [math.sin(2 * math.pi * 70 * i / SR) * (0.2 + 0.2 * (i / n)) for i in range(n)]
    burst = [0.0] * n
    for i in range(int(0.2 * SR)):
        idx = int(0.45 * SR) + i
        burst[idx] = math.sin(2 * math.pi * (1000 - i * 2) * i / SR) * (1 - i / int(0.2 * SR)) * 0.35
    out["boss_voltrak_shockwave.wav"] = apply_env(mix(hum, burst, scale(low_noise(n, 0.18), 0.18)), 0.02, 0.2, 0.4, 0.3)

    n = int(1.5 * SR)
    rise = mix(scale(chirp(120, 1700, n), 0.28), scale(low_noise(n, 0.2), 0.2))
    th = [0.0] * n
    for i in range(int(0.28 * SR)):
        idx = n - int(0.35 * SR) + i
        th[idx] = math.sin(2 * math.pi * 80 * i / SR) * (1 - i / int(0.28 * SR)) * 0.45
    out["boss_voltrak_intro.wav"] = apply_env(mix(rise, th), 0.02, 0.2, 0.55, 0.2)
    return out


def event_sfx() -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}

    n = int(1.2 * SR)
    portal = mix(scale(chirp(250, 850, n), 0.26), scale(low_noise(n, 0.18), 0.22), scale(chirp(900, 350, n), 0.2))
    out["portal_enter.wav"] = apply_env(portal, 0.04, 0.2, 0.5, 0.22)

    n = int(0.6 * SR)
    summon = [0.0] * n
    notes = [660, 880, 1100]
    for j, f in enumerate(notes):
        start = int(j * 0.1 * SR)
        dur = int(0.28 * SR)
        t = min(dur, n - start)
        if t <= 0:
            continue
        tone = apply_env(sine(f, t), 0.05, 0.2, 0.35, 0.25)
        for i in range(t):
            summon[start + i] += tone[i] * 0.25
    out["companion_summon.wav"] = mix(summon, scale(low_noise(n, 0.45), 0.08))

    n = int(3.0 * SR)
    fan = [0.0] * n
    seq = [(392, 0.28), (392, 0.28), (523, 0.28), (784, 0.9), (988, 0.8)]
    t0 = 0
    for f, d in seq:
        start = int(t0 * SR)
        dur = int(d * SR)
        tone = mix(scale(sine(f, dur), 0.28), scale(sine(f * 2, dur), 0.11))
        tone = apply_env(tone, 0.05, 0.2, 0.55, 0.2)
        for i in range(min(dur, n - start)):
            fan[start + i] += tone[i]
        t0 += d * 0.75
    out["victory_fanfare.wav"] = mix(fan, scale(low_noise(n, 0.34), 0.05))
    return out


def main() -> int:
    all_sfx = {}
    all_sfx.update(monster_sfx())
    all_sfx.update(boss_sfx())
    all_sfx.update(event_sfx())
    for name, sig in all_sfx.items():
        write(name, sig)
    print(f"Generated {len(all_sfx)} boss-fight sound files in assets/sounds/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
