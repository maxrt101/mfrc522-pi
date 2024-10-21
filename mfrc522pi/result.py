#
from typing import TypeVar, Generic
from mfrc522pi.status import Status

T = TypeVar('T')


class Result(Generic[T]):
    def __init__(self, status: Status, value: T = None):
        self.status = status
        self.value = value

    def ok(self) -> bool:
        return self.status == Status.OK

    def get_err_name(self) -> str:
        return self.status.name

    def get(self) -> T:
        return self.value

    def __getattribute__(self, name: str):
        if name in self.__dict__:
            return self.__dict[name]
        return self.value.__getattribute__(name)
