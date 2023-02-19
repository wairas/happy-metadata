# happy-metadata
Meta-data format for the [Happy framework](https://github.com/wairas/happy), working with hyper-spectral data.
Offers global and per-pixel meta-data. The meta-data is hierarchical, 
i.e., if a meta-data key is not found at the pixel-level, then the 
global meta-data is checked. Data like sample ID are therefore available 
at the pixel level as well.


## Format

The format has two sections:

* `global` - contains global (per image) meta-data
* `pixel` - contains meta-data on a per-pixel basis

Below `pixel`, you can define whether the pixel data is stored `row-wise` or 
`column-wise` (entry `type`).

Row and column indices are 0-based.

Recommended entry names for the `global` section:

* `filename`: the name of the hyper-spectral image, e.g., an ENVI image
* `sample_id`: the ID of the sample that was imaged or the coordinates in case of GIS data  

If a pixel is not specified, default values from the `default` section (under `global`) will be returned.


## Example

The example below stores the pixel meta-data in `column-wise` fashion:

```json
{
  "global": {
    "filename": "012345678-20230202_1234.hdr",
    "sample_id": "012345678",
    "default": {
      "type": "BG"
    }
  },
  "pixel": {
    "type": "column-wise",
    "0": {
      "0": {
        "nitrogen": 0.7,
        "type": "BG"
      },
      "5": {
        "nitrogen": 0.7,
        "type": "FG",
        "leaf": "0"
      }
    },
    "10": {
      "20": {
        "nitrogen": 0.7,
        "type": "FG",
        "leaf": "1"
      }
    }
  }
}
```
