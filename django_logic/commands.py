import logging

from django_logic.state import State
from django_logic.exceptions import TransitionNotAllowed


class BaseCommand(object):
    """
    Implements pattern Command
    """
    def __init__(self, commands=None, transition=None):
        self._commands = commands or []
        self._transition = transition

    @property
    def commands(self):
        return self._commands

    def execute(self, *args, **kwargs):
        raise NotImplementedError


class Conditions(BaseCommand):
    def execute(self, state: State, raise_exception=False, **kwargs):
        """
        It checks every condition for the provided instance by executing every command
        :param state: State object
        :param raise_exception: whether or not to raise an exception if some permissions fail
        :return: True or False
        :raises: TransitionNotAllowed
        """
        valid = True
        hints = []
        for command in self._commands:
            result = command(state.instance, **kwargs)
            if not result:
                valid = False
                if hasattr(command, 'hint'):
                    hints.append(command.hint)
        if raise_exception and not valid:
            raise TransitionNotAllowed(f"Conditions not met for action '{self._transition.action_name}'", hints=hints)
        return valid


class Permissions(BaseCommand):
    def execute(self, state: State, user: any, raise_exception=False, **kwargs):
        """
        It checks the permissions for the provided user and instance by executing evey command
        If user is None then permissions passed
        :param state: State object
        :param user: any or None
        :param raise_exception: whether or not to raise an exception if some permissions fail
        :return: True or False
        :raises: TransitionNotAllowed
        """
        if user is None:
            return True

        valid = True
        hints = []
        for command in self._commands:
            result = command(state.instance, user, **kwargs)
            if not result:
                valid = False
                if hasattr(command, 'hint'):
                    hints.append(command.hint)
        if raise_exception and not valid:
            raise TransitionNotAllowed(f"Permissions not met for action '{self._transition.action_name}'", hints=hints)
        return valid


class SideEffects(BaseCommand):
    def execute(self, state: State, **kwargs):
        """Side-effects execution"""
        logging.info(f"{state.instance_key} side effects of '{self._transition.action_name}' started")
        try:
            for command in self._commands:
                command(state.instance, **kwargs)
        except Exception as error:
            logging.info(f"{state.instance_key} side effects of '{self._transition.action_name}' failed with {error}")
            logging.exception(error)
            self._transition.fail_transition(state, error, **kwargs)
        else:
            logging.info(f"{state.instance_key} side-effects of '{self._transition.action_name}' succeeded")
            self._transition.complete_transition(state, **kwargs)


class Callbacks(BaseCommand):
    def execute(self, state: State, **kwargs):
        """
        Callback execution method.
        It runs commands one by one, if any of them raises an exception
        it will stop execution and send a message to logger.
        Please note, it doesn't run failure callbacks in case of exception.
        """
        try:
            for command in self.commands:
                command(state.instance, **kwargs)
        except Exception as error:
            logging.info(f"{state.instance_key} callbacks of '{self._transition.action_name}` failed with {error}")
            logging.exception(error)
