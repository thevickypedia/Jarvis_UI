# noinspection PyUnresolvedReferences
"""Helper functions for the UI.

>>> Helper

"""

import inflect

word_engine = inflect.engine()


def pluralize(count: int, word: str) -> str:
    """Helper for ``time_converter`` function.

    Args:
        count: Number based on which plural form should be determined.
        word: Word for which the plural form should be converted.

    Returns:
        str:
        String formatted time in singular or plural.
    """
    return f"{count} {word_engine.plural(text=word, count=count)}"


def time_converter(second: float) -> str:
    """Modifies seconds to appropriate days/hours/minutes/seconds.

    Args:
        second: Takes number of seconds as argument.

    Returns:
        str:
        Seconds converted to days or hours or minutes or seconds.
    """
    day = round(second // 86400)
    second = round(second % (24 * 3600))
    hour = round(second // 3600)
    second %= 3600
    minute = round(second // 60)
    second %= 60
    pluralize.counter = -1
    if day and hour and minute and second:
        return f"{pluralize(day, 'day')}, {pluralize(hour, 'hour')}, " \
               f"{pluralize(minute, 'minute')}, and {pluralize(second, 'second')}"
    elif day and hour and minute:
        return f"{pluralize(day, 'day')}, {pluralize(hour, 'hour')}, " \
               f"and {pluralize(minute, 'minute')}"
    elif day and hour:
        return f"{pluralize(day, 'day')}, and {pluralize(hour, 'hour')}"
    elif day:
        return pluralize(day, 'day')
    elif hour and minute and second:
        return f"{pluralize(hour, 'hour')}, {pluralize(minute, 'minute')}, and {pluralize(second, 'second')}"
    elif hour and minute:
        return f"{pluralize(hour, 'hour')}, and {pluralize(minute, 'minute')}"
    elif hour:
        return pluralize(hour, 'hour')
    elif minute and second:
        return f"{pluralize(minute, 'minute')}, and {pluralize(second, 'second')}"
    elif minute:
        return pluralize(minute, 'minute')
    else:
        return pluralize(second, 'second')
