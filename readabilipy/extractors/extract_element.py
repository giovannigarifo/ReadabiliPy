from collections import defaultdict
import lxml.html
from ..text_manipulation import normalise_whitespace


def extract_element(html, xpaths):
    """Return the relevant element (title, date or byline) from article HTML
        xpaths should be a list of tuples, each with the xpath and a reliability score
    """

    # Parse the html and extract the contents using all xpaths
    lxml_html = lxml.html.fromstring(html)
    extracted_strings = defaultdict(int)

    # Get all elements specified and concatenate scores
    for extraction_xpath, score in xpaths:
        for found_element in lxml_html.xpath(extraction_xpath):
            if isinstance(found_element, lxml.etree._ElementUnicodeResult):
                element = normalise_whitespace(found_element)
                if element:
                    extracted_strings[element] += score

    # Consider elements where one is just a longer version of another to be the same and concatenate scores
    delete_these = []
    for element in extracted_strings:
        for element2 in extracted_strings:
            if element in element2 and element != element2:  # if an element is a shorter version of a longer one
                extracted_strings[element] += extracted_strings[element2]  # combine scores
                delete_these.append(element2)  # then assign the larger element for deletion
    for del_str in delete_these:
        if del_str in extracted_strings:
            del extracted_strings[del_str]

    # Return highest scoring element
    if not extracted_strings:
        return None
    return max(extracted_strings, key=extracted_strings.get)
