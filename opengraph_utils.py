import metadata_parser


def get_title_description_image(url):
    parsed_page = metadata_parser.MetadataParser(url=url)
    title = ""
    description = ""
    image = ""
    if parsed_page.metadata.get("og"):
        title = parsed_page.metadata["og"].get("title", "")
        description = parsed_page.metadata["og"].get("description", "")
        image = parsed_page.metadata["og"].get("image", "")
        if type(image) == list:
            # see if there's a og:image:width and if so, find the smallest one
            # and then get the image with the same index.
            # otherwise just get the last image in the list
            image = image[-1]
            if parsed_page.metadata["og"].get("image:width"):
                all_widths = list(map(int, parsed_page.metadata["og"]["image:width"]))
                smallest_width = min(all_widths)
                smallest_index = all_widths.index(smallest_width)
                image = parsed_page.metadata["og"]["image"][smallest_index]
    return {"title": title, "description": description, "image": image}
