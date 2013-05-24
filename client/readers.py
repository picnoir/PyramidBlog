# -*- coding: utf-8 -*-
import codecs

try:
    import markdown
except ImportError:
    Markdown = False


class MarkdownReader:
    """Markdown parser"""

    
    def read(self, filePath):
        """Return metadatas and content of a markdown file"""

        with codecs.open(filePath, 'r', 'utf-8') as fileToRead:
            mdContent= fileToRead.read()
        md = markdown.Markdown(extensions = ['meta','codehilite'])
        htmlContent=md.convert(mdContent)
        return htmlContent,md.Meta
