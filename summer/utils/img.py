import os
import uuid

from PIL import Image

def process_banner_file(f, media_path=None, by_id='', max_height=240):
    if not media_path:
        new_folder = r'/var/temp'

    else:
        new_folder = os.path.join(media_path, str(by_id))

    short_name = uuid.uuid4().hex[:8]

    orig_extension = f.get('filename', 'Unknown.jpg').split('.')[-1]

    new_name = 'upload_%s.%s' % (short_name, orig_extension)

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    new_location = os.path.join(new_folder, new_name)

    with open(new_location, 'wb') as out_file:
        out_file.write(f.get('body', None))

    # open the newly uploaded image
    img = Image.open(new_location)

    # prep the image for fading to transparent
    img.putalpha(255)

    # crop to CSS height
    width, height = img.size

    img = img.resize((min(1080, int(width*.5)), max(max_height, int(height*.5))), Image.ANTIALIAS)

    width, height = img.size

    img = img.crop((0, height - max_height, width, height))

    img.save(new_location, quality=35, optimize=True)

    return os.path.join(str(by_id), new_name)