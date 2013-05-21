class TooMuchMetaCarac(Exception):
    """Raised when too much datas are avainlable in metadata.
    For exemple when there is more than one author"""

    def __init__(self, name):
        self.name=name

    def __str__(self):
        return "More or less than 1 {0} is specified in the markdow file's\
         metadata. Please correct that before submitting your article."\
          .format(self.name)
