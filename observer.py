

from abc import ABC, abstractmethod


class IObserver(ABC):

    @abstractmethod
    def update(self):
        pass


class IObservable(ABC):

    @abstractmethod
    def attach(self, observer: IObserver):
        pass

    @abstractmethod
    def detach(self, observer: IObserver):
        pass

    @abstractmethod
    def notify(self):
        pass