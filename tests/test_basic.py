import unittest
from pathlib import Path
from sammvir.run import file_exists


this_file = Path(__file__).parent.resolve()


def test_addition():
    my_sum = 1+1
    assert (my_sum == 2)


def test_file_exists():
    # Real file
    assert file_exists(this_file, ignore=False) == True
    assert file_exists(this_file, ignore=True) == True
    # Fake file does not exist
    # unittest.TestCase.assertRaises(
    #     SystemExit, file_exists(Path("fakefile.foo"), ignore=False))
    assert file_exists(Path("fakefile.foo"), ignore=True) == False


if __name__ == '__main__':
    unittest.main()
