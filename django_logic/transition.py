from django.core.cache import cache

from django_logic.exceptions import TransitionNotAllowed


class Transition:
    """
    Transition could be defined as a class or as an object and used as an object
    - action name
    - transitions name
    - target
    - it changes the the state of the object from source to target by triggering available action via transition name
    - validation if the action is available throughout permissions and conditions
    - run side effects and call backs
    """
    def __init__(self, action_name, target, sources, **kwargs):
        self.action_name = action_name
        self.target = target
        self.sources = sources
        self.side_effects = kwargs.get('side_effects')
        self.callbacks = kwargs.get('callbacks')
        self.failure_handler = kwargs.get('failure_handler')
        self.processing_state = kwargs.get('processing_state')
        self.permissions = kwargs.get('permissions')
        self.conditions = kwargs.get('conditions')
        self.parent_process = None  # initialised by process

    def change_state(self, instance, state_field):
        # TODO: consider adding the process as it also has side effects and callback (or remove them from it)
        # run the conditions and permissions
        # Lock state
        # run side effects
        # change state via transition to the next state
        # run callbacks
        if self._is_locked(instance):
            raise TransitionNotAllowed("State is locked")

        self._lock(instance)
        # self.side_effects.add(success(self))
        try:
            self.side_effects.execute()
        except Exception as ex:
            pass

        self._set_state(instance, state_field, self.target)
        self._unlock(instance)

    def _get_hash(self, instance):
        return "FSM-{}-{}-{}".format(instance._meta.app_label, instance._meta.model_name, instance.pk)

    def _lock(self, instance):
        cache.set(self._get_hash(instance), True)

    def _unlock(self, instance):
        cache.delete(self._get_hash(instance))

    def _is_locked(self, instance):
        return cache.get(self._get_hash(instance)) or False

    def _get_db_state(self, instance, state_field):
        """
        Fetches state directly from db instead of model instance.
        """
        return instance._meta.model.objects.values_list(state_field, flat=True).get(pk=instance.id)

    def _set_state(self, instance, state_field, state):
        """
        Sets intermediate state to instance's field until transition is over.
        """
        # TODO: how would it work if it's used within another transition?
        instance._meta.model.objects.filter(pk=instance.id).update(**{state_field: state})
        instance.refresh_from_db()
