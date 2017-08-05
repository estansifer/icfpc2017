#!/bin/bash

rm icfp-XXXX.tar.gz
tar cvzf icfp-XXXX.tar.gz install punter PACKAGES README src/*.py
md5sum icfp-XXXX.tar.gz
