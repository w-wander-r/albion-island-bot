"""
Island configurations and garden plot layouts.
Edit this to match your specific islands and garden arrangements.
"""
import json
from pathlib import Path

class Island:
    """Represents a single island with its garden layout."""
    
    def __init__(self, name, travel_tab_index, garden_plots):
        self.name = name
        self.travel_tab_index = travel_tab_index  # Position in favorites tab
        self.garden_plots = garden_plots  # List of (x, y) plot positions
    
    def to_dict(self):
        return {
            "name": self.name,
            "travel_tab_index": self.travel_tab_index,
            "garden_plots": self.garden_plots
        }

# Load island configurations from JSON
def load_islands():
    """Load island configurations from islands.json"""
    islands_file = Path(__file__).parent / "islands.json"
    
    if not islands_file.exists():
        # Create default empty config
        default = {
            "islands": [],
            "travel_menu": {
                "favorite_tab_position": (0, 0),  # UI coordinates
                "confirm_travel_position": (0, 0)
            }
        }
        with open(islands_file, 'w') as f:
            json.dump(default, f, indent=2)
        print(f"Created default islands.json - please edit it with your island details")
        return []
    
    with open(islands_file, 'r') as f:
        data = json.load(f)
    
    islands = []
    for island_data in data.get("islands", []):
        island = Island(
            name=island_data["name"],
            travel_tab_index=island_data["travel_tab_index"],
            garden_plots=island_data.get("garden_plots", [])
        )
        islands.append(island)
    
    return islands

# Example structure for islands.json:
"""
{
    "islands": [
        {
            "name": "Personal Island",
            "travel_tab_index": 0,
            "garden_plots": [
                [100, 200],
                [150, 200],
                [200, 200]
            ]
        },
        {
            "name": "Guild Island",
            "travel_tab_index": 1,
            "garden_plots": [
                [100, 300],
                [150, 300]
            ]
        }
    ],
    "travel_menu": {
        "favorite_tab_position": [50, 100],
        "confirm_travel_position": [500, 400]
    }
}
"""