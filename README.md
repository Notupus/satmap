# pmap

A python tool for projection and mapping of images from polar (and soon geosynchronous) orbiting satellites. It uses `OpenCV` allowing for high speed image manipulation.

**NOTE: THIS IS STILL INCREDIBLY BUGGY AND PROBABLY WONT WORK PROPERLY YET**

## Features

`pmap` is a tool for general purpose for manipulation of satellite images, being able to perform common operations to add useful information to images. 

Currently `pmap` can perform the following tasks:

 - Project images to Mercator earth projections
 - Create map underlays

**DEMO IMAGES HERE (SOON)**
 
## Requirements

All dependencies can be installed via pip.

```
pip3 install -r requirements.txt
```

## Use

To turn a image recorded at `2020-02-29 17:09:32` into a mappable version
```
python3 main.py -t "2020-02-29 17:09:32" -i gqrx_20200229_170932_137103008-1.png -o N19-2020-02-29-mercator.png
```

Or create an underlay for the same image:

```
python3 main.py -m mercator_map.jpg -t "2020-02-29 17:09:32" -S 909x1562 -o N19-2020-02-29-underlay.png
```

# Satellite settings

 - NOAA APT
   - 2 lines per second
   - 2900km swath
 - Meteor-M LRPT
   - 6.52 lines per second
   - 2800km swath (requires dewarping first)

## Resources

[https://visibleearth.nasa.gov/collection/1484/blue-marble](https://visibleearth.nasa.gov/collection/1484/blue-marble) has a lot of good images for underlays.

## Credits

Thank you to [APTDecoder.jl](https://github.com/Alexander-Barth/APTDecoder.jl) for providing the maths required for transformation between viewing angle and geographical coordinates on polar satellites.

## License

See `LICENSE`.