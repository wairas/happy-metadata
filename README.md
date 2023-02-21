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


## Examples

### Data

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

### Code

```python
from hmd import HappyMetaData

h = "/some/where/012345678-20230202_1234.hdr"
g = "/some/where/012345678-20230202_1234.global"
p = "/some/where/012345678-20230202_1234.pixels"

# from an empty data structure
print("empty data structure")
print("====================\n")
meta = HappyMetaData.empty()
print(meta)
meta.filename = h
meta.sample_id = "012345678-20230202_1234"
meta.set("nitrogen", value=0.6, row=0, col=0)
print(meta)
meta.save("/tmp")

# loading meta-data from disk
print("\nfrom disk")
print("=========\n")
print("using explicit .global/.pixels files")
meta = HappyMetaData(source_global=g, source_pixels=p)
print(meta)
print(meta.get("nitrogen", row=0, col=0, def_value=0.7))
print(meta)
print(meta.get("nitrogen", row=0, col=0, def_value=0.7))

print("using filename template")
meta = HappyMetaData.load(h)
print(meta)
```

## Tools

### hmd-add-metadata

```
usage: hmd-add-metadata [-h] -p DIR [-r] -s FILE [-i INDEX] [-m RANGE]
                        [-I INT]

Adds (global) meta-data stored in a spreadsheet to Happy meta-data JSON files
(ext: .global).

optional arguments:
  -h, --help            show this help message and exit
  -p DIR, --path DIR    the directory with the Happy meta-data files (ext:
                        .global) (default: None)
  -r, --recursive       Whether to look for JSON files recursively. (default:
                        False)
  -s FILE, --spreadsheet FILE
                        the spreadsheet with the meta-data to add
                        (csv/xls/xslx/ods) (default: None)
  -i INDEX, --sample_id INDEX
                        the column with the sample ID (1-based index)
                        (default: first)
  -m RANGE, --meta_data RANGE
                        the range of columns with sample data (1-based
                        indices), automatically excludes sample ID (default:
                        first-last)
  -I INT, --indent INT  the indentation to use for pretty-printing the JSON
                        files (default: None)
```