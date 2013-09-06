"""
Decorators to be used in Registrationshop.

:Authors:
    Berend Klein Haneveld
"""

# Singleton decorator


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


# Override decorator

def overrides(interface_class):
    """
    Use this to override a method explicitely. It will check for the existance
    of an attribute or function with the same name in the superclass. Method
    foot print is not checked (yet). But at least it will fail when typos are
    made or when refactoring goes wrong.

    Example of usage:

    class A:
        def someFunction(self):
            print "function of A"

    class B(A):
        @overrides(A)
        def someFunction(self):
            print "function of B"

    """
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
