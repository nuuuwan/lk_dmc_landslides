from lk_dmc import LandslideWarning, ReadMe

if __name__ == "__main__":
    LandslideWarning.list_from_remote(n_limit=None)
    LandslideWarning.aggregate()
    ReadMe().build()
