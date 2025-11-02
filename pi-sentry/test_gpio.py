#!/usr/bin/env python3
"""Quick test to check gpiod access"""
import gpiod

print("Testing gpiod access...")

for chip_name in ['/dev/gpiochip4', '/dev/gpiochip0', '/dev/gpiochip1']:
    try:
        print(f"\nTrying {chip_name}...")
        chip = gpiod.Chip(chip_name)
        print(f"  ✅ Chip opened successfully")

        # Try to get GPIO 17
        line = chip.get_line(17)
        print(f"  ✅ Got line 17")

        # Try to request it
        line.request(consumer="test", type=gpiod.LINE_REQ_EV_RISING_EDGE)
        print(f"  ✅ Successfully requested line 17 for rising edge events")

        line.release()
        chip.close()
        print(f"  ✅ {chip_name} works perfectly!")
        break

    except Exception as e:
        print(f"  ❌ Failed: {type(e).__name__}: {e}")

print("\nDone!")
