# PyLEDSimulator to SLDK Simulator Migration Guide

## API Comparison

The APIs are nearly identical, making migration straightforward:

### Import Changes

```python
# OLD (PyLEDSimulator):
from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT

# NEW (SLDK):
from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group
from sldk.simulator.adafruit_display_text import Label
from sldk.simulator.terminalio import FONT
```

### Common Operations (No Changes Needed)

```python
# Device creation and initialization
device = MatrixPortalS3()
device.initialize()

# Setting pixels
device.matrix.set_pixel(x, y, color)
device.matrix.clear()

# Running the simulation
device.run(title="...", update_callback=update_function)
```

### Path Setup

Both simulators require path setup, but SLDK needs the src directory:

```python
# OLD (PyLEDSimulator):
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NEW (SLDK):
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
```

### Migration Steps

1. Update imports - replace `pyledsimulator` with `sldk.simulator`
2. Update path setup to include SLDK's src directory
3. No other code changes needed in most cases

### Example Migration

```python
# Before:
from pyledsimulator.devices import MatrixPortalS3

# After:
from sldk.simulator.devices import MatrixPortalS3
```

That's it! The rest of the code remains the same.