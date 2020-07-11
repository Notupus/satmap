# satmap

It makes map overlays for satellites ¯\\\_(ツ)\_/¯
 
## Requirements

```
pip3 install -r requirements.txt
```

## Usage

TLE's are automatically downloaded and updated by deafult.

To use edit the ground station location in `satmap/config.py:20` and then run something like, the time should be **before** the pass:

```
python3 main.py -s "NOAA 18" -t "time" map.png
```

## Credits

[APTDecoder.jl](https://github.com/Alexander-Barth/APTDecoder.jl)

## License

See `LICENSE`.
