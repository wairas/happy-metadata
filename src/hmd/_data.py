import json
import os

from datetime import datetime


# global meta-data
GLOBAL_EXT = ".global"
SAMPLE_ID = "sample_id"
FILENAME = "filename"
DEFAULT = "default"

# pixels meta-data
PIXELS_EXT = ".pixels"
ROW_WISE = "row-wise"
COLUMN_WISE = "column-wise"
TYPE = "type"


class MetaDataManager(object):
    """
    Class for managing meta-data store in a JSON file.
    """

    def __init__(self, source, required=None):
        """
        Initializes the meta-data manager. Either filename or data need to be
        provided.
        
        :param source: the filename of the JSON file or a dictionary with the meta-data
        :param required: the list of require key names in the meta-data
        :type required: list
        """
        if source is None:
            raise Exception("Source cannot be None!")
        if not (isinstance(source, str) or isinstance(source, dict)):
            raise Exception("Source has to be either a filename or data dictionary, but got: %s" % str(type(source)))

        self.filename = source if isinstance(source, str) else None
        self._data = source if isinstance(source, dict) else None
        self.required = required

    @property
    def data(self):
        """
        Returns the underlying data, loads it if necessary.

        :return: the data
        :rtype: dict
        """
        if self._data is None:
            self._load()
        return self._data

    def _load(self):
        """
        Loads the meta-data from disk.
        """
        if self.filename is None:
            raise Exception("No filename specified, cannot load meta-data from disk!")
        with open(self.filename, "r") as fp:
            data = json.load(fp)
        if self.required is not None:
            for k in self.required:
                if k not in data:
                    raise Exception("Missing meta-data key: %s" % k)
        self._data = data

    @property
    def is_loaded(self):
        """
        Returns whether the data has been loaded.

        :return: True if loaded
        :rtype: bool
        """
        return self._data is not None


