#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

try:
    from PIL import Image, ImageFilter, ImageDraw
except ImportError:
    import Image, ImageFilter, ImageDraw

import StringIO

def dropShadow(image, offset=(5,5), background=0xffffff, shadow=0x444444,
                border=8, iterations=3):
  """
  Add a gaussian blur drop shadow to an image.

  In:
    - ``image`` -- The image to overlay on top of the shadow.
    - ``offset`` -- Offset of the shadow from the image as an (x,y) tuple.  Can be
      positive or negative.
    - ``background`` -- Background colour behind the image.
    - ``shadow`` -- Shadow colour (darkness).
    - ``border`` -- Width of the border around the image.  This must be wide
      enough to account for the blurring of the shadow.
    - ``iterations`` -- Number of times to apply the filter.  More iterations
      produce a more blurred shadow, but increase processing time.

  The author of this function is Kevin Schluff:
    http://code.activestate.com/recipes/474116/
  """
  # Create the backdrop image -- a box in the background colour with a
  # shadow on it.
  totalWidth = image.size[0] + abs(offset[0]) + 2*border
  totalHeight = image.size[1] + abs(offset[1]) + 2*border
  back = Image.new(image.mode, (totalWidth, totalHeight), background)

  # Place the shadow, taking into account the offset from the image
  shadowLeft = border + max(offset[0], 0)
  shadowTop = border + max(offset[1], 0)
  back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], shadowTop + image.size[1]])

  # Apply the filter to blur the edges of the shadow.  Since a small kernel
  # is used, the filter must be applied repeatedly to get a decent blur.
  n = 0
  while n < iterations:
      back = back.filter(ImageFilter.BLUR)
      n += 1

  # Paste the input image onto the shadow backdrop
  imageLeft = border - min(offset[0], 0)
  imageTop = border - min(offset[1], 0)
  back.paste(image, (imageLeft, imageTop))

  return back


def outline(image, border=5, color=0x000000):
    (w, h) = image.size

    back = Image.new(image.mode, (w+border*2, h+border*2), 0xffffff)
    back.paste(image, (border, border))

    draw = ImageDraw.Draw(back)
    draw.rectangle((0, 0, w+border*2-1, h+border*2-1), outline=color)
    #w+border*2, h+border*2))

    return back


def thumbnail(image):
  thumb = Image.open(StringIO.StringIO(image))
  format = thumb.format

  if thumb.mode == 'P':
      thumb.thumbnail((200,200))
  else:
      thumb.thumbnail((200,200), Image.ANTIALIAS)
      thumb = dropShadow(outline(thumb, border=8, color=0x666666), shadow=0x666666)

  i = StringIO.StringIO()
  thumb.save(i, format)
  return i.getvalue()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
  import sys

  image = Image.open(sys.argv[1])
  image.thumbnail( (200,200), Image.ANTIALIAS)

  dropShadow(outline(image, border=8, color=0x666666), shadow=0x666666).show()
  #dropShadow(image, background=0xeeeeee, shadow=0x444444, offset=(0,5)).show()
