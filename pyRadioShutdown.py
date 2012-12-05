#!/usr/bin/env python

"""
License:

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""

"""
This plug-in tries to demonstrate how to use python and the gimpfu python module
to write plug-ins for TheGIMP version 2.3.4 and beyond (http://www.gimp.org/).  

Modules

The first part of this plug-in tells python which modules to use.
According to the python tutorial, written by Guido van Rossum and quoted from 
http://docs.python.org/tut/node8.html :
"Python has a way to put definitions in a file and use them in a script [....]
Such a file is called a module; definitions from a module can be imported into other
modules or into the main module (the collection of variables that you have access to 
in a script executed at the top level and in calculator mode)."

There is a list of modules available to python at http://docs.python.org/modindex.html
and the gimpfu module is available from a gimp built with python enabled.

"""


from gimpfu import *
import string
import os

"""

Modules

The first part of this plug-in tells python which modules to use.
According to the python tutorial, written by Guido van Rossum and quoted from 
http://docs.python.org/tut/node8.html :
"Python has a way to put definitions in a file and use them in a script [....]
Such a file is called a module; definitions from a module can be imported into other
modules or into the main module (the collection of variables that you have access to 
in a script executed at the top level and in calculator mode)."

There is a list of modules available to python at http://docs.python.org/modindex.html
and the gimpfu module is available from a gimp built with python enabled.

"""


"""
I.  Functions or Subroutines

Once you start to author your own plug-ins, you will probably find yourself writing some of the
same code chunks over and over again.  Instead of doing this, it is easier to write a separate
self-contained set of instructions that given the same values each time will perform the same 
computational activities and send the results back to the main loop.  The Python Documentation 
calls these sets of instructions "functions";  others call them "subroutines". They are explained
better in the python tutorial here: 
http://docs.python.org/tut/node6.html#SECTION006600000000000000000

This script tries to demonstrate how they work and includes some that have been useful for
scripting TheGIMP with.
"""

def strip(name):
    resource_name = []
    rmspace = string.maketrans(" ","_")
    stripped_name = string.translate(name, rmspace,'()#,?')
    return stripped_name

"""
A. Subroutine that makes names safe for computers

def strip(name):
    resource_name = []
    rmspace = string.maketrans(" ","_")
    stripped_name = string.translate(name, rmspace,'()#,?')
    return stripped_name


The strip subroutine allows you to not worry about what sort of name the user picks and whether
or not it will work with other applications and operating systems.  Certain characters and spaces in
the names of files can be a problem that is simply better when avoided.  It takes a name and returns
an application and operating system safe name.

The python string module is being used by this subroutine or function.

"""

def make_image_new(image_width, image_height, fill_type, image_name, layer_name):
    image = pdb.gimp_image_new(image_width, image_height, RGB)
    drawable = pdb.gimp_layer_new(image, image_width, image_height, RGBA_IMAGE, layer_name, 100, 0)
    image.add_layer(drawable, 0)

    fill = fill_type
    pdb.gimp_edit_fill(drawable, fill)
    pdb.gimp_image_set_filename(image, image_name)
    return image, drawable

"""
B. Make a new GIMP Image subroutine


Making a new image is not a one step process with GIMP.  The idea of an image is more complex than 
a user can see.  An image is a container that holds all sorts of information.  GIMP scripts need
to handle an image as if it is a container and the process of creating a new image needs to put the
initial elements of the container together correctly.

make_image_new needs to know the new image size, what to fill it with and layer_name.  fill_type can 
confusing since it
looks like a string, but gimp has been coded to see it as an integer (this fact seems to elude me 
several times).  fill_type options are: 
FOREGROUND_FILL or 0, BACKGROUND_FILL or 1, WHITE_FILL or 2, TRANSPARENT_FILL or 3, PATTERN_FILL or 4

Even though using the hardcoded strings (or enums) can be confusing when you think they are strings,
they still seem to make more readible scripts.

The gimp python module is being used in this function or subroutine.
"""


def demo_format_indexed(image, fill_type):
    # from the Indexed Color Conversion Defaults
    dither_type, alpha_dither, remove_unused, palette = NO_DITHER, MAKE_PALETTE, False, True, ''
    if (fill_type == TRANSPARENT_FILL):num_cols = 255
    else:
        num_cols = 256
        layer = pdb.gimp_image_flatten(image)
    pdb.gimp_image_convert_indexed(image, dither_type, palette_type, num_cols, alpha_dither, remove_unused, palette)
    return image

"""


"""

def demo_save_gif(image, drawable, fill_type, filename, raw_filename):
    image = demo_format_indexed(image, fill_type)
    
    # from the Save as GIF Defaults
    interlace, loop, default_delay, default_dispose = False, False, False, 0
    pdb.file_gif_save(image, drawable, filename, raw_filename, interlace, loop, default_delay, default_dispose)
    return image, drawable

"""

A subroutine for saving gif.  This subroutine saves gif files the same way the GIMP default gif
dialog does.  It checks for transparency and resets the number of colors in the palette.

The gimp python module is being used in this function or subroutine.

"""
def demo_save_jpeg(image, drawable, new_filename, raw_filename, parasite):
    quality = 85.0
    smoothing, optimize, progressive, comment, subsmp, baseline, restart, dct = 0.0, True, False, parasite, 1, False, 0, 1
    pdb.file_jpeg_save(image, drawable, new_filename, raw_filename, quality, smoothing, optimize, progressive, comment, subsmp, baseline, restart, dct)
    return image, drawable

"""


"""
def demo_save_png(image, drawable, filename, raw_filename, is_indexed):
    if is_indexed:image = demo_format_indexed(image, TRANSPARENT_FILL)
    pdb.file_png_save_defaults(image, drawable, filename, raw_filename)
    return image, drawable

"""


"""
def demo_save_png_comment(image, drawable, filename, raw_filename, is_indexed, parasite):
    compression = 9
    if is_indexed:image = demo_format_indexed(image, TRANSPARENT_FILL)
    pdb.gimp_image_parasite_attach(image, parasite)
    # from the PNG Save Defaults
    interlace, compression, bkgd, gama, offs, phys, time, comment, svtrans = False, False, False, False, True, True, False
    pdb.file_png_save2(image, drawable, filename, raw_filename, interlace, compression, bkgd, gama, offs, phys, time, comment, svtrans) 
    return image, drawable

"""


"""

def image_format_save_simple(image, drawable, raw_filename, width, height, image_type, image_comment, fill_type, save_location):

    image_width = int(width)
    image_height = int(height)
    filename = os.path.join(save_location, raw_filename)

    pdb.gimp_image_set_filename(image, raw_filename)

    if (image_type == 'xcf'):
        if image_comment:
            pdb.gimp_image_parasite_attach(image, image_comment)
        pdb.gimp_xcf_save(1, image, drawable, filename, raw_filename)
    if (image_type == 'png'):
        is_indexed = False
        if not image_comment:
            demo_save_png(image, drawable, filename, raw_filename, is_indexed)
        else:
            demo_save_png_comment(image, drawable, filename, raw_filename, is_indexed, image_comment)
    if (image_type == 'gif'):
        demo_save_gif(image, drawable, fill_type, filename, raw_filename)
    return image, drawable

"""


The image_format_name_save subroutine takes the name, width, height, image_type, fill_type, 
save_location and makes some simple conversions to that information. It converts floats 
(example, 233.0) into integers (same example converted will be 233), fixes the user entered 
string for the name (by calling the subroutine that does this), builds the file name and where 
it will be saved to.  Then it uses the make_new_image subroutine to create the image.  Then it
saves the newly created image in the requested format and with a reasonable name.

The operating system (os) module is being used in this function or subroutine.

"""
    
def demo_new_image_save(name, width, height, image_type, image_comment, fill_type, save_location):
    layer_name = name
    image_name = strip(name)
    raw_filename = image_name + '.' + image_type
    image, drawable = make_image_new(width, height, fill_type, image_name, layer_name)
    display = pdb.gimp_display_new(image)        
    image, drawable = image_format_save_simple(image, drawable, raw_filename, width, height, image_type, fill_type, save_location)

"""

Simple stuff, this is the part of the script that accepts the information from the dialog and
passes it along to the image_format_name_save routine that passes the image back.
"""
    

register(
	"python_fu_demo_new_image_save",
	"A demonstration of how to make, display and save a new image with gimp python.",
	"This demonstration makes a new image of the requested size and fills it with requested color or pattern from the toolbox or with standard gimp fill options.  Then saves the image in the new location with the requested name.",
	"Carol Spears",
	"Carol Spears and Others and General Public License",
	"2005",
	"<Toolbox>/Xtns/Languages/Python-Fu/Demo/New Image",
	"",
	[
        (PF_STRING, "name",  "Prefix of the saved image:", "demo"),
        (PF_SPINNER, "width", "Width of the new image:", 377, (1,500,1)),
        (PF_SPINNER, "height", "Height of the new image:", 233, (1,500,1)),
	(PF_RADIO, "image_type", "Image type:", "png", (("xcf", "xcf"), ("png", "png"), ("gif", "gif"))),
        (PF_STRING, "image_comment",  "Image comments can be stored in xcf, png and jpeg files.", "This image was made as a simple PyGIMP demonstration."),
	(PF_RADIO, "fill_type", "Fill with:", TRANSPARENT_FILL, (("Foreground", FOREGROUND_FILL), ("Background", BACKGROUND_FILL), ("White", WHITE_FILL), ("Transparency", TRANSPARENT_FILL), ("Pattern", PATTERN_FILL))),
        (PF_FILE, "save_location", "Save to location:", "")
	],
	[],
	demo_new_image_save)

"""
The register area of a gimp plug-in is essentially a big subroutine or function that you write.


name
blurb
help
author
copyright
date
menupath
imagetypes
params
results
function



"""

def new_layer_add(image, drawable, fill_type, layer_name):
    new_layer = pdb.gimp_layer_new(image, image.width, image.height, RGBA_IMAGE, layer_name, 100.0, NORMAL_MODE)
    image.add_layer(new_layer, 0)
    pdb.gimp_drawable_fill(new_layer, fill_type)
    return image, new_layer

"""


"""

def demo_new_layer(image, drawable, fill_type):
    layer_name = 'a new layer'
    image, new_layer = new_layer_add(image, drawable, fill_type, layer_name)


register(
	"python_fu_demo_new_layer",
	"A demonstration of how to add a new layer to an existing image.",
	"This demonstration, while useless on its own, shows how to add a new layer in a gimp-python script.",
	"Carol Spears",
	"Carol Spears and Others and General Public License",
	"2005",
	"<Image>/Python-Fu/Demo/Add Layer",
	"",
	[
	(PF_RADIO, "fill_type", "Fill with:", TRANSPARENT_FILL, (("Foreground", FOREGROUND_FILL), ("Background", BACKGROUND_FILL), ("White", WHITE_FILL), ("Transparency", TRANSPARENT_FILL), ("Pattern", PATTERN_FILL)))
	],
	[],
	demo_new_layer)

def layers_separate(image, save, display_layers, ext, use_comment, destination_url):

    for layer in image.layers:

        layername = pdb.gimp_drawable_get_name(layer)
        dest_image = pdb.gimp_image_new(image.width, image.height, 0)
        layer_copy = pdb.gimp_layer_new_from_drawable(layer, dest_image)
        pdb.gimp_image_add_layer(dest_image, layer_copy, 0)

        if save:
            image_name = pdb.gimp_image_get_name(image)
            layer_imagename = image_name + '-' + layername
            comment =  'originally layer number ' + str(int(layer)) + ' from ' + image_name
            image_format_save_simple(dest_image, layer_copy, layer_imagename, image.width, image.height, ext, TRANSPARENT_FILL, save_location)
            if display_layers:
                display = pdb.gimp_display_new(dest_image)
            else:
                gimp.delete(dest_image)


def demo_layers_separate(image, drawable):

    save, display_layers, destination_url = (False, True, '')
    layers_separate(image, save, destination_url)



register(
	"python_fu_demo_layers_separate",
	"This plug-in will save the layers of an image into separate images.",
	"This plug-in will save the layers of an image into separate images.",
	"Carol Spears",
	"Carol Spears and Others and General Public License",
	"2005",
	"<Image>/Python-Fu/Demo/Layers/Separate",
	"",
	[
	],
	[],
	demo_layers_separate)


def demo_layers_separate_save(image, drawable, destination_url, display_layers):

    save = True
    layers_separate(image, save, display_layers, destination_url)



register(
	"python_fu_demo_layers_separate_save",
	"This plug-in will save the layers of an image into separate images and save them.",
	"This plug-in will save the layers of an image into separate images and save them.",
	"Carol Spears",
	"Carol Spears and Others and General Public License",
	"2005",
	"<Image>/Python-Fu/Demo/Layers/Separate and Save",
	"",
	[
	(PF_RADIO, "ext", "Image type to save layers as:", "png", (("xcf", "xcf"), ("png", "png"), ("gif", "gif"))),
        (PF_FILE, "destination_url", "Save to location:", "/tmp"),
        (PF_BOOL, "display_layers", "Display the images", True)
	],
	[],
	demo_layers_separate_save)


def get_check_size(checksize):
    if (checksize == "SMALL"):  check_size = 4
    if (checksize == "MEDIUM"): check_size = 8
    if (checksize == "LARGE"):  check_size = 16
    return check_size

def get_check_color(check_style):
    if (check_style == "LIGHT"):    bg_color, fg_color = (204,204,204),(255,255,255)
    if (check_style == "MID_TONE"): bg_color, fg_color = (102,102,102),(153,153,153)
    if (check_style == "DARK"):     bg_color, fg_color = (051,051,051),(000,000,000)
    if (check_style == "WHITE"):    bg_color, fg_color = (255,255,255),(255,255,255)
    if (check_style == "GRAY"):     bg_color, fg_color = (127,127,127),(127,127,127)
    if (check_style == "BLACK"):    bg_color, fg_color = (000,000,000),(000,000,000)
    return bg_color, fg_color

def emulate_preference_display_transparency(image, drawable, check_style, check_size, bg_color, fg_color):
    
    pdb.gimp_context_push()
    pdb.gimp_image_undo_group_start(image)
    pdb.gimp_context_set_background(bg_color)
    pdb.gimp_context_set_foreground(fg_color)

    if (check_style == "WHITE") or (check_style == "GRAY") or (check_style == "BLACK"):
        pdb.gimp_drawable_fill(drawable, FOREGROUND_FILL)
    else:
        pdb.plug_in_checkerboard(image, drawable, 0, check_size)

    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_context_pop()
    return image, drawable

def demo_new_image_display_transparency(name, width, height, check_style, checksize, image_type, save_location):

    fill_type = WHITE_FILL
    layer_name = name
    image_name = strip(name)
    raw_filename = image_name + '.' + image_type
    image, drawable = make_image_new(width, height, raw_filename, fill_type)
    check_size = get_check_size(checksize)
    bg_color, fg_color = get_check_color(check_style)
    image, drawable = emulate_preference_display_transparency(image, drawable, check_size, bg_color, fg_color)
    image_format_save_simple(image, drawable, raw_filename, width, height, image_type, fill_type, save_location)
    display = pdb.gimp_display_new(image)


register(
	"python_fu_demo_new_image_display_transparency",
	"A demonstration of how to make a new image and render one of the gimp checked transparency backgrounds the new image with gimp python.",
	"This demonstration renders the different options available via the Preferences to show what the gimp transparency 'looks like'.",
	"Carol Spears",
	"Carol Spears and Others and General Public License",
	"2005",
	"<Toolbox>/Xtns/Languages/Python-Fu/Demo/Transparency Look",
	"",
	[
        (PF_STRING, "name",  "Suffix of the saved image:", "demo"),
        (PF_SPINNER, "width", "Width of the new image:", 377, (1,500,1)),
        (PF_SPINNER, "height", "Height of the new image:", 233, (1,500,1)),
	(PF_RADIO, "check_style", "Check Style:", "MID_TONE", (("Light checks", "LIGHT"), ("Mid-tone checks", "MID_TONE"), ("Dark checks", "DARK"), ("White only", "WHITE"), ("Gray only", "GRAY"), ("Black only", "BLACK"))),
	(PF_RADIO, "checksize", "Check Size:", "MEDIUM", (("Small", "SMALL"), ("Medium", "MEDIUM"), ("Large", "LARGE"))),
	(PF_RADIO, "image_type", "Image type:", "png", (("xcf", "xcf"), ("png", "png"), ("gif", "gif"))),
        (PF_FILE, "save_location", "Save to location:", "")
	],
	[],
	demo_new_image_display_transparency)



def demo_display_transparency(image, drawable, check_style, checksize):

    check_size = get_check_size(checksize)
    bg_color, fg_color = get_check_color(check_style)
    image, drawable = emulate_preference_display_transparency(image, drawable, check_style, checksize)

register(
	"python_fu_demo_display_transparency",
	"A demonstration of how to render the gimp checked transparency background on an image with gimp python.",
	"This demonstration renders the different options available via the Preferences to show what the gimp transparency 'looks like'.",
	"Carol Spears",
	"Carol Spears and Others and General Public License",
	"2005",
	"<Image>/Python-Fu/Demo/Transparency Look",
	"",
	[
	(PF_RADIO, "check_style", "Check Style:", "MID_TONE", (("Light checks", "LIGHT"), ("Mid-tone checks", "MID_TONE"), ("Dark checks", "DARK"), ("White only", "WHITE"), ("Gray only", "GRAY"), ("Black only", "BLACK"))),
	(PF_RADIO, "checksize", "Check Size:", "MEDIUM", (("Small", "SMALL"), ("Medium", "MEDIUM"), ("Large", "LARGE")))
	],
	[],
	demo_display_transparency)


def get_style_name(style_number):
    if (style_number == 0):style_name = "LIGHT"
    if (style_number == 1):style_name = "MID_TONE"
    if (style_number == 2):style_name = "DARK"
    if (style_number == 3):style_name = "WHITE"
    if (style_number == 4):style_name = "GRAY"
    if (style_number == 5):style_name = "BLACK"
    return style_name

def demo_new_image_display_transparency_all(name, width, height, checksize, make_layers):

    fill_type = WHITE_FILL
    check_size = get_check_size(checksize)
    for style_number in range(0,6):
        style_name = get_style_name(style_number)
        bg_color, fg_color = get_check_color(style_name)
        if make_layers:
            if (style_number == 0):
                image, drawable = make_image_new(width, height, 'transparency-layers-demo', fill_type, style_name)
                image, drawable = emulate_preference_display_transparency(image, drawable, style_name, check_size, bg_color, fg_color)
                display = pdb.gimp_display_new(image)
            else:
                image, new_layer = new_layer_add(image, drawable, fill_type, style_name)
                image, new_layer = emulate_preference_display_transparency(image, new_layer, style_name, check_size, bg_color, fg_color)
                pdb.gimp_drawable_set_visible(new_layer, False)
        else:
            image_name = strip(name)
            image, drawable = make_image_new(width, height, image_name, fill_type, style_name)
            pdb.gimp_image_set_filename(image, style_name)
            image, drawable = emulate_preference_display_transparency(image, drawable, style_name, check_size, bg_color, fg_color)
            pdb.gimp_image_set_filename(image, style_name)
            display = pdb.gimp_display_new(image)


register(
	"python_fu_demo_new_image_display_transparency_all",
	"A demonstration of how to make a new image and render one of the gimp checked transparency backgrounds the new image with gimp python.",
	"This demonstration renders the different options available via the Preferences to show what the gimp transparency 'looks like'.",
	"Carol Spears",
	"Carol Spears and Others and General Public License",
	"2005",
	"<Toolbox>/Xtns/Languages/Python-Fu/Demo/Transparency Style",
	"",
	[
        (PF_STRING, "name",  "Suffix of the saved image:", "demo"),
        (PF_SPINNER, "width", "Width of the new image:", 377, (1,500,1)),
        (PF_SPINNER, "height", "Height of the new image:", 233, (1,500,1)),
	(PF_RADIO, "checksize", "Check Size:", "MEDIUM", (("Small", "SMALL"), ("Medium", "MEDIUM"), ("Large", "LARGE"))),
        (PF_BOOL, "make_layers", "Make Layered Image", True)
	],
	[],
	demo_new_image_display_transparency_all)



main()
