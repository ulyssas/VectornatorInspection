# Vectornator Inspection

![](example.png)

## About
Vectornator Inspection aims to convert .vectornator / .curve files into SVG.

## Announcement
This project has been turned into Inkscape extension! The link is here: [extension-curve]

[extension-curve]: https://gitlab.com/WimPum/extension-curve

## TODO
* Complete Linearity Curve 5.x format(yes, Vectornator 4.x and Curve 5.x files are technically different format!)
* My plan is to add support for fileFormatVersion 44(5.18.0~5.18.4) first, then add Vectornator 4.x file format support, and later, earlier Linearity Curve(5.1.2).
* Gaussian Blur.
* Text support.
* Corner radius, shapes and line start/end style.
* Support for other units than `Pixels`. Curve supports other units as well, which will be added later.
* Other stuffs(brush-type stroke, multiple artboards, masks). I'm not sure how to implement them.

Any amount of contribution is welcome!

## Motivation
Popular Illustrator alternative app Vectornator has changed its name to Linearity Curve.

Vectornator offered all of its features for free. However, with Linearity Curve, most of them have been paywalled, **INCLUDING SVG/PDF EXPORT.**

This means Curve documents cannot be exported without sacrificing quality.

All of my works on Curve can no longer be exported with layer structures intact. It is such a bummer.

So in this project, I want to make a converter for Vectornator / Curve files, so that all of my projects are safe.

And once this is working, I might make an Inkscape extension that can import such files.
