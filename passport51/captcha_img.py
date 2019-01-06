import re
from PIL import Image

import requests
from scrapy.selector import Selector


def get_captcha_img():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Referer': 'http://passport.51.com/login/proxy'
    }
    url = 'http://passport.51.com/authcode/slidecode/?from=passport'
    r = requests.get(url, headers=headers)
    img_url_r = re.search('url\("(//passport.51.com/yzm/pic_temp/code/\d+/big/.*?.png)"\)', r.text)
    img_url = 'https:' + img_url_r.group(1)

    headers_img = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Referer': 'http://passport.51.com/'
    }
    r_img = requests.get(img_url, headers=headers_img)
    with open('./img/captcha.png', 'wb') as f:
        f.write(r_img.content)

    all_position = get_position(r.text)
    restore_img(all_position, img_width=13, img_hight=25, line=4)


def get_position(html):
    # get position of img
    all_position = []
    hxs = Selector(text=html)
    position_r = hxs.xpath('//div[@id="Verification"]//div[@class="gt_cut_fullbg_slice"]/@style').extract()
    for data in position_r:
        p = re.findall('\w+-\w+:(.*?)px (.*?)px;', data)
        if p:
            position = tuple(int(t) for t in p[0])
            all_position.append(position)
    return all_position


def restore_img(locations, img_width, img_hight, line):
    # restore img
    img = Image.open('./img/captcha.png')
    new_img = Image.new('RGB', (260, 100))

    img_list = []
    for location in locations:
        img_list.append(
            img.crop((abs(location[0]), abs(location[1]), abs(location[0]) + img_width, abs(location[1]) + img_hight)))

    for i in range(line):
        x_offset = 0
        for im in img_list[20 * i: 20 * (i + 1)]:
            new_img.paste(im, (x_offset, 25 * i))
            x_offset += img_width
    new_img.save('./img/new_captcha.png')


if __name__ == '__main__':
    get_captcha_img()
