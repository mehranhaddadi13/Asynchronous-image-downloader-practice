"""By this personal exercise, We use asynchronous programming and go to the
'Special Offers' section of 'technolife.ir' online store and download the images of the products
with their names."""

import asyncio
import requests
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
import os
import time

home_url = "http://technolife.ir"
# A valid user-agent should be provided otherwise our request will be failed
h = {"user-agent": ""}
tasks = []  # The list of the asynchronous tasks
path = "~/Personal projects/Image_Downloader/Images/"    # Saving path


async def downloader(name: str, img_url: str):
    """
    Downloads images from given url and saves them to the path with given name.
    :param str name: Product's name
    :param str img_url: Product's image url
    """
    # Replace / in products' name with , since it is mistaken as Unix's addressing syntax and raises
    # exception
    if "/" in name:
        name = name.replace("/", ",")
    # Add file extension
    name += ".png"
    # Make a connection to the url and download the image then save it as a file with its related
    # name. All are done via asynchronous libraries, aiohttp and aiofiles
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as resp:
            f = await aiofiles.open(path + name, 'wb')
            await f.write(await resp.read())
            await f.close()


def get_html(url: str) -> str:
    """
    Make a connection to the url and return its HTML content. Since we make just one connection
    at a time, there is no need to do it via aiohttp.
    :param str url: Desired url
    :return: HTML context of url
    :rtype: str
    """
    res = requests.get(url, headers=h)
    if res.status_code == 200:   # Return HTML context of url if our request is successful
        return res.text


def parse_html(url: str, t_type: str) -> str:
    """
    HTML parser by which we obtain desired data.
    Since we use BeautifulSoup, which is a synchronous library, there is no point in using
    aiohttp library here.
    :param str url: The url we want to get data from
    :param str t_type: Our task type, either 'special' or 'image'
    :return: If the t_type is 'special', it returns url
    :rtype: str
    """
    content = get_html(url)
    # Create a dom to search through HTML tags with it
    dom = BeautifulSoup(content, 'html.parser')
    if t_type == "special":     # Our first task to find out Special Offers url
        # Through my personal inspection, I understood that Special Offers url can be obtained in
        # this way:
        for link in dom.find_all('a'):  # Searching in 'a' tags in dom object
            ref_url = link.get("href")
            if ref_url.endswith("special/special"):
                return home_url + ref_url
    elif t_type == "image":  # Our second task to make asynchronous tasks to download images
        for img in dom.find_all('img'):
            if "product" in img.get("src"):
                name = img.get("title")
                img_url = img.get("src")
                tasks.append(downloader(name, img_url))  # Append coroutines in tasks list


async def main():
    # First, we obtain the url of Special Offers page from website's homepage by specifying our 
    # task's type to the parse_html coroutine.
    special_url = parse_html(home_url, "special")
    # Next, we get the image address and name of products and create a task for each one.
    parse_html(special_url, "image")
    # Then, make sure that saving path exists
    if not os.path.exists(path):
        os.mkdir(path)
    # Finally, we run tasks!
    await asyncio.gather(*tasks)


start = time.perf_counter()
asyncio.run(main())
print(time.perf_counter() - start)
