# arches-bngpoint
Arches package containing the BNGPoint datatype, supporting widget and functions to sync with a geojson-feature-collection node node.

Arches v4.4.1, v5.0.0 versions and v.6.2.x are available (the 6.2.x version should work on any 6.x installation)

# Installation

To install into your Arches project run the following command:

```bat

python manage.py packages -o load_package -s /path/to/arches-bngpoint/pkg

```


# Information

## BNG Datatype

The BNG Datatype was written to contain a 12 figure alphanumeric grid reference representing the centre point location of a resource e.g. ***SU1234512345***. Details of this coordinate system can be found [here](https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid).

BNG datatype values can be searched in Advanced Search but be aware that this is a text search.

### Validation

The value must be 12 figures and zero padded if necessary e.g. ***TA123123*** must be padded to ***TA1230012300***. This is validated during a tile card.

When using the widget to enter the value it will automatically be padded before saving. It you are importing the data then it must have been padded to 12 figures before hand.


## BNG Widget

The BNG Widget is the default widget for the BNG datatype. They are linked in the BNG Widgets python config, which states the datatype that it can be used with: `"datatype": "bngcentrepoint" `

The widget accepts a text value as the input in the following formats:

* Alphanumeric BNG (deafult)
* Absolute BNG
* Long/Lat

The format is selected from the drop down to ensure it is converted to a 12 figure alphanumeric grid reference correctly.

The widget triggers the process of transforming data into a 12 character Alphanumeric BNG grid reference once focus is removed from the input textbox (i.e. when a user clicks outside the input textbox).

Error messages are displayed, in bold red text, above the Preview element to guide users when they have entered an incorrect value.

### Alphanumeric BNG
The widget checks that there is a 100km Grid Square reference at the start of the value entered and then handles the number element of the value to that the length of the number element is 10 (making a total length of 12 for the complete value). It does this by padding the easting and northing number values with 0s.

*Example input alphanumeric BNG: SP0123401234*

### Absolute BNG
The widget splits the value in half to create easting and northing. It uses the first number of the eastings and the first number of the northings to identify the correct 100km Grid Square value and then pads out the remaining numbers as necessary to achieve an Alphanumeric BNG grid reference with a length of 12.

*Example input absolute BNG: 401234,201234*

### Long/Lat

We state long/lat in that order because they represent the x/y order of coordinates to match the other two. Lat/long would reverse the order to y/x.

Using the Proj4JS module, the long/lat values (split on a comma and turned into integers) are reprojected to return an OSGB absolute grid reference. The resulting value is handled as described in the Absolute BNG section.

*Example input Long/Lat: -1.54,55.5*


---
## BNG to GeoJSON  and GeoJSON to BNG functions


### What the functions do

The BNG to GeoJSON and GeoJSON to BNG functions work together to ensure the record's Geometry and BNG centre point values remain synchronised.

The BNG to GeoJSON function takes a 12 figure alphanumeric grid reference saved as the NGR value and populates the geometry node with a point at the grid reference.  If there are other geometries present then they are kept but a point is added at the BNG position. This point is updated when the BNG value is.

The GeoJSON to BNG function takes whatever geometry/ies has been added to the geometry node, calculates the centre point of the geometry/ies and populates the NGR value with the centre point value as an alphanumeric grid reference.


### Bulk loading data

When carrying out a bulk load of data, these functions need to be unattached to the resource model so that the data being added is not overwritten.  There may be cases where the bulk load should use these functions but you must be aware of the performance hit on loading times.

# Limitations

The datatype and functions should work for everything in the OS National Grid except for off the north coast of mainland Scotland as it does not account for 7 figure northings.

The BNG and the GEOJSON nodes ***must*** be in the same tile OR in tiles that share the same parent tile. It is very difficult to find a way of determining the correct parent tile outside this configuration. The models at Historic England using this function were designed to meet these limitations.