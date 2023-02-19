# happy-metadata
Meta-data format for the [Happy framework](https://github.com/wairas/happy), working with hyper-spectral data.
Offers global and per-pixel meta-data. The meta-data is hierarchical, 
i.e., if a meta-data key is not found at the pixel-level, then the 
global meta-data is checked. Data like sample ID are therefore available at the pixel level as well.


## Format

To make it more efficient to manage sample-wide meta-data, the format is split into two separate JSON files:

* `.global` - contains global (per image) meta-data
* `.pixels` - contains meta-data on a per-pixel basis

### .global

Required entry names for the `.global` file:

* `filename`: the name of the hyper-spectral image, e.g., an ENVI image
* `sample_id`: the ID of the sample that was imaged or the coordinates in case of GIS data  

### .pixels

* If a pixel is not specified, default values from the `default` section (from the `.global` file) will be returned.
* You can define whether the pixel data is stored `row-wise` or `column-wise` (entry `type`).
* Row and column indices are 0-based.


## Example

The example below stores the pixel meta-data in `column-wise` fashion:

* `012345678-20230202_1234.global`

```json
{
  "filename": "012345678-20230202_1234.hdr",
  "sample_id": "012345678",
  "default": {
    "type": "BG"
  }
}
```

* `012345678-20230202_1234.pixels`

```json
{
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
```
