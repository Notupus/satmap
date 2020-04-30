# `pmap`
***

A python tool for projection and mapping of images from polar (and soon geosynchronous) orbiting satellites.

**NOTE: THIS IS STILL INCREDIBABLY BUGGY AND PROBABLY WONT WORK PROPERLY YET**

## Features

`pmap` is a tool for general purpose for manipulation of satellite images, being able to perform common operations to add useful information to images.

Currently `pmap` can perform the following tasks:

 - (badly) Project images to Mercator earth projections
 - Create map underlays

**DEMO IMAGES HERE**
 
## Install

Assuming everything wants to work, all dependencies can be installed via pip.

```
pip3 install -r requirements.txt
```

However I have had problems when installing `cartopy` from pip, this can be resolved by installing it directly from source.

```
pip3 install Cython
git clone https://github.com/SciTools/Cartopy && cd Cartopy
sudo python3 setup.py
```

## Use

Something like:

```
time python3 main.py -t "2020-02-29 17:09:32" -i gqrx_20200229_170932_137103008-a.png -o N19-2020-02-29-mercator.png
```

# Satellite params

 - NOAA APT
   - 2 lines per second
   - 2900km swath
 - Meteor-M LRPT
   - 6.52 lines per second
   - 2800km swath (requires dewarping)

## Resources

[https://visibleearth.nasa.gov/collection/1484/blue-marble](https://visibleearth.nasa.gov/collection/1484/blue-marble) has a lot of good images for underlays.

## Credits

Thank you to [APTDecoder.jl](https://github.com/Alexander-Barth/APTDecoder.jl) for providing the maths required for transformation between viewing angle and geographical coordinates on polar satellites.

## License

See `LICENSE`.