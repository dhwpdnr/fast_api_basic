import pytest


def test_equal_or_not():
    assert 1 == 1
    assert 1 != 2


def test_is_instance():
    assert isinstance(1, int)
    assert isinstance("hello", str)
    assert not isinstance(1, str)
    assert not isinstance("10", int)


def test_boolean():
    validated = True
    assert validated is True
    assert ("hello" == "world") is False


def test_type():
    assert type(1) == int
    assert type("hello") == str
    assert type(1.0) == float
    assert type([1, 2, 3]) == list
    assert type((1, 2, 3)) == tuple
    assert type({"a": 1, "b": 2}) == dict
    assert type({1, 2, 3}) == set
    assert type("hello" is str)


def test_greater_or_less():
    assert 1 > 0
    assert 1 >= 1
    assert 1 < 2
    assert 1 <= 1


def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]
    assert 1 in num_list
    assert 6 not in num_list
    assert any(any_list) is False
    assert all(any_list) is False
    assert any(num_list) is True
    assert all(num_list) is True


class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.year = years


@pytest.fixture
def default_employee():
    return Student("John", "Doe", "Computer Science", 4)


def test_person_initialization(default_employee):
    assert default_employee.first_name == "John"
    assert default_employee.last_name == "Doe"
    assert default_employee.major == "Computer Science"
    assert default_employee.year == 4
