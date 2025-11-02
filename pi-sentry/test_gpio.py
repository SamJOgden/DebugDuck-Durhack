#!/usr/bin/env python3
"""Quick test to check gpiod access"""
import gpiod
from gpiod.line import Direction, Edge

print("Testing gpiod 2.x access...")
print(f"gpiod version: {gpiod.__version__}")

for chip_name in ['/dev/gpiochip4', '/dev/gpiochip0', '/dev/gpiochip1']:
    try:
        print(f"\nTrying {chip_name}...")
        chip = gpiod.Chip(chip_name)
        print(f"  ✅ Chip opened successfully")

        # Try to request GPIO 17 with gpiod 2.x API
        line_config = {17: gpiod.LineSettings(direction=Direction.INPUT, edge_detection=Edge.RISING)}
        request = chip.request_lines(consumer="test", config=line_config)
        print(f"  ✅ Successfully requested GPIO 17 for rising edge events")

        request.release()
        chip.close()
        print(f"  ✅ {chip_name} works perfectly!")
        print(f"\n🎉 SUCCESS! Use {chip_name} for GPIO")
        break

    except Exception as e:
        print(f"  ❌ Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\nDone!")