class HappyMetaData(object):
    """
    Class for managing meta-data hyper-spectral data.
    """

    def __init__(self, source_global=None, source_pixels=None):
        """
        Initializes the meta-datac container.

        :param source_global: the global meta-data dictionary or filename
        :type source_global: dict or str
        :param source_pixels: the pixel meta-data dictionary or filename
        :type source_pixels: dict or str
        """
        self._meta_global = MetaDataManager(source_global, required=[FILENAME, SAMPLE_ID])
        self._meta_pixels = MetaDataManager(source_pixels, required=[TYPE])

    @property
    def filename(self):
        """
        Returns the filename, if any.

        :return: the filename
        :rtype: str
        """
        return self.get(FILENAME, def_value="")

    @filename.setter
    def filename(self, value):
        """
        Sets the filename.

        :param value: the new filename
        :type value: str
        """
        self.set(FILENAME, value)

    @property
    def sample_id(self):
        """
        Returns the sample ID, if any.

        :return: the filename
        :rtype: str
        """
        return self.get(SAMPLE_ID, def_value="")

    @sample_id.setter
    def sample_id(self, value):
        """
        Sets the sample ID.

        :param value: the new sample ID
        :type value: str
        """
        self.set(SAMPLE_ID, value)

    def get(self, field, row=None, col=None, def_value=None):
        """
        Returns the value of the field or the default value if not present.
        If row and col are None, global meta-data is directly accessed, otherwise
        the pixel meta-data (width fallback on the global meta-data).

        :param field: the field to return the value for
        :type field: str
        :param row: the row in the pixels to access
        :type row: int
        :param col: the column in the pixels to access
        :param def_value: the default value to return
        :type def_value: object
        :return: the associated value or the default value
        :rtype: object
        """
        result = def_value

        if (row is None) or (col is None):
            if field in self._meta_global.data:
                result = self._meta_global.data[field]
        else:
            found = False
            if self._meta_pixels.data[TYPE] == ROW_WISE:
                if row in self._meta_pixels.data:
                    if col in self._meta_pixels.data[row]:
                        if field in self._meta_pixels.data[row][col]:
                            result = self._meta_pixels.data[row][col][field]
                            found = True
            elif self._meta_pixels.data[TYPE] == COLUMN_WISE:
                if col in self._meta_pixels.data:
                    if row in self._meta_pixels.data[col]:
                        if field in self._meta_pixels.data[col][row]:
                            result = self._meta_pixels.data[col][row][field]
                            found = True
            else:
                raise Exception("Pixel data must be either stored in '%s' or '%s' fashion (key: %s)" % (ROW_WISE, COLUMN_WISE, TYPE))

            # check global meta-data?
            if not found:
                if DEFAULT in self._meta_global.data:
                    if field in self._meta_global.data[DEFAULT]:
                        result = self._meta_global.data[DEFAULT][field]
                        found = True
            if not found:
                if field in self._meta_global.data:
                    result = self._meta_global.data[field]

        return result

    def set(self, field, value, row=None, col=None):
        """
        Sets the meta-data value.

        :param field: the name of the meta-data value to set
        :type field: str
        :param value: the value to set (int, float, str, bool)
        :param row: the row, when setting in the pixels meta-data, None when setting in global meta-data
        :type row: int
        :param col:the column, when setting in the pixels meta-data, None when setting in global meta-data
        :type col: int
        """
        if (value is not None) and not isinstance(value, (int, float, str, bool)):
            raise Exception("Only accepting: int/float/str/bool but got: %s" % str(type(value)))
        if (row is None) or (col is None):
            self._meta_global.data[field] = value
        else:
            if self._meta_pixels.data[TYPE] == ROW_WISE:
                if row not in self._meta_pixels.data:
                    self._meta_pixels.data[row] = dict()
                if col not in self._meta_pixels.data[row]:
                    self._meta_pixels.data[row][col] = dict()
                self._meta_pixels.data[row][col][field] = value
            elif self._meta_pixels.data[TYPE] == COLUMN_WISE:
                if col not in self._meta_pixels.data:
                    self._meta_pixels.data[col] = dict()
                if row not in self._meta_pixels.data[col]:
                    self._meta_pixels.data[col][row] = dict()
                self._meta_pixels.data[col][row][field] = value
            else:
                raise Exception("Pixel data must be either stored in '%s' or '%s' fashion (key: %s)" % (ROW_WISE, COLUMN_WISE, TYPE))

    def save_global(self, fname, indent=None):
        """
        Saves the global data to the specified file.

        :param fname: the file to save the global meta-data to
        :rtype fname: str
        :param indent: the indentation to use, None uses minimal whitespaces
        :type indent: int
        """
        with open(fname, "w") as fp:
            json.dump(self._meta_global.data, fp, indent=indent)

    def save_pixels(self, fname, indent=None):
        """
        Saves the pixel data to the specified file.

        :param fname: the file to save the pixel meta-data to
        :rtype fname: str
        :param indent: the indentation to use, None uses minimal whitespaces
        :type indent: int
        """
        with open(fname, "w") as fp:
            json.dump(self._meta_pixels.data, fp, indent=indent)

    def save(self, dname, indent=None):
        """
        Saves the global and pixel data to the specified directory, using the
        sample ID as prefix.

        :param dname: the directory to save the meta-data to
        :type dname: str
        :param indent: the indentation to use, None uses minimal whitespaces
        :type indent: int
        """
        if (self.sample_id is None) or (len(self.sample_id) == 0):
            raise Exception("No sample ID available, cannot generate output filenames automatically!")

        self.save_global(os.path.join(dname, self.sample_id + GLOBAL_EXT), indent=indent)
        self.save_pixels(os.path.join(dname, self.sample_id + PIXELS_EXT), indent=indent)

    def __str__(self):
        """
        Returns a simple string representation.

        :return: the generated string
        :rtype: str
        """
        if self._meta_pixels.is_loaded:
            size = str(len(self._meta_pixels.data))
        else:
            size = "unknown (not loaded yet)"
        return "global: %s\npixels: size=%s" % (str(self._meta_global.data), size)

    @classmethod
    def empty(cls, row_wise=True):
        """
        Returns an empty meta-data instance.

        :param row_wise: whether the pixels are organized row-wise or column-wise
        :type row_wise: bool
        :return: the meta-data instance
        :rtype: HappyMetaData
        """
        return HappyMetaData(
            source_global={FILENAME: "none", SAMPLE_ID: str(datetime.now())},
            source_pixels={TYPE: ROW_WISE if row_wise else COLUMN_WISE})

    @classmethod
    def load(cls, fname):
        """
        Uses the filename as template for .global/.pixels and loads the meta-data.
        .pixels file is optional.

        :param fname: the filename template to use
        :type fname: str
        :return: the meta-data
        :rtype: HappyMetaData
        """
        gname = os.path.splitext(fname)[0] + GLOBAL_EXT
        pname = os.path.splitext(fname)[0] + PIXELS_EXT
        if not os.path.exists(gname):
            raise Exception("Global JSON file does not exist: %s" % gname)
        if os.path.exists(pname):
            return HappyMetaData(source_global=gname, source_pixels=pname)
        else:
            return HappyMetaData(source_global=gname, source_pixels={TYPE: ROW_WISE})
