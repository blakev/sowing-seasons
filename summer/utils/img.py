import os
import uuid

from PIL import Image

def process_banner_file(f, media_path=None, by_id='', max_height=240):
    if not media_path:
        new_folder = r'/var/temp'

    else:
        new_folder = os.path.join(media_path, str(by_id))

    short_name = uuid.uuid4().hex[:8]

    # orig_extension = f.get('filename', 'Unknown.jpg').split('.')[-1]

    new_name = 'upload_%s.jpg' % (short_name)

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

    new_width = 1080
    new_height = int((new_width / float(width)) * height)

    img = img.resize((new_width, new_height), Image.ANTIALIAS)

    width, height = img.size

    img = img.crop((0, 0, width, int(new_height * 0.25)))

    img.save(new_location, quality=85, optimize=True)

    return os.path.join(str(by_id), new_name)