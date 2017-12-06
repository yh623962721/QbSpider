class static(object):

    def __init__(self,**kwargs):

        print kwargs.get("a","+"*66)

        print "*"*66


    @classmethod
    def from_settings(cls):

        return cls(a = "-"*66)


if __name__ == "__main__":

    print static()