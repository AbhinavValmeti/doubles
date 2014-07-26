from inspect import isbuiltin, getcallargs

from doubles.exceptions import VerifyingDoubleArgumentError, VerifyingDoubleError


def verify_method(target, method_name, class_level=False):
    """
    Verifies that the provided method exists on the target object.

    :param Target target: A ``Target`` object containing the object with the method to double.
    :param str method_name: The name of the method to double.
    :raise: ``VerifyingDoubleError`` if the attribute doesn't exist, if it's not a callable object,
        and in the case where the target is a class, that the attribute isn't an instance method.
    """

    attr = target.attrs.get(method_name)

    if not attr:
        raise VerifyingDoubleError(method_name, target.doubled_obj).no_matching_method()

    if attr.kind == 'data' and not isbuiltin(attr.object):
        raise VerifyingDoubleError(method_name, target.doubled_obj).not_callable()

    if class_level and attr.kind == 'method':
        raise VerifyingDoubleError(method_name, target.doubled_obj).requires_instance()


def verify_arguments(target, method_name, args, kwargs):
    """
    Verifies that the provided arguments match the signature of the provided method.

    :param Target target: A ``Target`` object containing the object with the method to double.
    :param str method_name: The name of the method to double.
    :param tuple args: The positional arguments the method should be called with.
    :param dict kwargs: The keyword arguments the method should be called with.
    :raise: ``VerifyingDoubleError`` if the provided arguments do not match the signature.
    """

    attr = target.attrs[method_name]
    method = attr.object

    if attr.kind in ('class method', 'static method'):
        method = attr.object.__get__(None, attr.defining_class)
    else:
        args = ['self_or_cls'] + list(args)

    try:
        getcallargs(method, *args, **kwargs)
    except TypeError as e:
        raise VerifyingDoubleArgumentError(e.message)
